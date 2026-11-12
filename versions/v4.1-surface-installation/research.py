"""Retrieve source pages for local review; cache is excluded from publication."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request, urllib.parse, re, html, json, sys, logging
logging.getLogger('pypdf').setLevel(logging.ERROR)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'_qa'/'sources'
OUT.mkdir(parents=True,exist_ok=True)
def strip(s):
    s=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',s,flags=re.S|re.I)
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def fetch(pair):
    key,url=pair
    try:
        url=urllib.parse.quote(url,safe=':/?=&%+;#')
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=30) as r:
            raw=r.read();final=r.url
        if raw.startswith(b'%PDF'):
            from pypdf import PdfReader
            p=OUT/(key+'.pdf');p.write_bytes(raw)
            pages=[p.extract_text() or '' for p in PdfReader(p).pages]
            text='\n\n'.join(f'PDF_PAGE {i+1}\n{t}' for i,t in enumerate(pages))
            links=[]
        else:
            s=raw.decode('utf-8',errors='replace');text=strip(s)
            (OUT/(key+'.html')).write_text(s,encoding='utf-8')
            links=[{'text':strip(t),'url':urllib.parse.urljoin(final,html.unescape(u))} for u,t in re.findall(r'<a[^>]+href=[\"\x27]([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>',s,re.S|re.I)]
        (OUT/(key+'.txt')).write_text(text,encoding='utf-8')
        metadata={'id':key,'url':final,'chars':len(text),'links':links}
        (OUT/(key+'.json')).write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
        if key.startswith('search'):
            hits=[]
            for link in links:
                if 'uddg=' in link['url']:
                    u=urllib.parse.parse_qs(urllib.parse.urlparse(link['url']).query).get('uddg',[''])[0]
                    if u and not any(h['url']==u for h in hits):hits.append({'url':u,'title':link['text']})
            return {'id':key,'results':hits[:8]}
        return {'id':key,'url':final,'chars':len(text),'text':text[:2200] if len(text)<16000 else text[:300], 'links':[l for l in links if re.search(r'pdf|下载|附件|框|坡|10001|10621|3362',l['url']+' '+l['text'],re.I)][:20]}
    except Exception as e:return {'id':key,'error':str(e)}
if __name__=='__main__':
    items=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
    with ThreadPoolExecutor(max_workers=5) as pool:
        for result in pool.map(fetch,items.items()):print(json.dumps(result,ensure_ascii=False),flush=True)
