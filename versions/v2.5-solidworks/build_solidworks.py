"""Native SolidWorks 2025 concept CAD. API units: metres; design helpers: mm.

Requires pywin32 and an installed, licensed SolidWorks session. Existing documents
are not closed. Output is preliminary, not a fabrication/structural release.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import pythoncom
import win32com.client
from win32com.client import makepy

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "CAD"
TEMPLATE = Path(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2025\templates")
TYPELIB = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\sldworks.tlb"
lib = pythoncom.LoadTypeLib(TYPELIB)
attr = lib.GetLibAttr()
try:
    swmod = win32com.client.gencache.GetModuleForTypelib(attr[0], attr[1], attr[3], attr[4])
except ImportError:
    makepy.GenerateFromTypeLibSpec(TYPELIB)
    swmod = win32com.client.gencache.GetModuleForTypelib(attr[0], attr[1], attr[3], attr[4])


def wrap(obj, name):
    return getattr(swmod, name)(obj._oleobj_)


sw = wrap(win32com.client.Dispatch("SldWorks.Application"), "ISldWorks")
sw.Visible = True
C = math.cos(math.radians(32))
S = math.sin(math.radians(32))
SH = 80 + 1000 * S
PY = SH - 40 / C
TOE = 150 + 1000 * C
REPORT = []


def point(s, n=0):
    """At distance s along the inclined support-plate TOP; n normal upward."""
    return (150 + s * C + n * S, PY - s * S + n * C)


def new_part():
    obj = sw.NewDocument(str(TEMPLATE / "gb_part.prtdot"), 0, 0, 0)
    if obj is None:
        raise RuntimeError("SolidWorks did not create the part")
    return wrap(obj, "IModelDoc2")


def plane(doc):
    feat = doc.FirstFeature()
    while feat:
        f = wrap(feat, "IFeature")
        if f.GetTypeName2() == "RefPlane":
            return f
        feat = f.GetNextFeature()
    raise RuntimeError("Front reference plane not found")


def extrude(doc, name, profiles, width, start=0, merge=False):
    """Closed XY polygons extruded in positive Z (the transverse direction)."""
    doc.ClearSelection2(True)
    if not plane(doc).Select2(False, 0):
        raise RuntimeError("Reference-plane selection failed")
    sk = wrap(doc.SketchManager, "ISketchManager")
    sk.InsertSketch(True)
    sk.AddToDB = True
    for poly in profiles:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            seg = sk.CreateLine(a[0] / 1000, a[1] / 1000, 0,
                                b[0] / 1000, b[1] / 1000, 0)
            if seg is None:
                raise RuntimeError(f"Sketch line failed: {name}")
    sk.AddToDB = False
    doc.SketchAddConstraints("sgFIXED")
    sk.InsertSketch(True)
    fm = wrap(doc.FeatureManager, "IFeatureManager")
    feat = fm.FeatureExtrusion2(True, False, False, 0, 0, width / 1000, 0,
                               False, False, False, False, 0, 0, False, False,
                               False, False, merge, True, True,
                               3 if start else 0, start / 1000, False)
    if feat is None:
        raise RuntimeError(f"Extrusion failed: {name}")
    wrap(feat, "IFeature").Name = name
    return feat


def rectangle(x1, y1, x2, y2):
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]


def finish(doc, filename, color, expected_bodies=None, transparency=0):
    doc.MaterialPropertyValues = win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8,
        tuple(color) + (0.25, 0.75, 0.3, 0.25, transparency, 0))
    doc.ForceRebuild3(False)
    part = wrap(doc, "IPartDoc")
    bodies = part.GetBodies2(0, False) or []
    bounds, volumes, checks = [], [], []
    for body in bodies:
        b = wrap(body, "IBody2")
        bounds.append(list(b.GetBodyBox()))
        mass = b.GetMassProperties(1000)
        volumes.append(mass[3] if mass else None)
        checks.append(b.Check2())
    if any(checks):
        raise RuntimeError(f"Invalid solid geometry: {filename}: {checks}")
    if not bodies:
        raise RuntimeError(f"No solid bodies: {filename}")
    if expected_bodies is not None and len(bodies) != expected_bodies:
        raise RuntimeError(f"{filename}: expected {expected_bodies} bodies, got {len(bodies)}")
    doc.ShowNamedView2("", 7)
    doc.ViewZoomtofit2()
    ext = wrap(doc.Extension, "IModelDocExtension")
    path = OUT / filename
    result = ext.SaveAs(str(path), 0, 1, None, 0, 0)
    if not result[0] or result[1]:
        raise RuntimeError(f"Save failed: {path}: {result}")
    REPORT.append({"file": filename, "bodies": len(bodies),
                   "body_bounds_m": bounds, "volumes_m3": volumes,
                   "body_check2_codes": checks, "save": list(result)})
    print(filename, "bodies:", len(bodies), "save:", result, flush=True)
    return doc, path


def tube_xy(doc, label, a, b, z):
    """40x40x3 open tube: two side skins and two longitudinal edge walls."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length

    def band(low, high):
        return [(a[0] + low * nx, a[1] + low * ny),
                (b[0] + low * nx, b[1] + low * ny),
                (b[0] + high * nx, b[1] + high * ny),
                (a[0] + high * nx, a[1] + high * ny)]

    extrude(doc, label + "_skin_A", [band(-20, 20)], 3, z, True)
    extrude(doc, label + "_edge_walls", [band(-20, -17), band(17, 20)], 34, z + 3, True)
    extrude(doc, label + "_skin_B", [band(-20, 20)], 3, z + 37, True)


