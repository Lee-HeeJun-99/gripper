"""Passive same-binary Gauss4 failure journal; no additional force queries."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded

HOOK=r'''
std::ofstream diagnostic;
if(argc>8){diagnostic.open(argv[8]);diagnostic<<std::setprecision(17)<<"time,h,iteration,cut,alpha,residual,trial_residual,linear_residual,delta_norm,unchanged_components,directional_derivative\n";
 regrip_c2_startup::newtonObserver=[&](const regrip_c2_startup::NewtonTrial& z){
 auto linear=z.tangent*z.delta+z.residual;
 diagnostic<<z.time<<','<<z.h<<','<<z.iteration<<','<<z.cut<<','<<z.alpha<<','<<z.residual.norm()<<','<<z.trialResidual.norm()<<','<<linear.norm()<<','<<z.delta.norm()<<','<<(z.state.array()==z.trial.array()).count()<<','<<z.residual.dot(z.tangent*z.delta)<<'\n';diagnostic.flush();
 if(z.cut==15){std::ofstream matrix(std::string(argv[8])+".matrix.csv"),vectors(std::string(argv[8])+".vectors.csv");matrix<<std::setprecision(17)<<"row,col,value\n";vectors<<std::setprecision(17)<<"state,residual,delta,trial,trial_residual\n";
 for(int i=0;i<z.state.size();++i){vectors<<z.state(i)<<','<<z.residual(i)<<','<<z.delta(i)<<','<<z.trial(i)<<','<<z.trialResidual(i)<<'\n';for(int j=0;j<z.state.size();++j)if(z.tangent(i,j)!=0)matrix<<i<<','<<j<<','<<z.tangent(i,j)<<'\n';}}
 };}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--increment',action='store_true');p.add_argument('--extended',action='store_true');p.add_argument('--only-window',action='store_true');a=p.parse_args()
 provider=ROOT/'results/autonomous_film_20261119_precise_tendon_gauss1715';old=json.loads((provider/'summary.json').read_text())
 for f,d in old['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('immutable source mismatch')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(provider/'sources',out/'sources');shutil.copy2(provider/'public_mass.txt',out/'public_mass.txt')
 shutil.copy2(ROOT/'models/film_c2_startup/Gauss4.h',out/'sources/models/film_c2_startup/Gauss4.h')
 cpp=out/'sources/diagnostics/film_three_finger/Gauss4Probe.cpp';code=cpp.read_text();needle='try{using namespace regrip_transmission;'
 if code.count(needle)!=1:raise ValueError('exact frozen driver required')
 code=code.replace(needle,'try{'+HOOK+'using namespace regrip_transmission;')
 if a.increment:
  if code.count('fd&&k==0,tolerance)')!=1:raise ValueError('exact increment call adapter required')
  code=code.replace('fd&&k==0,tolerance)','fd&&k==0,tolerance,true)')
 if a.extended:
  shutil.copytree(ROOT/'models/film_extended_precision',out/'sources/models/film_extended_precision')
  for name in ('AD.h','MembraneAD.h'):shutil.copy2(ROOT/'models/film_shell'/name,out/'sources/models/film_shell'/name)
  # Unused contact helpers are transitively parsed by the free-coupon map.
  # Keep their public double geometry outputs explicit in this private build;
  # this does NOT qualify extended-precision contact or modify original SDK.
  for filename,before,after in (
   ('film_impact/SurfaceEvent.h','std::min(result.advance,e.gap.v/path.triangleSpeedBound(t,a))','std::min(result.advance,double(e.gap.v/path.triangleSpeedBound(t,a)))'),
   ('film_impact/WholeSurfaceMidpoint.h','std::min(out.minimumGap,regrip_film_sphere::ClosestPrimitive::evaluate(p,center,radius).gap.v)','std::min(out.minimumGap,double(regrip_film_sphere::ClosestPrimitive::evaluate(p,center,radius).gap.v))'),
   ('film_coupled_contact/CoupledSphere.h','std::min(g,primitive(s,i).gap.v)','std::min(g,double(primitive(s,i).gap.v))')):
   target=out/'sources/models'/filename;content=target.read_text()
   if content.count(before)!=1:raise ValueError('exact unused helper compatibility adapter required')
   target.write_text(content.replace(before,after))
  code=code.replace('film_precise_tendon/Force.h','film_extended_precision/Force.h').replace('regrip_precise_tendon::parts','regrip_extended_precision::parts')
 code=code.replace('for(unsigned k=0;k<substeps;++k){','std::ofstream accepted(std::string(argv[3])+".accepted.csv");accepted<<std::setprecision(17)<<"time,q,v\\n";for(unsigned k=0;k<substeps;++k){')
 code=code.replace('clock+=h;q=map.expand(r.q);v=map.expand(r.v);','clock+=h;q=map.expand(r.q);v=map.expand(r.v);accepted<<clock;quote(accepted,q);quote(accepted,v);accepted<<\'\\n\';accepted.flush();')
 cpp.write_text(code)
 r=dict(status='INCOMPLETE',increment_stage_variables=a.increment,extended_AD_and_assembly=a.extended,scope='independent Newton arithmetic candidate ONLY;NOT actual SOFA or convergence certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},trials={})
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off',*(['-DREGRIP_FILM_EXTENDED_AD'] if a.extended else []),'-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']!=0:write_json(out/'summary.json',r);return
 r['binary_sha256']=sha(out/'reference')
 cases=[('failure','.001',40)] if a.only_window else [('startup','.0002',8),('failure','.001',40)]
 for label,finish,count in cases:
  for enabled in (False,True):
   name=label+('_on' if enabled else '_off');folder=out/name;folder.mkdir();command=[out/'reference','fem',out/'public_mass.txt',folder/'state.csv',finish,str(count),'1e-24','plain']
   if enabled:command.append(folder/'trials.csv')
   r['trials'][name]=guarded(command,folder/'process',480);write_json(out/'progress.json',r)
 r['purity']={label:{suffix:sha(out/(label+'_on')/('state.csv'+suffix))==sha(out/(label+'_off')/('state.csv'+suffix)) for suffix in ('','.stages.csv','.newton.csv')} for label,_,_ in cases}
 rows=list(csv.DictReader((out/'failure_on/trials.csv').open()));last=rows[-1];r['last_trial']=last
 r['status']='PASS' if all(all(x.values()) for x in r['purity'].values()) and all(r['trials'][label+'_on']['exit_code']==0 for label,_,_ in cases if label=='startup') and r['trials']['failure_on']['exit_code']==(0 if a.increment or a.extended else 1) else 'FAIL'
 r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in out.rglob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','trials','compile')}))
if __name__=='__main__':main()
