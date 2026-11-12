from pathlib import Path
from pdf2image import convert_from_path
from pypdf import PdfReader
import json
ROOT=Path(__file__).resolve().parent
out=ROOT/'_qa/render'
pdf=out/'report.pdf'
images=convert_from_path(str(pdf),dpi=110,poppler_path='C:/Users/asus/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin')
for i,im in enumerate(images,1):im.save(out/f'page-{i:02d}.png')
texts=[p.extract_text() or '' for p in PdfReader(pdf).pages]
(out/'extracted.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
report={'pages':len(images),'text_chars':[len(t) for t in texts],'first_lines':[t[:100] for t in texts]}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