def post(doc, label, x, z, top):
    left, right = x - 20, x + 20

    def band(x1, x2):
        return [(x1, 40), (x2, 40), (x2, top(x2)), (x1, top(x1))]

    extrude(doc, label + "_skin_A", [band(left, right)], 3, z, True)
    extrude(doc, label + "_walls", [band(left, left + 3), band(right - 3, right)], 34, z + 3, True)
    extrude(doc, label + "_skin_B", [band(left, right)], 3, z + 37, True)


def ring(cx, cy, half, rotated=False):
    result = []
    for x, y in [(-half, -half), (half, -half), (half, half), (-half, half)]:
        result.append((cx + (x * C + y * S if rotated else x),
                       cy + (-x * S + y * C if rotated else y)))
    return result


def frame():
    doc = new_part()
    for side, z in [("L", 0), ("R", 460)]:
        tube_xy(doc, side + "_base_870", (50, 20), (920, 20), z)
        tube_xy(doc, side + "_inclined_895", point(5, -24), point(900, -24), z)
        tube_xy(doc, side + "_platform_100", (50, PY - 24), (150, PY - 24), z)
        post(doc, side + "_rear_post", 70, z, lambda x: PY - 44)
        for x in (200, 500, 800):
            post(doc, f"{side}_post_x{x}", x, z,
                 lambda xx: PY - (xx - 150) * S / C - 44 / C)
    for s in (25, 300, 600, 900):
        x, y = point(s, -24)
        extrude(doc, f"Transverse_s{s}_420", [ring(x, y, 20, True), ring(x, y, 17, True)], 420, 40, True)
    for x in (100, 500, 880):
        extrude(doc, f"Base_transverse_x{x}_420", [ring(x, 20, 20), ring(x, 20, 17)], 420, 40, True)
    # Rear cross tie for the 100 mm shoulder platform.
    extrude(doc, "Platform_cross_tie_420", [ring(70, PY - 24, 20), ring(70, PY - 24, 17)], 420, 40, True)
    return finish(doc, "01_Q235B_40x40x3_空腔支架.SLDPRT", (0.25, 0.34, 0.43))


def saddle():
    doc = new_part()
    extrude(doc, "Base_plate_940_to_1004_t6", [rectangle(940, 0, 1004, 6)], 500)
    pad = [point(950, -4), point(1000, -4), point(1000, -10), point(950, -10)]
    extrude(doc, "Inclined_bearing_plate_t6", [pad], 500, 0, True)
    top = lambda x: PY - (x - 150) * S / C - 10 / C
    for i, z in enumerate((20, 247, 474), 1):
        web = [(956, 6), (990, 6), (990, top(990)), (956, top(956))]
        extrude(doc, f"Toe_web_{i}_t6", [web], 6, z, True)
    return finish(doc, "02_Q235B_坡脚低位托座.SLDPRT", (0.32, 0.41, 0.5))


