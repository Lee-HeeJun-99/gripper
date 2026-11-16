"""Byte identity of completed physical journals, not numerical qualification."""
import argparse,json
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=2,required=True);a=p.parse_args()
    roots=[ROOT/'results'/('autonomous_film_'+name) for name in a.cases]
    for root in roots:
        result=json.loads((root/'summary.json').read_text())
        if result.get('status')!='PASS' or not result.get('finite'):raise ValueError('completed finite trajectories required')
    files={}
    for name in ('journal.csv','contact.csv','contact_rows.csv','momentum.csv','coupled.csv'):
        pair=[root/'1'/name for root in roots];hashes=[sha(path) for path in pair]
        files[name]=dict(identical=hashes[0]==hashes[1],sha256=hashes)
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    result=dict(status='PASS' if all(x['identical'] for x in files.values()) else 'FAIL',scope='physical-journal byte identity only;NOT physical certification',cases=a.cases,files=files,script_sha256=sha(__file__))
    write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
