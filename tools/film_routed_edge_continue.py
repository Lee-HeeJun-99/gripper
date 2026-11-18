"""Actual/material-edge standalone continuation of qualified routed V2 state."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
TAIL=r'''
 if(argc!=4||std::string(argv[3]).rfind("cont",0)!=0)throw std::runtime_error("explicit continuation count required");unsigned steps=std::stoul(std::string(argv[3]).substr(4));if(steps!=2&&steps!=4&&steps!=8)throw std::runtime_error("bounded2/4/8 steps only");
 if(std::ifstream(argv[2]))throw std::runtime_error("output exists");std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time,minimum_gap,momentum,normal_velocity,U_shell,U_attachment,K,T,force,q,v\n";
 for(unsigned k=0;k<steps;++k){auto r=regrip_collocation::persistentRows(s.shared.M,2,q,v,time,h,force,[&](const auto&x){return edgeGeometry(s,x,edges);});double gap=s.clearance(r.q);for(const auto&stage:r.stages)gap=std::min(gap,s.clearance(stage.q));if(gap< -1e-10)throw std::runtime_error("whole stage clearance fails");q=r.q;v=r.v;time+=h;double shell=0,bond=0;
  for(unsigned f=0;f<3;++f){auto local=s.local(q,f);s.shared.films[f].film.model.elements(local.q,0,[&](const Element&e){if(e.kind==0)shell+=e.energy.v;else if(e.kind==1)bond+=e.energy.v;});}
  out<<time<<','<<gap<<','<<r.momentumResidual<<','<<r.velocityResidual<<','<<shell<<','<<bond<<','<<.5*v.dot(s.shared.M*v)<<','<<regrip_film_rail::ControlProfile::evaluate(time,.0001,.01,.02,.03,true).tension;
  for(const auto*x:{&r.stages.back().force,&q,&v}){out<<',';for(int i=0;i<x->size();++i)out<<(i?" ":"")<<(*x)[i];}out<<'\n';out.flush();
 }
 std::cout<<"PASS bounded routed material-edge standalone continuation;NOT actual/time/grasp certificate\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(2,4,6,8),default=2);p.add_argument('--reference',action='store_true');p.add_argument('--parent',default='20261118_routed_edge_actual1336');p.add_argument('--checkpoint-step',type=int,default=127);p.add_argument('--qualification');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((src/'summary.json').read_text());checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt';provider=ROOT/'results/autonomous_film_20261118_routed_edge_actual1336';pm=json.loads((provider/'summary.json').read_text())
 if m['status'] not in ('PASS','EXPERIMENTAL') or m['process']['exit_code'] or m['sofa_errors'] or sha(checkpoint)!=m['raw_hashes'][checkpoint.name] or m['binary_sha256']!=pm['binary_sha256']:raise ValueError('qualified actual routed material-edge checkpoint required')
 if m['status']=='EXPERIMENTAL':
  qual=ROOT/'results'/('autonomous_film_'+a.qualification);qm=json.loads((qual/'summary.json').read_text())
  if qm['status']!='PASS' or qm['actual_summary_sha256']!=sha(src/'summary.json'):raise ValueError('strict finite actual API qualification required')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('actual source archive changed')
 if sha(src/'scene.scn')!=m['scene_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=m['sdk_runner_sha256']:raise ValueError('actual scene/SDK changed')
 tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2]);end=time
 if tokens[0]!='REGRIP_ROUTED_EDGE_V2' or tokens[4]!=m['identity'] or dt!=.0002:raise ValueError('route-bound material-edge physical schema required')
 for i in range(a.steps):end+=dt
 if end>.03:raise ValueError('bounded C2 interval')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');profile=ROOT/'results/autonomous_film_20261118_routed_unload_begin1307';cost=json.loads((profile/'summary.json').read_text());forecast=2*cost['process']['runtime_s']*a.steps/cost['actual_steps']+30;r=dict(status='BLOCKED',scope='routed material-edge finite continuation;NOT full Unload/release/time/energy/wrapping/grasp',reference=a.reference,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),parent_summary_sha256=sha(src/'summary.json'),input_checkpoint_sha256=sha(checkpoint),start_time_s=time,dt_s=dt,actual_steps=a.steps,expected_end_time_s=end,predicted_child_runtime_s=forecast,cost_profile_summary_sha256=sha(profile/'summary.json'),root_reaction_work=None,legacy_sampled_work='NOT restored;excluded')
 if forecast>480:r['failure_reason']='measured conditional geometry profile forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 if a.reference:
  archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/RoutedEdgeContinuation.cpp';cpp.parent.mkdir(parents=True);original=ROOT/'diagnostics/film_three_finger/EdgeRelease.cpp';text=original.read_text();anchor=' if(argc==4&&std::string(argv[3]).rfind("ac",0)==0){'
  if text.count(anchor)!=1:raise ValueError('existing edge loader boundary differs')
  text=text.split(anchor)[0]
  if text.count('"REGRIP_EDGE_V2"')!=1:raise ValueError('existing loader schema differs')
  cpp.write_text(text.replace('"REGRIP_EDGE_V2"','"REGRIP_ROUTED_EDGE_V2"')+TAIL.replace('steps!=2&&steps!=4&&steps!=8','steps!=2&&steps!=4&&steps!=6&&steps!=8'));compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'input.checkpoint',out/'states.csv','cont'+str(a.steps)],out/'process',480) if compile['exit_code']==0 else None;r.update(status='FAIL',compile=compile,process=run,source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
  if (out/'reference').exists():r['binary_sha256']=sha(out/'reference')
  if run and run['exit_code']==0:
   rows=list(csv.DictReader((out/'states.csv').open()));r.update(status='PASS' if len(rows)==a.steps else 'FAIL',end_time_s=float(rows[-1]['time']))
  if run and run['exit_code']!=0:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 else:
  tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmFaceEdgeODE')
  if owner is None:owner=scene.find('RoutedThreeFilmEdgeODE')
  if owner is None:raise ValueError('qualified material-edge Scene owner missing')
  owner.tag='RoutedThreeFilmEdgeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(end,'.17g'));binary=ROOT/pm['build_relative']/'libReGripThreeFilmPrimitive.so'
  if sha(binary)!=m['binary_sha256']:raise ValueError('qualified executable changed')
  for node in scene.iter():
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
  tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);r.update(status='FAIL',process=run,sofa_errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log')),binary_sha256=sha(binary),identity=m['identity'],scene_sha256=sha(out/'scene.scn'),sdk=str(SDK),sdk_runner_sha256=m['sdk_runner_sha256'])
  if run['exit_code']==0 and not r['sofa_errors']:
   rows=list(csv.DictReader((out/'three.states.csv').open()));clock=time;exact=True
   for row in rows:clock+=dt;exact=exact and float(row['time'])==clock
   gap=min(float(x['minimum_gap']) for x in rows);momentum=max(float(x['momentum_residual']) for x in rows);vn=max(float(x['normal_velocity_residual']) for x in rows);r.update(status='EXPERIMENTAL' if len(rows)==a.steps and exact and gap>=-1e-10 and momentum<=1e-17 and vn<=1e-10 else 'FAIL',accumulated_clock_exact=exact,end_time_s=clock,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=momentum,normal_velocity_residual_mm_s=vn)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
