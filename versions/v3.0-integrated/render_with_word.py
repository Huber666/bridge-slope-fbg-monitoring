"""Local QA fallback when this Windows runtime has no bundled LibreOffice.

The canonical skill renderer must be attempted first. Use a separate invisible
Word instance, open each DOCX read-only, export intermediate PDFs and rasterize
with bundled Poppler through pdf2image. Never save the read-only source.
"""
from pathlib import Path
import json
import win32com.client
from pdf2image import convert_from_path, pdfinfo_from_path

ROOT=Path(__file__).resolve().parent
QA=ROOT/'_qa'
POPPLER=Path('C:/Users/asus/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin')

def main():
    app=win32com.client.DispatchEx('Word.Application')
    app.Visible=False;app.DisplayAlerts=0
    records=[]
    try:
        for src in ROOT.glob('*.docx'):
            out=QA/src.stem;out.mkdir(parents=True,exist_ok=True)
            # Remove only renderer-owned page images from an earlier run.
            for old in out.glob('page-*.png'):
                old.unlink()
            pdf=out/(src.stem+'.pdf')
            doc=app.Documents.Open(str(src),ReadOnly=True,AddToRecentFiles=False)
            try:
                doc.Repaginate()
                doc.ExportAsFixedFormat(str(pdf),17)
            finally:doc.Close(False)
            info=pdfinfo_from_path(str(pdf),poppler_path=str(POPPLER))
            images=convert_from_path(str(pdf),dpi=120,poppler_path=str(POPPLER))
            for i,im in enumerate(images,1):im.save(out/f'page-{i}.png')
            records.append({'file':src.name,'pages':info['Pages'],'png_count':len(images),'renderer':'Microsoft Word 16 read-only export and bundled Poppler 120 dpi'})
            print(records[-1],flush=True)
    finally:app.Quit()
    (QA/'render_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
