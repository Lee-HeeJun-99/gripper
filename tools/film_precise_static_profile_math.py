"""Original FD/objectivity/balance gates for independent static profile combination."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--outboard',type=float,choices=(6.,8.,10.),default=6.);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_precise_static_potential1746';sm=json.loads((src/'summary.json').read_text())
 for f,d in sm['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('qualified force sources changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');shutil.copy2(ROOT/'models/film_precise_static/Profiled.h',out/'sources/models/film_precise_static/Profiled.h');tests=out/'sources/tests';tests.mkdir();original=ROOT/'tests/test_film_lateral.cpp';shutil.copy2(original,tests/'original_test_film_lateral.cpp');code=original.read_text().replace('film_lateral_tendon/Route.h','film_precise_static/Profiled.h')
 code=code.replace('if(original)m.elements(q,.001,visit);else elements(m,q,.001,lateral,visit);','if(original)regrip_precise_tendon::elements(m,q,.001,6.,visit);else regrip_precise_static_profile::elements(m,q,.001,lateral,visit);').replace('for(double lateral:{0.,6.})','for(double lateral:{0.,.5,4.5})').replace('if(length(m,q,0)!=m.cableLength(q))','if(regrip_precise_static_profile::route(m,q,0,0,[](const Element&){})!=regrip_precise_tendon::route(m,q,0,6.,[](const Element&){}))')
 original_profile=ROOT/'results/autonomous_film_20261118_profiled_math1431';pm=json.loads((original_profile/'summary.json').read_text());source=original_profile/'sources/models/film_profiled_tendon'
 if pm['status']!='PASS' or sha(source/'Route.h')!=pm['source_hashes']['models/film_profiled_tendon/Route.h']:raise ValueError('qualified original guide geometry required')
 shutil.copytree(source,out/'sources/models/film_profiled_tendon')
 if a.outboard!=6:
  code=code.replace('for(double lateral:{0.,.5,4.5})','for(double lateral:{.5,4.5})').replace('regrip_precise_static_profile::elements(m,q,.001,lateral,visit)','regrip_precise_static_profile::elements(m,q,.001,lateral,visit,'+str(a.outboard)+')')
 cpp=tests/'profile.generated.cpp';cpp.write_text(code);r=dict(status='FAIL',scope='original force/Hessian FD,rigid objectivity,nodal force/moment balance'+(' and zero-amplitude parity' if a.outboard==6 else ';zero-amplitude parity NOT MEASURED for changed'+str(a.outboard)+'mm route')+' ONLY;NOT SOFA/contact/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},outboard_mm=a.outboard,amplitudes_mm=[0,.5,4.5] if a.outboard==6 else [.5,4.5],old_profile_scope='existing .5mm route reuse;its old free50ms worse-arch outcome is NOT revoked',physical_model='precise shell/bond plus existing objective profiled guide geometry;constant T;new independent static domain',selected_design=None)
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'test'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'test');r['process']=guarded([out/'test'],out/'process',180)
  if r['process']['exit_code']==0:
   r.update(status='PASS',metrics=json.loads((out/'process/stdout.log').read_text()))
   if a.outboard!=6:r['metrics']['baseline_F_H_E_max_abs']=None;r['baseline_note']='Unvisited initialized harness counter in raw output is not a physical baseline measurement;changed outboard design has no old identical baseline.'
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
