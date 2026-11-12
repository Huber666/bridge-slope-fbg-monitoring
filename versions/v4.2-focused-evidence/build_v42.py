"""Build the focused research plan and original figures. No earlier version is edited."""
from pathlib import Path
import sys,re,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'v4.0-transverse-microstrain'))
import build_v4 as base
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
base.ASSETS=ROOT/'assets';base.ASSETS.mkdir(exist_ok=True)
D=base.Drawing

def figures():
    f=D('相同测量链  两种底座安装分别校准',620)
    f.rect((100,340,1450,460),'#dfc8a7')
    f.line([(775,340),(755,390),(780,460)],'#b13c34',5)
    for x in [370,1080]:f.rect((x,295,x+80,350),'#a3b7c0')
    f.line([(410,295),(1120,295)],'#657d88',9)
    f.rect((730,280,810,295),'#b13c34')
    f.line([(810,280),(860,230),(1410,230)],'#24647d',5)
    f.text((125,115),'金属载体上粘FBG\n载体两端传递相对运动',30)
    f.text((970,115),'温度栅邻近且隔离机械应变\n尾纤横向引出  松弛保护',28)
    f.text((200,490),'同一组件两端统一固定方式  粘接组或浅孔组',28)
    f.text((120,555),'图示为共同传力路径  两种固定方式分次比较',26)
    f.save('F01_安装与传力')
    f=D('方向A  受控微动先验证安装和检测限',650)
    f.rect((130,230,720,430),'#dfc8a7');f.rect((780,230,1370,430),'#dfc8a7')
    f.rect((130,430,720,470),'#a3b7c0');f.rect((780,430,1370,470),'#a3b7c0')
    f.text((265,480),'固定端',30,True);f.text((980,480),'精密移动端',30,True)
    f.rect((520,215,580,240),'#657d88');f.rect((920,215,980,240),'#657d88')
    f.line([(550,215),(950,215)],'#b13c34',7)
    f.text((520,145),'跨缝组件  有效标距实测',28)
    f.arrow((1380,330),(1500,330));f.text((1310,370),'小幅差动',25)
    f.circle(580,315,8);f.circle(920,315,8)
    f.arrow((580,315),(920,315),both=True)
    f.text((515,540),'独立参考测混凝土两点差动\n另看底座是否滑移  不直接用电机读数作真值',27)
    f.text((80,90),'P1/P2提供传力依据  本装置为改造设计  不是完整坡体',27)
    f.save('F02_微动台架')
    f=D('方向B  小型混凝土梁的真实受弯开裂',780)
    x0,k=140,1.15
    X=lambda x:x0+x*k
    f.rect((X(0),230,X(1100),345),'#dfc8a7')
    f.line([(X(20),322),(X(1080),322)],'#657d88',4)
    for x in [250,850]:
        xx=X(x);f.line([(xx,345),(xx-35,405),(xx+35,405),(xx,345)],'#24647d',4)
    f.arrow((X(550),115),(X(550),225),'#b13c34')
    f.text((X(550)+40,95),'中心加载  2.5 N/s来自P2\n实际停机值另核定',27)
    for x in [400,700]:f.rect((X(x)-10,345,X(x)+10,370),'#657d88')
    f.line([(X(400),370),(X(700),370)],'#b13c34',6)
    f.arrow((X(0),190),(X(1100),190),both=True)
    f.text((240,140),'试件总长1100',28)
    f.arrow((X(250),455),(X(850),455),both=True);f.text((660,470),'支承跨距600',28)
    f.text((120,535),'截面100 × 100   两根直径8钢筋   原文养护28 d',28)
    f.text((120,590),'受拉面跨缝组件标距300   温度参考邻近   相机同时看锚点与裂缝',27)
    f.text((120,645),'首轮无预制缺口为本项目改动  不承诺裂缝出现位置与原文一致',27)
    f.text((120,710),'单位mm  P2原尺寸  坐标由居中布置推算  非加工详图或全坡缩尺',26)
    f.save('F03_梁试验')

def build():
    p=ROOT/'重点方向与最小可行试验方案.md';doc=Document();base.setup(doc)
    for para in doc.sections[0].footer.paragraphs:
        for run in para.runs:run.text=run.text.replace('V4.0','V4.2').replace('2026-10-28','2026-11-12')
    doc.styles['Normal'].paragraph_format.line_spacing=1.08
    doc.styles['Normal'].paragraph_format.space_after=Pt(6)
    doc.styles['Heading 1'].font.size=Pt(16)
    lines=p.read_text(encoding='utf-8').splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')]);i+=1
            base.table(doc,rows);continue
        if line=='<!-- PAGE -->':pass
        elif line.startswith('# '):doc.add_paragraph(line[2:],style='Title')
        elif line.startswith('## '):doc.add_paragraph(line[3:],style='Heading 1')
        elif line.startswith('!['):
            m=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
            para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER
            para.paragraph_format.keep_with_next=True
            sh=para.add_run().add_picture(str(ROOT/m[2]),width=Inches(6.7));sh._inline.docPr.set('descr',m[1])
        elif re.match(r'^图\d+',line):
            para=doc.add_paragraph(line,style='Caption');para.alignment=WD_ALIGN_PARAGRAPH.CENTER
        else:
            para=doc.add_paragraph();base.text_runs(para,line)
            if re.match(r'^P\d+ ',line):para.paragraph_format.keep_with_next=True
        i+=1
    doc.save(p.with_suffix('.docx'))
    vals={'provenance':'P2 geometry; derived values are calculations, not measurements','beam_mm':[1100,100,100],'span_mm':600,'gauge_mm':300,'volume_m3':1.1*.1*.1,'mass_at_assumed_2400kgm3':1.1*.1*.1*2400,'rate_N_s':.0025*1000,'ideal_ue_for_1_5_20um':[u/1000/300*1e6 for u in [1,5,20]],'single_node_gratings':2}
    (ROOT/'设计核算.json').write_text(json.dumps(vals,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'docx':str(p.with_suffix('.docx')),'tables':len(doc.tables),'images':len(doc.inline_shapes),'calculations':vals},ensure_ascii=False))
if __name__=='__main__':figures();build()
