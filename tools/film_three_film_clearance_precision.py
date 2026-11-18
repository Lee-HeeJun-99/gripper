"""Inspect exactly stored geometry at a failed parent's ACCEPTED prefix checkpoint.
This is not a completed SOFA trial or permission to change old results.
"""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--step',type=int,required=True);p.add_argument('--midpoint',action='store_true');p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text());checkpoint=src/f'three.checkpoint_{a.step}.txt'
 if sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('actual accepted checkpoint changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint')
 if a.midpoint:
  rows=list(csv.DictReader((src/'three.rows.csv').open()));group=rows[-6:-3];r=group[0]
  if len(group)!=3 or any(x['stage_q']!=r['stage_q'] or x['stage_v']!=r['stage_v'] for x in group):raise ValueError('missing actual midpoint stage')
  tokens=(out/'input.checkpoint').read_text().split();tokens[1]=r['time'];tokens[5:1958]=r['stage_q'].split();tokens[1958:3911]=r['stage_v'].split();(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
 archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/ClearancePrecision.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/ClearancePrecision.cpp',cpp);binary=out/'reference'
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((prior/'summary.json').read_text());binary=prior/'reference'
  for n,h in proof['sources'].items():
   if (n.endswith('.h') or n.endswith('ClearancePrecision.cpp')) and sha(archive/n)!=h:raise ValueError('compiled geometry code changed')
  if sha(binary)!=proof['binary_sha256']:raise ValueError('geometry binary changed')
  compile=dict(exit_code=0,reused=a.reuse)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'input.checkpoint',out/'geometry.csv'],out/'run',120) if compile['exit_code']==0 else None;result=dict(status='FAIL',scope='independent334-bit entire-triangle distance audit of actual '+('MIDPOINT STAGE,not accepted endpoint' if a.midpoint else 'accepted endpoint')+';NOT new SOFA continuation/PASS of failed parent',parent_status=meta['status'],checkpoint_sha256=sha(checkpoint),diagnostic_input_sha256=sha(out/'input.checkpoint'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,run=run)
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'geometry.csv').open()));worst=min(rows,key=lambda r:float(r['AD_gap_mm']));precise=min(rows,key=lambda r:float(r['high_precision_gap_mm']));selected=[r for r in rows if r['selected']=='1'];compact=lambda r:{k:v for k,v in r.items() if k!='coordinates'};error=max(abs(float(r['AD_gap_mm'])-float(r['high_precision_gap_mm'])) for r in rows);result.update(status='PASS',meaning='inspection completed,NOT physics gate',triangles=len(rows),worst_AD=compact(worst),worst_high_precision=compact(precise),selected=[compact(r) for r in selected],max_AD_value_error_mm=error,binary_sha256=sha(binary),geometry_sha256=sha(out/'geometry.csv'))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run')}))
if __name__=='__main__':main()
