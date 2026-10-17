"""Rebuild the two V2.6 manuals and original technical illustrations.

Use the Codex bundled Python. No SolidWorks session is started.
"""
from pathlib import Path
import math
import re
import json
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
FONT = 'C:/Windows/Fonts/msyh.ttc'
FONT_B = 'C:/Windows/Fonts/msyhbd.ttc'
C, S = math.cos(math.radians(32)), math.sin(math.radians(32))
SH, TOE = 80 + 1000*S, 150 + 1000*C
INK, BLUE, EARTH, BED, RED = '#18252d', '#2c6680', '#d4b286', '#90735b', '#b33d32'

def font(size=32, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)

class Drawing:
    def __init__(self, title, h=780):
        self.im = Image.new('RGB', (1600,h),'white')
        self.d = ImageDraw.Draw(self.im)
        self.text((45,25),title,38,True)
    def text(self,p,t,size=32,bold=False,fill=INK,anchor=None):
        self.d.text(p,t,font=font(size,bold),fill=fill,anchor=anchor,spacing=10)
    def line(self,p,fill=INK,width=3):
        self.d.line(p,fill=fill,width=width)
    def arrow(self,a,b,fill=BLUE,width=4,both=False):
        self.line([a,b],fill,width)
        def head(q,p):
            th=math.atan2(p[1]-q[1],p[0]-q[0])
            pts=[p,(p[0]-15*math.cos(th-.45),p[1]-15*math.sin(th-.45)),(p[0]-15*math.cos(th+.45),p[1]-15*math.sin(th+.45))]
            self.d.polygon(pts,fill=fill)
        head(a,b)
        if both: head(b,a)
    def box(self,xy,t,fill='#edf3f5',size=32):
        self.d.rounded_rectangle(xy,radius=10,fill=fill,outline='#77858c',width=2)
        x1,y1,x2,y2=xy
        self.text(((x1+x2)/2,(y1+y2)/2),t,size,anchor='mm')
    def save(self,name):
        self.im.save(ASSETS/name)

def section():
    f=Drawing('固定 32° 纵剖面   单位 mm   工程坐标 x 向右  z 向上',900)
    ox, oy, k = 110,795,.79
    def p(x,z): return ox+x*k,oy-z*k
    f.d.rectangle([p(0,850),p(1400,0)],outline=BLUE,width=4)
    deck=SH-40/C
    f.d.polygon([p(50,deck),p(150,deck),p(TOE,80-40/C),p(TOE,80),p(150,SH),p(50,SH)],fill=BED)
    f.d.polygon([p(50,SH),p(150,SH),p(TOE,80),p(TOE,80+120/C),p(150,SH+120/C),p(50,SH+120/C)],fill=EARTH)
    f.line([p(50,deck),p(150,deck),p(TOE,80-40/C)],INK,7)
    f.line([p(60,0),p(920,0),p(150,deck),p(60,0)],BLUE,5)
    f.text(p(150,220),'板下空腔\n只减用土量',34)
    f.text(p(1120,250),'坡脚\n收集区',32)
    f.text((130,90),'槽高 850',30)
    f.text((410,115),'主动层 120 法向\n最高土面 z = 751.421',30)
    f.arrow((540,205),p(450,SH-300*math.tan(math.radians(32))+75))
    f.text((1000,200),'低渗床 40 法向\n下方 304 承托板厚 3',30)
    f.arrow((1060,300),p(700,SH-550*math.tan(math.radians(32))-22))
    a,b=p(150,SH+190),p(TOE,80+190)
    f.arrow(a,b,both=True)
    f.text(((a[0]+b[0])/2-30,(a[1]+b[1])/2-60),'斜长 1000',32)
    f.text((160,815),'平台 100     水平投影 848.048       收集区 401.952',32)
    f.text((1050,690),'床面坡脚 z = 80',30)
    f.text((1050,740),'承托板顶 z = 32.833',30)
    f.text((980,825),'净槽长 1400   宽 500',32)
    f.save('M02_总剖面.png')

