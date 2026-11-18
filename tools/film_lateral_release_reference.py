"""Existing bounded release composition on actual lateral27ms state."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_routed_release_reference import TAIL
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--grid',type=int,choices=(32,64,128),default=32);p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_lateral_to270_actual1509';m=json.loads((src/'summary.json').read_text());checkpoint=src/'three.checkpoint_135.txt'
 if m['status']!='PASS' or sha(checkpoint)!=m['raw_hashes'][checkpoint.name]:raise ValueError('strict actual lateral27ms checkpoint required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('actual source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);loader=(ROOT/'diagnostics/film_three_finger/RoutedCheckpoint.h').read_text().replace('REGRIP_ROUTED_PERSISTENT_V1','REGRIP_LATERAL_CONTROLLED_V1');(diag/'RoutedCheckpoint.h').write_text(loader)
 path=archive/'models/film_routed_contact/AdmissibleRelease.h';text=path.read_text()
 if text.count('time<.027||')!=1:raise ValueError('existing bounded release fixture anchor differs')
 path.write_text(text.replace('time<.027||','time<.0269||time>.0271||'))
 preamble='''#include "RoutedCheckpoint.h"
#include "../../models/film_routed_contact/AdmissibleRelease.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_resume;
int main(int argc,char**argv){try{
 SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double time,h;regrip_routed_checkpoint::read(argv[1],s,q,v,time,h);std::vector<EdgeOwner>edges;
 for(unsigned f=0;f<3;++f){auto row=s.selected(q,f);if(row.triangle!=116||row.feature!=5)throw std::runtime_error("actual canonical edge fixture differs");auto tri=s.shared.films[f].triangles[row.triangle];edges.push_back({f,row.triangle,{tri[1],tri[2]}});}
 auto selected=s.geometry(q),owned=edgeGeometry(s,q,edges);if((selected.gap-owned.gap).cwiseAbs().maxCoeff()>1e-12||(selected.J-owned.J).cwiseAbs().maxCoeff()>1e-12)throw std::runtime_error("canonical material-edge pullback differs");
'''
 cpp=diag/'LateralRelease.cpp';cpp.write_text(preamble+TAIL);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};forecast=None
 if a.reuse:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse);pr=json.loads((previous/'summary.json').read_text())
  if pr['source_hashes']!=sources or pr['input_checkpoint_sha256']!=sha(checkpoint) or sha(previous/'reference')!=pr['binary_sha256']:raise ValueError('exact compiled-source/input release reuse required')
  if pr['status']=='PASS':forecast=2*(pr['root_seconds']+pr['free_seconds']+pr['rk_seconds']*a.grid/pr['grid'])+30
  elif pr['status']=='FAIL' and a.grid==2*pr['grid'] and pr.get('failure_reason','').startswith('positive acceleration reaction outside touching tangent state;'):
   old=json.loads((ROOT/'results/autonomous_film_20261118_three_film_acc_local1075/summary.json').read_text())
   if old['status']!='PASS' or old['acc_grid']!=64:raise ValueError('completed conditional64-grid cost reference required')
   forecast=2*(pr['process']['runtime_s']+old['run']['runtime_s']*a.grid/64)+30
  else:raise ValueError('reuse is not a valid physical/runtime qualification')
  shutil.copy2(previous/'reference',out/'reference');compile=dict(exit_code=0,reused_from=a.reuse)
 else:
  if a.grid!=32:raise ValueError('initial measured grid32 required')
  compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 r=dict(status='BLOCKED',scope='existing numerical release composition on actual lateral27ms IVP;NOT actual SOFA/full time/energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,input_checkpoint_sha256=sha(checkpoint),parent_summary_sha256=sha(src/'summary.json'),grid=a.grid,compile=compile,predicted_child_runtime_s=forecast,fixture_change='explicit27ms window admits actual accumulated .026999999999999948;clock NEVER rounded/reset',edge_history='current exact material nodes only;no invented birth time/history',root_work=None,release_time='collocation admissibility bracket/RK stage times,NOT certified continuous exit root',momentum_metric='sum of segment residual norms;NOT independent global vector defect')
 if forecast and forecast>480:r['failure_reason']='measured policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 run=guarded([out/'reference',out/'input.checkpoint',out/'states.csv',str(a.grid)],out/'process',480) if compile['exit_code']==0 else None;r.update(status='FAIL',process=run)
 if (out/'reference').exists():r['binary_sha256']=sha(out/'reference')
 if run and run['exit_code']==0:r.update(json.loads((out/'process/stdout.log').read_text()))
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.glob('states.csv*')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
