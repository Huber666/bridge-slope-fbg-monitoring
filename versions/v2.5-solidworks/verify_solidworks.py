"""Check saved native CAD in SolidWorks; do not change source geometry."""
import json
import math
import build_solidworks as cad


def verify():
    results = []
    for name, count in [("空腔钢支架_32deg.SLDASM", 2),
                        ("支架及承托板_32deg.SLDASM", 4),
                        ("坡体总装_32deg.SLDASM", 9)]:
        path = cad.OUT / name
        existing = cad.sw.GetOpenDocumentByName(str(path))
        if existing:
            cad.sw.CloseDoc(cad.wrap(existing, "IModelDoc2").GetTitle())
        obj, err, warn = cad.sw.OpenDoc6(str(path), 2, 1, "", 0, 0)
        if not obj or err:
            raise RuntimeError(f"Reopen failed: {name}: {err}, {warn}")
        doc = cad.wrap(obj, "IModelDoc2")
        assy = cad.wrap(doc, "IAssemblyDoc")
        components = assy.GetComponents(False) or []
        if len(components) != count:
            raise RuntimeError(f"Missing components: {name}")
        references = []
        for obj in components:
            comp = cad.wrap(obj, "IComponent2")
            referenced = comp.GetModelDoc2()
            if not referenced:
                raise RuntimeError(f"Unresolved reference: {comp.Name2}")
            t = cad.wrap(comp.Transform2, "IMathTransform").ArrayData
            if any(abs(a - b) > 1e-10 for a, b in zip(t, (1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0))):
                raise RuntimeError(f"Unexpected transform: {comp.Name2}")
            references.append(comp.GetPathName())
        detector = cad.wrap(assy.InterferenceDetectionManager, "IInterferenceDetectionMgr")
        detector.TreatCoincidenceAsInterference = False
        detector.IncludeMultibodyPartInterferences = True
        detector.MakeInterferingPartsTransparent = False
        interferences = []
        for obj in detector.GetInterferences() or []:
            item = cad.wrap(obj, "IInterference")
            names = [cad.wrap(c, "IComponent2").Name2 for c in item.Components]
            volume = item.Volume
            interferences.append({"components": names, "volume_m3": volume})
        detector.Done()
        results.append({"assembly": name, "reopen_errors": err,
                        "reopen_warnings": warn, "resolved_references": references,
                        "interferences": interferences})
        print(name, "references", len(references), "interferences", interferences, flush=True)
    solids = []
    record = json.loads((cad.ROOT / "CAD校验记录.json").read_text(encoding="utf-8"))
    for item in record["artifacts"]:
        if "bodies" not in item:
            continue
        obj = cad.sw.GetOpenDocumentByName(str(cad.OUT / item["file"]))
        doc = cad.wrap(obj, "IModelDoc2")
        body_results = []
        for obj in cad.wrap(doc, "IPartDoc").GetBodies2(0, False):
            b = cad.wrap(obj, "IBody2")
            code = b.Check2()
            if code:
                raise RuntimeError(f"Solid geometry fault: {item['file']}: {code}")
            body_results.append(code)
        errors = []
        obj = doc.FirstFeature()
        while obj:
            f = cad.wrap(obj, "IFeature")
            code = f.GetErrorCode2(False)
            if code[0]:
                errors.append({"feature": f.Name, "code": code})
            obj = f.GetNextFeature()
        if errors:
            raise RuntimeError(f"Feature errors: {item['file']}: {errors}")
        solids.append({"part": item["file"], "body_check2": body_results,
                       "feature_errors": errors})
    # Analytic independent volume checks for the vertically cut soil ends.
    expected = {"05_压实低渗土床_n40.SLDPRT": 1 * .5 * .04 + .1 * .5 * (.04 / cad.C),
                "06_砂或混合土_主动层_n120.SLDPRT": 1 * .5 * .12 + .1 * .5 * (.12 / cad.C)}
    volume_checks = []
    for filename, target in expected.items():
        entry = next(i for i in record["artifacts"] if i["file"] == filename)
        actual = sum(entry["volumes_m3"])
        if not math.isclose(actual, target, rel_tol=1e-8):
            raise RuntimeError(f"Soil volume mismatch: {filename}: {actual}, {target}")
        volume_checks.append({"file": filename, "cad_m3": actual, "analytic_m3": target})
    (cad.ROOT / "装配干涉与重开校验.json").write_text(json.dumps({
        "assemblies": results, "part_geometry": solids, "soil_volume_checks": volume_checks,
        "note": "FBG package intentionally lies inside active soil. No strength or loss-of-stability simulation is performed."
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    cad.sw.ActivateDoc3("坡体总装_32deg.SLDASM", False, 0, 0)


if __name__ == "__main__":
    verify()