def assembly():
    f=Drawing('装配接口与荷载传递   示意非加工放行图',820)
    labels=[('实心主动土层 120 + 低渗床 40',EARTH),('304 连续承托板 3', '#a4b7c1'),('EPDM 隔离垫条 1','#c1c9cd'),('Q235B 空腔钢架及低位托座','#728b98'),('304 槽底 3 + 外底架密集支承','#a4b7c1')]
    for i,(t,col) in enumerate(labels):
        y=115+i*106
        f.box((100,y,940,y+72),t,col)
        if i<4:f.arrow((520,y+77),(520,y+101))
    f.box((1010,115,1530,270),'PC 壁预选 8\n外侧连续压框与密封垫')
    f.box((1010,315,1530,470),'连接件不穿主动层\n支架须有防侧移连接')
    f.box((1010,515,1530,670),'调平支脚及防侧移斜撑\n地面承压和重心另算')
    f.text((100,715),'先定位连接和限水检漏，再铺土。未建模接口须由加工方统一出图。',32)
    f.save('M05_装配接口.png')

def soil():
    f=Drawing('配土与称量   所有配比按干质量',760)
    f.box((70,130,480,280),'砂与高岭土\n分别测初始含水率')
    f.box((595,130,1005,280),'按干基换算湿料\n称量分开登记')
    f.box((1120,130,1530,280),'低扬尘预混\n分次雾化加水')
    f.arrow((485,205),(585,205)); f.arrow((1010,205),(1110,205))
    f.box((1120,430,1530,580),'含细料组密封调湿\n复拌与多点测水分')
    f.box((595,430,1005,580),'每层按体积和密度\n计算目标湿质量')
    f.box((70,430,480,580),'按层编号铺筑\n厚度与质量双复核')
    f.arrow((1325,290),(1325,420)); f.arrow((1110,505),(1010,505));f.arrow((585,505),(490,505))
    f.text((70,650),'A10 算例  干料 10 kg = 干砂 9 kg + 干高岭土 1 kg',34)
    f.save('M09_制样流程.png')

def layers():
    f=Drawing('铺土顺序与安装停检点   单位 mm',880)
    x1,x2,y0,h=170,1080,170,65
    for i in range(8):
        y=y0+i*h
        fill=('#e2c8a7' if i%2==0 else EARTH) if i<6 else BED
        f.d.rectangle((x1,y,x2,y+h),fill=fill,outline='white',width=3)
        layer=6-i if i<6 else 8-i
        txt=f'主动层第 {layer} 层   n = {100-i*20} 至 {120-i*20}' if i<6 else f'低渗床第 {layer} 层'
        f.text((205,y+14),txt,30)
    y=y0+4*h
    f.line([(x1,y),(x2,y)],RED,7)
    for x in (380,780): f.d.rectangle((x,y-8,x+100,y+8),fill=RED)
    f.text((1130,y-55),'n = 40\n装光栅\n及真值探头',32,fill=RED)
    f.arrow((1150,y+80),(1150,y+150),RED)
    f.text((1100,150),'n = 120 土表',30)
    f.text((1100,y0+6*h+15),'n = 0 床顶',30)
    f.text((185,735),'铺筑自下而上，每层法向 20；平台相应竖直增量约 23.584。',30)
    f.text((185,790),'红线为安装高度，示意横断面；光栅实际长轴沿坡向。',30)
    f.save('M12_分层铺土.png')

def system():
    f=Drawing('独立供水  光栅阵列  真值联合观测',820)
    f.box((65,145,400,285),'水箱与泵\n记录补水和压力')
    f.box((620,110,1030,250),'喷头及独立架\n水平接雨标定')
    f.box((560,385,1100,565),'32° 实心分层土坡\n8 应变 FBG + 2 温度点', '#e9d4b8')
    f.box((65,415,400,555),'槽外光学接续箱\n解调器与原始波长')
    f.box((1200,345,1540,505),'侧视及俯视相机\n标尺与表面标记')
    f.box((1200,560,1540,720),'水分或吸力\n位移及振动参考')
    f.box((590,655,1080,770),'径流  床面渗流  裸槽接雨\n分路收集计量')
    f.arrow((400,215),(610,185));f.arrow((825,255),(825,375));f.arrow((550,475),(410,475));f.arrow((1110,445),(1190,425));f.arrow((1110,525),(1190,625));f.arrow((825,575),(825,645))
    f.save('E01_实验系统.png')