def seats():
    doc = new_part()
    strip = [point(5, -3), point(900, -3), point(900, -4), point(5, -4)]
    for i, z in enumerate((0, 460), 1):
        extrude(doc, f"Rail_seat_{i}_EPDM_t1", [strip], 40, z)
        extrude(doc, f"Platform_seat_{i}_EPDM_t1", [rectangle(50, PY - 4, 150, PY - 3)], 40, z)
    toe = [point(950, -3), point(1000, -3), point(1000, -4), point(950, -4)]
    extrude(doc, "Toe_seat_EPDM_t1", [toe], 500)
    for s in (25, 300, 600, 900):
        # The cross-tie is square in the along-slope / normal plane.
        cross = [point(s - 20, -3), point(s + 20, -3), point(s + 20, -4), point(s - 20, -4)]
        extrude(doc, f"Cross_seat_s{s}_EPDM_t1", [cross], 420, 40)
    return finish(doc, "03_EPDM_隔离垫条_t1.SLDPRT", (0.08, 0.09, 0.1))


def deck():
    doc = new_part()
    profile = [(50, PY), (150, PY), point(1000), point(1000, -3),
               (150, PY - 3 / C), (150, PY - 3), (50, PY - 3)]
    extrude(doc, "304_deck_normal_t3_and_horizontal_platform_t3", [profile], 500)
    return finish(doc, "04_304_连续承托板_t3.SLDPRT", (0.68, 0.73, 0.78), 1)


def soils():
    bed = new_part()
    profile = [(50, PY), (150, PY), point(1000), (TOE, 80), (150, SH), (50, SH)]
    extrude(bed, "Compacted_low_permeability_bed_normal_40", [profile], 500)
    b = finish(bed, "05_压实低渗土床_n40.SLDPRT", (0.50, 0.31, 0.19), 1)
    soil = new_part()
    profile = [(50, SH), (150, SH), (TOE, 80), (TOE, 80 + 120 / C),
               (150, SH + 120 / C), (50, SH + 120 / C)]
    extrude(soil, "Active_sand_layer_normal_120", [profile], 500)
    a = finish(soil, "06_砂或混合土_主动层_n120.SLDPRT", (0.78, 0.60, 0.33), 1, 0.72)
    return b, a


def enclosure():
    tray = new_part()
    extrude(tray, "304_floor_1400x500_t3", [rectangle(-3, -3, 1403, 0)], 506, -3)
    t = finish(tray, "07_304_槽底示意_t3.SLDPRT", (0.6, 0.65, 0.70), 1)
    wall = new_part()
    extrude(wall, "PC_observation_wall_left_t8", [rectangle(0, 0, 1400, 850)], 8, -8)
    extrude(wall, "PC_observation_wall_right_t8", [rectangle(0, 0, 1400, 850)], 8, 500)
    extrude(wall, "PC_rear_end_t8", [rectangle(-8, 0, 0, 850)], 516, -8)
    extrude(wall, "PC_toe_end_t8", [rectangle(1400, 0, 1408, 850)], 516, -8)
    w = finish(wall, "08_PC_观察围壁_t8_未含压框.SLDPRT", (0.67, 0.83, 0.91), transparency=0.94)
    return t, w


def sensors():
    doc = new_part()
    for row, z in enumerate((150, 350)):
        for col, s in enumerate((125, 375, 625, 875)):
            # Bed top is vertically 40/cos above support top; sensor is n=40 above bed.
            x = 150 + s * C + 40 * S
            y = SH - s * S + 40 * C
            shape = [(x + ds * C + dn * S, y - ds * S + dn * C)
                     for ds, dn in [(-55, -3), (55, -3), (55, 3), (-55, 3)]]
            extrude(doc, f"S{row * 4 + col + 1}_110x8x6_SCHEMATIC", [shape], 8, z - 4)
    return finish(doc, "09_FBG_8点包封占位_非成品设计.SLDPRT", (0.90, 0.16, 0.1), 8)


