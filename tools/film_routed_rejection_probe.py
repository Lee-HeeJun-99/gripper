"""Minimal next-step diagnostic from matched accepted prefix of FAILED1312/13.
No parent horizon is relabelled PASS and no rejected state is committed.
"""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();actual=ROOT/'results/autonomous_film_20261118_routed_unload_to2761312';ref=ROOT/'results/autonomous_film_20261118_routed_unload_to276_reference1313';m=json.loads((actual/'summary.json').read_text());r=json.loads((ref/'summary.json').read_text());checkpoint=actual/'three.checkpoint_121.txt'
 if m['status']!='FAIL' or r['status']!='FAIL' or sha(checkpoint)!=m['raw_hashes'][checkpoint.name] or 'persistent rows endpoint drift;no projection' not in (ref/'process/stderr.log').read_text():raise ValueError('preserved failed horizon and exact accepted checkpoint required')
 for f,d in m['raw_hashes'].items():
  if sha(actual/f)!=d:raise ValueError('failed actual raw changed')
 x=list(csv.DictReader((actual/'three.states.csv').open()));y=list(csv.DictReader((ref/'states.csv').open()));tokens=checkpoint.read_text().split();n=1953
 if len(x)!=15 or len(y)!=15 or tokens[0]!='REGRIP_ROUTED_PERSISTENT_V1' or float(tokens[1])!=float(x[-1]['time']):raise ValueError('expected matched15-step accepted prefix absent')
 for i,j in zip(x,y):
  if i['time']!=j['time'] or any(not np.array_equal(np.fromstring(i[k],sep=' '),np.fromstring(j[k],sep=' ')) for k in ('q','v')):raise ValueError('accepted actual/reference prefix differs')
 for k,start in (('q',5),('v',5+n)):
  if not np.array_equal(np.array(tokens[start:start+n],float),np.fromstring(x[-1][k],sep=' ')):raise ValueError('checkpoint is not actual last accepted state')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');shutil.copytree(ref/'sources',out/'sources');cpp=out/'sources/diagnostics/film_three_finger/RoutedHoldReference.cpp';text=cpp.read_text();anchor='return g;});'
 if text.count(anchor)!=1:raise ValueError('rejected-state observer anchor differs')
 callback='''return g;},false,[&](const auto&r){std::ofstream reject(std::string(argv[4])+".rejected.csv");reject<<std::setprecision(17)<<"state,time,h,finger,triangle,feature,gap,normal_velocity,force\\n";for(unsigned which=0;which<3;++which){const auto&z=which?r.stages[which-1].q:q;const auto&vel=which?r.stages[which-1].v:v;auto geo=s.geometry(z);for(unsigned f=0;f<3;++f){auto row=s.selected(z,f);reject<<(which==0?"initial":which==1?"mid":"rejected_end")<<','<<time+h*(which==0?0:which==1?.5:1)<<','<<h<<','<<f<<','<<row.triangle<<','<<row.feature<<','<<geo.gap[f]<<','<<geo.J.row(f).dot(vel)<<','<<(which?r.stages[which-1].force[f]:r.initialForce[f])<<'\\n';}}});'''
 cpp.write_text(text.replace(anchor,callback));sources={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()};compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'input.checkpoint','8','1',out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None;observed=out/'states.csv.rejected.csv'
 result=dict(status='EXPERIMENTAL' if observed.exists() and run and run['exit_code']!=0 else 'FAIL',scope='read-only rejected-next-step diagnostic,EXACT accepted15-step prefix only;parents1312/1313/full horizon remain FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(actual/'summary.json'),reference_summary_sha256=sha(ref/'summary.json'),accepted_prefix_states=15,accepted_prefix_qv_time_exact=True,source_checkpoint_sha256=sha(checkpoint),reference_prefix_observed_sha256=sha(ref/'states.csv'),source_hashes=sources,compile=compile,process=run,rejected_state_committed=False,full_time_gate='FAIL remains')
 if observed.exists():result.update(rejected_rows=list(csv.DictReader(observed.open())),rejected_csv_sha256=sha(observed),binary_sha256=sha(out/'reference'))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