def package():
    f=Drawing('三段式保护   感测传力与非感测铠装分离',780)
    f.box((70,190,620,365),'短感测封装\n总长 100 至 150 候选\n机械标距 50 至 80 候选','#e9d4b8')
    f.line([(100,410),(220,410),(240,445),(270,375),(300,445),(330,410),(600,410)],RED,5)
    f.text((110,485),'短条接触局部土体\n组件整体校准与湿态拉拔',30)
    f.box((700,190,1080,365),'节点间柔性松套\n缓弯与自由长度')
    f.box((1160,190,1530,365),'槽外保护引线\n可按需加铠')
    f.arrow((625,270),(690,270));f.arrow((1085,270),(1150,270))
    f.text((720,430),'不固定到框架\n不绷直连接两土块',30)
    f.text((1170,430),'护口及防滴水弯\n独立应力释放',30)
    f.text((70,640),'不以连续钢铠加固坡体；温度参考采用经验证的短松套机械隔离。',32)
    f.save('E03_封装分区.png')

def fiber():
    f=Drawing('床面展开点位   s 向坡脚   y 横坡   单位 mm',780)
    x0,y0,k=175,150,1.13
    f.d.rectangle((x0,y0,x0+1000*k,y0+500*k),fill='#f7eddf',outline=BLUE,width=4)
    for row,y in enumerate((150,350),1):
        yy=y0+y*k
        for col,s in enumerate((125,375,625,875),1):
            xx=x0+s*k
            f.d.rectangle((xx-55*k,yy-9,xx+55*k,yy+9),fill=RED)
            f.text((xx,yy-50),f'S{row}{col}',30,anchor='mm')
            if col<4:
                f.d.arc((xx+62,yy-20,xx+220,yy+25),0,180,fill=RED,width=3)
            f.text((xx,735),str(s),30,anchor='mm')
        f.text((50,yy-20),f'y={y}',30)
        f.d.ellipse((x0+375*k-12,yy+45,x0+375*k+12,yy+69),fill=BLUE)
        f.text((x0+375*k+20,yy+45),f'T{row}',28)
    f.text((200,95),'坡肩 s=0',30)
    f.text((1180,95),'坡脚 s=1000',30)
    f.line([(x0,y0+250*k),(x0+1000*k,y0+250*k)],'#87939a',2)
    f.text((1350,420),'中心\ny=250\n真值避让',30)
    f.save('E04_光纤点位.png')

def rainfall():
    f=Drawing('先导程序示例   落土面积 0.474024 m²',800)
    x0,y0,xs,ys=150,600,20,6
    f.line([(x0,130),(x0,y0),(1400,y0)],INK,3)
    for val in (0,20,40,60):
        y=y0-val*ys
        f.line([(x0,y),(1350,y)],'#d5dde0',2)
        f.text((70,y-20),str(val),30)
    for a,b,v,col in [(0,20,20,'#b4d5e1'),(20,40,40,'#78a9bd'),(40,60,60,'#467b95')]:
        f.d.rectangle((x0+a*xs,y0-v*ys,x0+b*xs,y0),fill=col)
        f.text((x0+(a+b)/2*xs,y0-v*ys+45),f'{v} mm/h',30,True,anchor='mm')
        f.text((x0+(a+b)/2*xs,665),f'{v*.474024048/3:.3f} L',32,anchor='mm')
    for t in (0,20,40,60):f.text((x0+t*xs,620),str(t),30,anchor='mm')
    f.text((1220,690),'时间 min',30)
    f.text((175,735),'落土累计 18.961 L   覆盖全槽累计 28 L   另加实际过喷',30)
    f.save('E07_降雨水量.png')