def assembly(filename, components):
    obj = sw.NewDocument(str(TEMPLATE / "gb_assembly.asmdot"), 0, 0, 0)
    doc = wrap(obj, "IModelDoc2")
    assy = wrap(obj, "IAssemblyDoc")
    mathutil = wrap(sw.GetMathUtility(), "IMathUtility")
    identity = mathutil.CreateTransform((1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.))
    names = []
    for partdoc, path in components:
        component = assy.AddComponent5(str(path), 0, "", False, "", 0, 0, 0)
        if component is None:
            raise RuntimeError(f"Could not insert component {path}")
        comp = wrap(component, "IComponent2")
        comp.Transform2 = identity
        if not comp.Select4(False, None, False):
            raise RuntimeError("Could not select inserted component")
        assy.FixComponent()
        doc.ClearSelection2(True)
        names.append(comp.Name2)
    doc.ForceRebuild3(False)
    doc.ClearSelection2(True)
    doc.ViewDisplayShaded()
    doc.ShowNamedView2("", 7)
    doc.ViewZoomtofit2()
    ext = wrap(doc.Extension, "IModelDocExtension")
    native = OUT / filename
    save = ext.SaveAs(str(native), 0, 1, None, 0, 0)
    if not save[0] or save[1]:
        raise RuntimeError(f"Assembly save failed: {save}")
    step = ext.SaveAs(str(native.with_suffix(".STEP")), 0, 1, None, 0, 0)
    if not step[0] or step[1]:
        raise RuntimeError(f"STEP export failed: {step}")
    bmp = native.with_suffix(".bmp")
    if not doc.SaveBMP(str(bmp), 1800, 1200):
        raise RuntimeError("SolidWorks view export failed")
    from PIL import Image
    with Image.open(bmp) as im:
        im.save(native.with_suffix(".png"))
    # BMP is kept as an application-generated original, not an edited source.
    REPORT.append({"file": filename, "components": names, "save": list(save), "step_save": list(step)})
    print(filename, "components:", len(names), "native + STEP + preview saved", flush=True)
    return doc, native


def build():
    if (OUT / "坡体总装_32deg.SLDASM").exists():
        raise RuntimeError("Outputs already exist; preserve them and select a new output folder")
    f, t, pads, d = frame(), saddle(), seats(), deck()
    b, a = soils()
    floor, walls = enclosure()
    nodes = sensors()
    assembly("空腔钢支架_32deg.SLDASM", [f, t])
    assembly("支架及承托板_32deg.SLDASM", [f, t, pads, d])
    assembly("坡体总装_32deg.SLDASM", [f, t, pads, d, b, a, floor, walls, nodes])
    (ROOT / "CAD校验记录.json").write_text(json.dumps({
        "solidworks_revision": sw.RevisionNumber(),
        "status": "concept CAD; not structurally verified; not fabrication release",
        "units": "m in API and saved bound/volume records; mm in helper parameters",
        "coordinates": "SolidWorks X=engineering x; Y=engineering z (up); Z=engineering y",
        "dimensions_mm": {"angle_deg": 32, "bed_length": 1000, "width": 500,
                          "bed_normal": 40, "active_normal": 120, "toe_x": TOE,
                          "deck_shoulder_y": PY, "deck_toe_y": 80 - 40 / C,
                          "highest_soil_y": SH + 120 / C},
        "artifacts": REPORT}, ensure_ascii=False, indent=2), encoding="utf-8")


def probe():
    doc = new_part()
    extrude(doc, "Probe_40x40x3_hollow", [rectangle(0, 0, 40, 40),
                                          rectangle(3, 3, 37, 37)], 100, 20)
    finish(doc, "API_probe.SLDPRT", (0.3, 0.4, 0.6), 1)
    print(json.dumps(REPORT, indent=2), flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    if "--probe" in sys.argv:
        probe()
    else:
        build()
