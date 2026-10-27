"""Rasterize local Word-exported PDFs after canonical renderer lacks LibreOffice."""
from pathlib import Path
import json
from pdf2image import convert_from_path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
POPPLER='C:/Users/asus/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'
reports=[]
for pdf in sorted((ROOT/'_qa'/'word_render').glob('0*.pdf')):
    out=pdf.parent/pdf.stem
    out.mkdir(exist_ok=True)
    pages=convert_from_path(str(pdf),dpi=120,poppler_path=POPPLER)
    for i,im in enumerate(pages,1):im.save(out/f'page-{i:02d}.png')
    texts=[p.extract_text() for p in PdfReader(pdf).pages]
    reports.append({'file':pdf.name,'pages':len(pages),'text_chars_per_page':[len(x) for x in texts],'page_files':[str(out/f'page-{i:02d}.png') for i in range(1,len(pages)+1)]})
    (out/'extracted.txt').write_text('\n\n'.join(f'PAGE {i+1}\n'+t for i,t in enumerate(texts)),encoding='utf-8')
(ROOT/'_qa'/'render_manifest.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(reports,ensure_ascii=False,indent=2))