def excavation():
    f=Drawing('局部坡脚开挖   横向窗口与位置边界',760)
    f.d.polygon([(100,200),(800,560),(800,400),(100,70)],fill=EARTH)
    f.line([(100,200),(800,560)],BED,18)
    f.d.rectangle((690,410,800,490),outline=RED,width=5)
    f.arrow((1080,460),(815,460),RED)
    f.text((920,360),'水平进深先试 10 mm\n工具撤离后再观察',32)
    f.text((110,270),'不切低渗床\n不碰承托板或光纤',32)
    f.d.rectangle((170,590,1290,675),fill='#e8eef1',outline=BLUE,width=3)
    f.d.rectangle((562,590,898,675),fill='#e7ada5',outline=RED,width=3)
    f.text((200,690),'y = 0',30);f.text((1150,690),'y = 500',30)
    f.text((730,632),'窗口 y = 175 至 325   宽 150',30,anchor='mm')
    f.text((1060,180),'上：坡脚侧视\n下：窗口横向位置',32)
    f.save('E09_坡脚开挖.png')

def observation():
    f=Drawing('主动层代表性观测   n 从床顶向表面',780)
    x1,x2,y1=180,1280,190
    f.d.rectangle((x1,y1,x2,y1+360),fill=EARTH)
    f.d.rectangle((x1,y1+360,x2,y1+480),fill=BED)
    for n in (0,20,40,80,120):
        y=y1+(120-n)*3
        f.line([(x1,y),(x2,y)],'#f7ead8',2)
        f.text((50,y-18),f'n={n}',30)
    for x,n,t in [(480,80,'上部水分'),(820,20,'近床水分')]:
        y=y1+(120-n)*3
        f.d.ellipse((x-22,y-22,x+22,y+22),fill=BLUE)
        f.text((x+40,y-15),t,30)
    f.d.rectangle((240,y1+240-8,350,y1+240+8),fill=RED)
    f.text((240,y1+240-53),'FBG 在 n=40',30)
    f.text((940,y1+395),'低渗土床 40',32)
    f.text((140,710),'示意为中坡断面；探头在 y=250 附近，实际尺寸须避开两排 FBG。',30)
    f.text((1310,200),'土表',30);f.text((1310,530),'床顶',30)
    f.save('E11_观测断面.png')

def dataflow():
    f=Drawing('按独立重建划分   先划分再切窗与归一化',720)
    f.box((50,120,430,280),'每个独立坡体\n一个 trial_id')
    f.box((610,90,980,230),'训练试验组')
    f.box((610,285,980,425),'验证试验组')
    f.box((610,480,980,620),'测试试验组')
    for yy in (160,355,550):f.arrow((440,220),(600,yy))
    f.box((1160,90,1540,230),'训练内切窗\n拟合归一化与阈值')
    f.box((1160,285,1540,425),'验证内切窗\n选择模型参数')
    f.box((1160,480,1540,620),'测试内切窗\n独立性能评估')
    for yy in (160,355,550):f.arrow((990,yy),(1150,yy))
    f.text((60,655),'同一坡体的相邻窗口、同次降雨的不同阶段，不能分到不同集合。',30)
    f.save('E13_数据划分.png')

def add_link(p,text,url):
    link=OxmlElement('w:hyperlink')
    rid=p.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
    link.set(qn('r:id'),rid)
    r=OxmlElement('w:r'); pr=OxmlElement('w:rPr')
    color=OxmlElement('w:color');color.set(qn('w:val'),'245A75');pr.append(color);r.append(pr)
    t=OxmlElement('w:t');t.text=text;r.append(t);link.append(r);p._p.append(link)

def text_runs(p,t):
    t=t.replace('**','').replace('*','')
    for part in re.split(r'(https://[^\s。]+)',t):
        if part.startswith('https://'):add_link(p,part,part)
        else:p.add_run(part)

