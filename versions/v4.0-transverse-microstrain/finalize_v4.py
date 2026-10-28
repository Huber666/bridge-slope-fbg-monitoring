"""Synchronize edition metadata and check authored references before rendering."""
from pathlib import Path
import re,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parent
for p in ROOT.glob('0[1-4]_*.md'):
    t=p.read_text(encoding='utf-8')
    t=t.replace('V4.0 工作稿　2026年10月27日　内容已保存 最终复核待完成','V4.0 研究设计版　2026年10月28日　样件与工程参数须实物验证')
    if p.name.startswith('01_'):
        t=t.replace('证据状态以2026-10-27本次取得的正文或既有记录标记。','证据核查截至2026-10-28，区分本次取得的正文与继承记录。')
    p.write_text(t,encoding='utf-8')
errors=[]
for p in ROOT.glob('*.md'):
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if not target.startswith(('http:','https:','#')) and not (p.parent/target).exists():errors.append({'file':p.name,'missing':target})
if errors:raise SystemExit(json.dumps(errors,ensure_ascii=False))
print('All authored local links resolve.')
