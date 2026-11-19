"""Append-only historical component-completeness audit; never rewrite trials."""
import argparse,json,re
from pathlib import Path
from skin_load_assess import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name in a.cases:
  src=BASE/'results'/name;m=json.loads((src/'summary.json').read_text());messages=[]
  for file in (src/'process/stdout.log',src/'process/stderr.log'):messages.extend(re.findall(r'Element Intersector[^\n]*NOT FOUND',file.read_text(errors='replace')))
  records.append(dict(case=name,preserved_original_status=m['status'],contact_geometry_gate='INVALID_CONTACT_COMPONENT_COMBINATION' if messages else 'NO_MISSING_INTERSECTOR_MESSAGE_ONLY',messages=messages,input_hashes={f.name:sha(f) for f in (src/'summary.json',src/'process/stdout.log',src/'process/stderr.log')},scope='no warning is not sufficient contact certification;missing sphere/mesh methods invalidate Skin-contact absence as mechanism evidence'))
 result=dict(scope='historical log audit,not new physics or overwritten verdict',records=records,source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