def setup(doc):
    sec=doc.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=Inches(.65);sec.bottom_margin=Inches(.65)
    sec.left_margin=Inches(.8);sec.right_margin=Inches(.8)
    sec.footer_distance=Inches(.28)
    for name,sz in [('Normal',11),('Title',24),('Subtitle',11),('Heading 1',17),('Heading 2',13),('Heading 3',11),('Caption',10)]:
        st=doc.styles[name];st.font.name='Microsoft YaHei';st.font.size=Pt(sz);st.font.color.rgb=RGBColor(0,0,0)
        st.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
        st.paragraph_format.space_after=Pt(6 if name=='Normal' else 9)
        st.paragraph_format.line_spacing=1.15
        ppr=st.element.find(qn('w:pPr'))
        if ppr is not None:
            for border in list(ppr.findall(qn('w:pBdr'))):ppr.remove(border)
    doc.styles['Caption'].font.bold=False
    doc.styles['Normal'].paragraph_format.widow_control=True
    for name in ['Heading 1','Heading 2']:
        doc.styles[name].paragraph_format.keep_with_next=True
    f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=f.add_run('V3.0　|　');r.font.size=Pt(9)
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');f._p.append(fld)
    doc.core_properties.author='桥梁边坡光纤监测项目组'
    doc.core_properties.last_modified_by='桥梁边坡光纤监测项目组'

