"""Actual stored-stage F/H and geometry derivative parity,not just positions."""
import argparse,csv,json,re,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();actual=ROOT/'results/autonomous_film_20261118_routed_unload_begin1307';am=json.loads((actual/'summary.json').read_text());cache=ROOT/'results/autonomous_film_20261118_precise_cache_build1340';cm=json.loads((cache/'summary.json').read_text());base=ROOT/'results/autonomous_film_20261118_routed_resume1278';bm=json.loads((base/'summary.json').read_text())
 if cm['status']!='PASS' or bm['status']!='PASS' or am['process']['exit_code'] or am['sofa_errors']:raise ValueError('qualified original/candidate compilation and complete actual samples required')
 for path,meta in ((base,bm),(cache,cm)):
  for f,d in meta['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('compiled source archive changed')
 if sha(actual/'three.rows.csv')!=am['raw_hashes']['three.rows.csv']:raise ValueError('actual stored query states changed')
 rows=list(csv.DictReader((actual/'three.rows.csv').open()));samples=[];seen=set()
 if len(rows)!=72:raise ValueError('all8macro actual stage rows required')
 for i in range(0,len(rows),3):
  group=rows[i:i+3];r=group[0]
  if any((x['time'],x['stage_q'])!=(r['time'],r['stage_q']) for x in group):raise ValueError('rows do not share actual stage state')
  key=(r['time'],r['stage_q'])
  if key not in seen:samples.append(key);seen.add(key)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(cache/'sources/models',archive/'models');path=archive/'models/film_three_finger/SharedFilmSystem.h';candidate=path.read_text()
 if len(re.findall(r'\bSharedFilmSystem\b',candidate))!=2:raise ValueError('pure diagnostic class rename anchors differ')
 (path.parent/'CachedSharedFilmSystem.h').write_text(re.sub(r'\bSharedFilmSystem\b','CachedSharedFilmSystem',candidate));shutil.copy2(base/'sources/models/film_three_finger/SharedFilmSystem.h',path);cpp=archive/'diagnostics/film_three_finger/PreciseCacheParity.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/PreciseCacheParity.cpp',cpp);(out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(t+' '+q for t,q in samples)+'\n');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'test'],out/'compile',120);run=guarded([out/'test',out/'samples.txt'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='direct F/H/gap/J/contact-H/query-purity parity on stored actual stages ONLY;NOT universal time/grasp qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(actual/'summary.json'),actual_rows_sha256=sha(actual/'three.rows.csv'),cache_build_summary_sha256=sha(cache/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},samples_sha256=sha(out/'samples.txt'),compile=compile,process=run,sdk='NOT used for standalone algebra;actual input has installed-SDK provenance')
 if (out/'test').exists():r['binary_sha256']=sha(out/'test')
 if run and run['exit_code']==0:r.update(json.loads((out/'process/stdout.log').read_text()))
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
