"""Build V4.1 diagrams and Word report without modifying earlier versions."""
from pathlib import Path
import sys, re, json, math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'v4.0-transverse-microstrain'))
import build_v4 as base
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
base.ASSETS=ROOT/'assets'
base.ASSETS.mkdir(exist_ok=True)
D=base.Drawing

def figures():
    f=D('横向主光路与三种局部感测路线',920)
    f.text((55,95),'① 有可靠表面  优先贴附或两端固定',30,True)
    f.rect((80,180,960,260),fill='#dfc8a7')
    f.line([(80,155),(960,155)],'#24647d',7)
    f.rect((200,185,340,210),fill='#b13c34')
    f.text((150,285),'贴片测梁面局部应变',27)
    f.line([(620,180),(600,220),(625,260)],'#b13c34',5)
    f.rect((540,200,570,240),fill='#a3b7c0')
    f.rect((680,200,710,240),fill='#a3b7c0')
    f.line([(555,220),(695,220)],'#b13c34',5)
    f.text((510,285),'两底座跨缝  测相对位移',27)
    f.text((1040,165),'主光路沿横梁\n局部感测件按变形方向\n尾纤松弛并保护',27)
    f.text((55,365),'② 新建加筋填土  施工期贴到受力肋',30,True)
    for y in [435,475,515]:f.line([(100,y),(900,y)],'#7e9a80',6)
    for x in range(100,950,100):f.line([(x,430),(x,530)],'#7e9a80',6)
    f.line([(395,435),(395,510)],'#b13c34',9)
    f.arrow((970,435),(970,525),both=True)
    f.text((1020,435),'感测方向沿承力肋\n不能只为横向走线\n改变受力方向',27)
    f.text((55,590),'③ 无可靠载体或目标在深部  孔内构件补测',30,True)
    f.rect((90,660,930,820),fill='#dfc8a7')
    f.line([(100,635),(900,635)],'#24647d',6)
    f.line([(440,640),(440,790)],'#7e9a80',12)
    f.line([(100,740),(900,740)],'#b13c34',3)
    for y in [690,725,755,785]:f.circle(450,y,6)
    f.text((520,680),'孔内杆跨剪切带',27)
    f.text((520,765),'孔口横向光缆汇接',27)
    f.text((1030,675),'必须检验回填和传力\n空孔松放光纤不可行\n稳定参考段另行确认',27)
    f.text((65,855),'示意不按比例  蓝色为光路  红色为感测段或目标裂缝',25)
    f.save('F01_安装路线')

    f=D('同一土箱更换表面与病害模块',860)
    f.text((65,105),'可换表面  每轮使用一种',30,True)
    labels=['C0 裸土','C1 活体草','C2 砂浆骨架','C3 连续面层','C4 土内格栅']
    for i,label in enumerate(labels):
        x=65+i*300
        f.rect((x,165,x+255,260),fill='#dfc8a7' if i<2 else '#dce8ee')
        f.text((x+8,280),label,25)
        if i==1:
            for xx in range(x+15,x+245,25):f.line([(xx,170),(xx-7,135),(xx,153),(xx+9,132)],'#4f7b53',3)
        if i==2:
            for yy in [180,210,240]:f.line([(x+12,yy),(x+242,yy)],'#657d88',8)
            for xx in [x+35,x+125,x+220]:f.line([(xx,170),(xx,250)],'#657d88',8)
        if i==4:
            for yy in [190,225]:f.line([(x+15,yy),(x+240,yy)],'#4f7b53',5)
    f.rect((150,405,1060,600),fill='#dfc8a7')
    f.text((185,425),'试验净空间 s600 × y800 × 高300 mm',30,True)
    f.text((185,480),'土厚160 mm  同批土与分层工艺保持可比',28)
    f.rect((150,600,1060,635),fill='#a3b7c0')
    for x in [200,500,800]:f.rect((x,635,x+170,715),fill='#dce8ee')
    f.text((185,730),'M1 张开',26)
    f.text((485,730),'M3 错动',26)
    f.text((785,730),'M2 下沉',26)
    f.text((1130,410),'观察壁可拆\n相机与位移架独立\n驱动器位于干区\n连续集水底在下方',28)
    f.text((1130,620),'先做水平传力试验\n再做坡槽自然演化',28)
    f.text((65,810),'三种模块择一装入  植被与格栅不是可随意撕下重贴的表皮',26)
    f.save('F02_模块与表面')

    f=D('框格贴附布点与必须保留的漏测对照',870)
    ox,oy,scale=105,140,1.05
    xy=lambda s,y:(ox+y*scale,oy+s*scale)
    f.rect((ox,oy,ox+800*scale,oy+600*scale),fill='#f3eadc')
    for s in [150,300,450]:
        a,b=xy(s,100),xy(s,700)
        f.line([a,b],'#a3b7c0',23)
        f.line([(a[0],a[1]-17),(b[0],b[1]-17)],'#24647d',4)
        for y in [175,475]:
            x,z=xy(s,y);f.circle(x,z,9)
    for y in [100,400,700]:f.line([xy(75,y),xy(525,y)],'#a3b7c0',23)
    # Repaint sensing markers after structural lines.
    for s in [150,300,450]:
        for y in [175,475]:
            x,z=xy(s,y);f.circle(x,z,9)
        f.text((ox+745*scale,oy+s*scale-17),f'H{[150,300,450].index(s)+1}',26)
    x,z=xy(225,250)
    f.rect((x-52,z-52,x+52,z+52),fill='#edc8c3',outline='#b13c34',width=3)
    f.text((x-45,z-18),'格内',25)
    x,z=xy(300,400)
    f.rect((x-52,z-52,x+52,z+52),fill='#c9dce5',outline='#24647d',width=3)
    f.text((x-45,z-18),'节点',25)
    f.arrow((ox,120),(ox+840,120),both=True)
    f.text((400,75),'横坡 y 800 mm',27)
    f.text((1010,160),'红点为候选测量位置\n每处上面与侧面各1栅\n6处共12应变栅\n另3温度栅  合计15栅',29)
    f.text((1010,370),'蓝区  撤去梁下支承\n检验构件弯曲响应',29)
    f.text((1010,485),'红区  撤去格内支承\n土体动而骨架可能不动\n记录贴附方案漏测',29)
    f.text((1010,650),'这两种位置分次重建\n不能在同一试次混用',28)
    f.text((110,805),'s向下  横梁s150/300/450  纵梁y100/400/700  示意尺寸单位mm',24)
    f.save('F03_布点与盲区')