def table(doc,rows):
    rows=[r for r in rows if not all(re.match(r'^:?-+:?$',c.strip()) for c in r)]
    n=len(rows[0]);t=doc.add_table(rows=0,cols=n);t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
    weights={2:[.23,.77],3:[.23,.37,.40],4:[.18,.26,.22,.34],5:[.26,.16,.19,.19,.20],6:[.18,.22,.15,.15,.15,.15]}.get(n,[1/n]*n)
    for c,w in zip(t.columns,weights):c.width=Inches(6.9*w)
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
    t._tbl.tblPr.append(borders)
    for i,row in enumerate(rows):
        cells=t.add_row().cells
        trpr=t.rows[-1]._tr.get_or_add_trPr()
        if i==0:trpr.append(OxmlElement('w:tblHeader'))
        trpr.append(OxmlElement('w:cantSplit'))
        for j,(cell,txt) in enumerate(zip(cells,row)):
            cell.width=Inches(6.9*weights[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=cell._tc.get_or_add_tcPr();margin=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                m=OxmlElement('w:'+side);m.set(qn('w:w'),'75');m.set(qn('w:type'),'dxa');margin.append(m)
            tcpr.append(margin)
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DCE8EE' if i==0 else ('F5F7F8' if i%2==0 else 'FFFFFF'));tcpr.append(shade)
            p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(1);p.paragraph_format.space_before=Pt(1);p.paragraph_format.line_spacing=1.12
            if i==0:
                # Keep the header with the first data row when a table starts
                # near a page boundary; repeated headers remain readable.
                p.paragraph_format.keep_with_next=True
            if len(txt)<16:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            r=p.add_run(txt);r.font.size=Pt(10);r.bold=i==0
    doc.add_paragraph().paragraph_format.space_after=Pt(2)

def build(mdname):
    doc=Document();setup(doc)
    lines=(ROOT/mdname).read_text(encoding='utf-8').splitlines()
    i=0;pagebreak=False
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line=='<!-- page -->':
            # Cover is separate; subsequent chapters flow to avoid near-empty
            # figure continuation pages. Headings keep with their first block.
            pagebreak = not any(p.style.name=='Heading 1' for p in doc.paragraphs)
            i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append([s.strip() for s in lines[i].strip().strip('|').split('|')]);i+=1
            table(doc,rows);continue
        if line.startswith('# '):p=doc.add_paragraph(line[2:],style='Title')
        elif line.startswith('#### '):p=doc.add_paragraph(line[5:],style='Heading 3')
        elif line.startswith('### '):p=doc.add_paragraph(line[4:],style='Heading 2')
        elif line.startswith('## '):p=doc.add_paragraph(line[3:],style='Heading 1')
        elif line.startswith('!['):
            m=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line);path=(ROOT/m[2]).resolve()
            p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
            with Image.open(path) as im:iw,ih=im.size
            w=min(6.9,4.1*iw/ih)
            shape=p.add_run().add_picture(str(path),width=Inches(w));shape._inline.docPr.set('descr',m[1])
        elif line.startswith('图') and re.match(r'^图[ME]\d+',line):
            p=doc.add_paragraph(line,style='Caption');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        else:
            p=doc.add_paragraph();text_runs(p,line)
        if pagebreak:p.paragraph_format.page_break_before=True;pagebreak=False
        i+=1
    path=ROOT/Path(mdname).with_suffix('.docx');doc.save(path)
    print(path.name,'paragraphs',len(doc.paragraphs),'tables',len(doc.tables),'figures',len(doc.inline_shapes))

def templates():
    p=ROOT/'templates';p.mkdir(exist_ok=True)
    # JSON avoids ambiguous prefilled results; no claim these are measured.
    example={
        'trial_id':None,'batch_id':None,'configuration_version':'V3.0','cad_version':'V3.0 (V2.5 CAD source)',
        'operator':None,'date_timezone':'Asia/Shanghai','independent_rebuild':None,
        'geometry_measured_mm':{'net_L':None,'net_W':None,'net_H':None,'active_normal':None,'bed_normal':None},
        'angle_measured_deg':None,'materials':{'active_dry_ratio':None,'bed_dry_ratio':None,'active_dry_density_kg_m3':None,'bed_dry_density_kg_m3':None,'active_water_content_dry_basis':None,'bed_water_content_dry_basis':None},
        'optical':{'system_type':None,'actual_full_channel_rate_Hz':None,'calibration_id':None,'wavelength_raw_units':None},
        'sync':{'method':None,'error_bound_ms':None,'drift_ms':None},
        'rain':{'calibration_id':None,'horizontal_soil_area_m2':.474024048,'planned_steps':[],'actual_rain_start':None,'actual_rain_end':None},
        'boundary':{'side_seal':None,'toe_drain':None,'bed_interface':None},
        'pretest_acceptance':None,'stop_reason':None,'actual_event':None,'optical_valid_intervals':[],
        'reused_soil':None,'deviations':[],'reviewer':None}
    (p/'单次试验元数据模板.json').write_text(json.dumps(example,ensure_ascii=False,indent=2),encoding='utf-8')
    specs={
        '分层称量记录.csv':'trial_id,layer_id,material_batch,dry_ratio,target_normal_thickness_mm,measured_normal_thickness_mm,volume_m3,target_dry_density_kg_m3,raw_water_content_dry_basis,target_water_content_dry_basis,raw_wet_mass_kg,added_water_kg,placed_wet_mass_kg,measured_water_content_dry_basis,compaction_tool,passes,photo_id,operator,remark\n',
        '实际用水与排水日志.csv':'trial_id,stage_id,start_time,end_time,target_intensity_mm_h,calibrated_actual_intensity_mm_h,soil_horizontal_area_m2,planned_soil_rain_L,estimated_actual_soil_rain_L,tank_start_L,tank_added_L,tank_end_L,surface_runoff_L,bed_drain_L,bare_area_rain_L,abnormal_leak_L,measurement_uncertainty,stop_reason\n',
        '事件标签记录.csv':'trial_id,event_id,start_time_or_interval,end_time_or_interval,event_type,phase,trigger,position_s_y_n_mm,material_state,video_frames,reference_displacement,confidence,optical_validity,annotator,reviewer,remarks\n',
        '传感点位与标定记录.csv':'trial_id,sensor_id,branch_id,sensor_serial,actual_s_mm,actual_y_mm,actual_n_mm,actual_x_mm,actual_z_mm,axis,gauge_length_mm,calibration_id,K_strain_with_units,K_temp_with_units,static_bend_radius_mm,dynamic_bend_radius_mm,baseline_wavelength,peak_quality,photo_id\n'
    }
    for name,txt in specs.items():(p/name).write_text(txt,encoding='utf-8-sig')

if __name__=='__main__':
    for fn in [section,assembly,soil,layers,system,package,fiber,rainfall,excavation,observation,dataflow]:fn()
    templates()
    for name in ['模型制造与装配手册.md','边坡监测试验操作手册.md','文献综合评述与模型设计依据.md']:build(name)
