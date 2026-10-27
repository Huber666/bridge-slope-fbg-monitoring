"""Fetch primary-source pages for local evidence review; full texts stay in ignored QA."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, re, urllib.request, html
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'_qa'/'sources'
URLS={
'USGS_types':'https://pubs.usgs.gov/fs/2004/3072/',
'USGS_signs':'https://www.usgs.gov/programs/landslide-hazards/what-are-signs-landslide-development-what-do-i-do-if-a-landslide-occurs',
'Schenato2017':'https://www.nature.com/articles/s41598-017-12610-1',
'FBG_slope2016':'https://pmc.ncbi.nlm.nih.gov/articles/PMC5038695/',
'Zhu2017':'https://www.mdpi.com/1424-8220/17/3/452',
'Sun2017':'https://www.mdpi.com/1424-8220/17/3/597',
'Bastianini2019':'https://www.mdpi.com/1424-8220/19/23/5172',
'Fang2012':'https://nhess.copernicus.org/articles/12/527/2012/',
'Drusa2021':'https://www.mdpi.com/1424-8220/21/19/6404',
'Zhao2021':'https://www.frontiersin.org/journals/earth-science/articles/10.3389/feart.2021.660918/full',
'Gao2019':'https://doi.org/10.1049/joe.2019.0777',
'Zhang2019':'https://www.mdpi.com/1424-8220/19/7/1591'
}
DOIS=['10.3390/s17030452','10.3390/s17030597','10.3390/s19235172','10.3390/s21196404','10.3390/s19071591','10.3390/s22249685','10.3390/s26020742','10.1038/s41598-026-46115-7','10.1007/s10064-025-04237-8']
def fetch(item):
 key,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=35) as r:
   status=r.status; final_url=r.url; raw=r.read().decode('utf-8',errors='replace')
  titles=re.findall(r'<title[^>]*>(.*?)</title>',raw,re.S)
  stripped=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',raw,flags=re.S|re.I)
  txt=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',stripped)))
  OUT.mkdir(parents=True,exist_ok=True)
  (OUT/(key+'.txt')).write_text(txt,encoding='utf-8')
  positions=[m.start() for m in re.finditer(r'Abstract|ABSTRACT|Early detection|Conclusion|Conclusions|warning signs|Types of Landslides',txt)]
  return {'id':key,'status':status,'url':final_url,'length':len(txt),'title':titles[0] if titles else '', 'extracts':[txt[max(0,p-60):p+3000] for p in positions[:4]]}
 except Exception as e:return {'id':key,'error':str(e)}
if __name__=='__main__':
 for doi in DOIS:
  try:
   from urllib.parse import quote
   u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+quote('DOI:'+doi)+'&format=json'
   with urllib.request.urlopen(u,timeout=20) as r:data=json.loads(r.read())
   entries=data.get('resultList',{}).get('result',[])
   print(json.dumps({'doi':doi,'metadata':entries},ensure_ascii=False),flush=True)
   if entries and entries[0].get('pmcid'):
    URLS[doi.replace('/','_')]='https://www.ebi.ac.uk/europepmc/webservices/rest/'+entries[0]['pmcid']+'/fullTextXML'
  except Exception as e:print(json.dumps({'doi':doi,'error':str(e)}),flush=True)
 URLS['USGS_types_full']='https://pubs.usgs.gov/fs/2004/3072/fs-2004-3072.html'
 URLS['search_internal_erosion']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=TITLE_ABS%3A%28%22internal%20erosion%22%20AND%20%22fiber%22%29&format=json'
 with ThreadPoolExecutor(max_workers=6) as pool:
  for item in pool.map(fetch,URLS.items()):print(json.dumps(item,ensure_ascii=False),flush=True)