def build():
    path=ROOT/'边坡类型表面防护与贴附光纤试验方案.md'
    doc=Document();base.setup(doc)
    for p in doc.sections[0].footer.paragraphs:
        for run in p.runs:run.text=run.text.replace('V4.0','V4.1').replace('2026-10-28','2026-11-12')
    doc.styles['Normal'].paragraph_format.space_after=Pt(5)
    doc.styles['Normal'].paragraph_format.line_spacing=1.10
    doc.styles['Heading 1'].font.size=Pt(16)
    lines=path.read_text(encoding='utf-8').splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')]);i+=1
            base.table(doc,rows);continue
        if line=='---PAGE---':pass
        elif line.startswith('# '):doc.add_paragraph(line[2:],style='Title')
        elif line.startswith('## '):doc.add_paragraph(line[3:],style='Heading 1')
        elif line.startswith('!['):
            m=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
            p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next=True
            shape=p.add_run().add_picture(str(ROOT/m[2]),width=Inches(6.8))
            shape._inline.docPr.set('descr',m[1])
        elif re.match(r'^图\d+',line):
            p=doc.add_paragraph(line,style='Caption');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        else:
            p=doc.add_paragraph();base.text_runs(p,line)
            if re.match(r'^S\d+ ',line):p.paragraph_format.keep_with_next=True
        i+=1
    doc.save(path.with_suffix('.docx'))
    c={'status':'design_examples_not_measured','direct_1mm_over_100mm_ue':10000,'direct_3mm_over_100mm_ue':30000,'ideal_beam_ue_per_mm':3*.5/120**2*(1-2*15/120)*1e6,'ideal_beam_N_per_mm':193000*10*.5**3/120**3,'gratings_core':6*2+3,'gratings_with_two_single_fbg_displacement_gauges':6*2+3+2,'horizontal_rain_20mmh_20min_L':.6*.8*20/3}
    assert math.isclose(c['ideal_beam_ue_per_mm'],78.125)
    (ROOT/'设计计算.json').write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(path.with_suffix('.docx')),'paragraphs':len(doc.paragraphs),'tables':len(doc.tables),'figures':len(doc.inline_shapes),'calculations':c},ensure_ascii=False,indent=2))
if __name__=='__main__':figures();build()
