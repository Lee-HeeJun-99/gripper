"""Bounded admissible Lobatto→existing acceleration-LCP→free midpoint."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
TAIL=r'''
 if(argc!=4)throw std::runtime_error("grid required");unsigned grid=std::stoul(argv[3]);auto r=regrip_routed_release::resolve(s,q,v,time,h,edges,grid);
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time,minimum_gap_mm,momentum_bound_Ns,minimum_force_N,final_mask,outgoing_normal_velocity_mm_s,q,v\n"<<time+h<<','<<r.minimumGap<<','<<r.momentumBound<<','<<r.minimumForce<<",0,"<<r.outgoing<<','<<r.after.q.transpose()<<','<<r.after.v.transpose()<<'\n';
 std::ofstream stages(std::string(argv[2])+".rk.csv");stages<<std::setprecision(17)<<"time,weight_s,mask,force,q,v\n";double firstFree=-1,lastActive=-1;
 for(const auto&z:r.release.stages){stages<<z.time<<','<<z.weight<<','<<z.mask<<','<<z.force.transpose()<<','<<z.q.transpose()<<','<<z.v.transpose()<<'\n';if(z.mask==0&&firstFree<0)firstFree=z.time;if(z.mask!=0)lastActive=z.time;}
 std::cout<<std::setprecision(17)<<"{\"status\":\"PASS\",\"pre_h_s\":"<<r.preH<<",\"admissible_root_lo_s\":"<<r.rootLo<<",\"admissible_root_hi_s\":"<<r.rootHi<<",\"root_evaluations\":"<<r.rootEvaluations<<",\"RK_stages\":"<<r.release.stages.size()<<",\"last_active_STAGE_time_s\":"<<lastActive<<",\"first_all_free_STAGE_time_s\":"<<firstFree<<",\"actual_RK_end_time_s\":"<<r.release.endTime<<",\"end_time_s\":"<<time+h<<",\"minimum_gap_mm\":"<<r.minimumGap<<",\"outgoing_normal_velocity_mm_s\":"<<r.outgoing<<",\"momentum_bound_Ns\":"<<r.momentumBound<<",\"root_seconds\":"<<r.rootSeconds<<",\"rk_seconds\":"<<r.rkSeconds<<",\"free_seconds\":"<<r.freeSeconds<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--grid',type=int,choices=(16,32,64,128),default=32);p.add_argument('--reuse');p.add_argument('--reuse-failed-profile',action='store_true');a=p.parse_args();prefix=ROOT/'results/autonomous_film_20261118_routed_release_prefix1349';pm=json.loads((prefix/'summary.json').read_text());checkpoint=prefix/'input.checkpoint'
 if pm['status']!='EXPERIMENTAL' or not pm['accepted_prefix_qv_time_exact'] or sha(checkpoint)!=pm['source_checkpoint_sha256']:raise ValueError('exact accepted prefix of preserved failed trial required')
 for f,d in pm['source_hashes'].items():
  if sha(prefix/'sources'/f)!=d:raise ValueError('physical source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(prefix/'sources/models',archive/'models');shutil.copy2(ROOT/'models/film_routed_contact/AdmissibleRelease.h',archive/'models/film_routed_contact/AdmissibleRelease.h');cpp=archive/'diagnostics/film_three_finger/RoutedReleaseReference.cpp';cpp.parent.mkdir(parents=True);text=(ROOT/'diagnostics/film_three_finger/EdgeRelease.cpp').read_text();anchor=' if(argc==4&&std::string(argv[3]).rfind("ac",0)==0){'
 if text.count(anchor)!=1:raise ValueError('existing V2 loader anchor differs')
 text=text.split(anchor)[0];cpp.write_text('#include "../../models/film_routed_contact/AdmissibleRelease.h"\n'+text.replace('"REGRIP_EDGE_V2"','"REGRIP_ROUTED_EDGE_V2"')+TAIL);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};forecast=None
 if a.reuse:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((previous/'summary.json').read_text())
  if old['source_hashes']!=sources or sha(previous/'reference')!=old['binary_sha256'] or old['input_checkpoint_sha256']!=sha(checkpoint):raise ValueError('same-IVP compiled release binary required')
  if old['status']=='PASS':forecast=2*(old['root_seconds']+old['free_seconds']+old['rk_seconds']*a.grid/old['grid'])+30
  elif a.reuse_failed_profile and old['status']=='FAIL' and old['grid'] in (32,64) and a.grid==2*old['grid'] and old.get('failure_reason','').startswith('positive acceleration reaction outside touching tangent state;'):
   legacy=ROOT/'results/autonomous_film_20261118_three_film_acc_local1075';lm=json.loads((legacy/'summary.json').read_text())
   if lm['status']!='PASS' or lm['acc_grid']!=64:raise ValueError('complete old64-RK evaluation-count profile required')
   # Failed32 total is a conservative measured root+startup cost. Add a
   # COMPLETE64-stage old-route run (same core/mesh,includes free remainder),
   # then2x+30s. This is a conditional CROSS-ROUTE cost estimate,not a speed
   # claim or an extrapolation of a failed RK prefix to a completed32 run.
   forecast=2*(old['process']['runtime_s']+lm['run']['runtime_s']*a.grid/64)+30
  else:raise ValueError('failed reference is not a qualified physical profile;explicit guarded64 probe required')
  shutil.copy2(previous/'reference',out/'reference');compile=dict(exit_code=0,reused_from=a.reuse,failed_profile_reuse=a.reuse_failed_profile)
 else:
  if a.grid!=32:raise ValueError('first bounded profile must be32;do not jump to large grid')
  compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 r=dict(status='BLOCKED',scope='new bounded numerical composition of EXISTING laws,27.2..27.4ms release reference ONLY;NOT actual SOFA/whole time/energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,prefix_summary_sha256=sha(prefix/'summary.json'),input_checkpoint_sha256=sha(checkpoint),grid=a.grid,compile=compile,predicted_child_runtime_s=forecast,conditional_failed_profile_cost=a.reuse_failed_profile,root_reaction_work=None,impulse_at_release='NONE;continuous q/v',momentum_metric='sum of segment residual norms,NOT independently measured global vector defect',release_time_note='collocation admissibility bracket and RK stage times,NOT certified continuous exit time',old_trials='1346/1347/1350 FAIL remain')
 if forecast and forecast>480:r['failure_reason']='measured policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 run=guarded([out/'reference',out/'input.checkpoint',out/'states.csv',str(a.grid)],out/'process',480) if compile['exit_code']==0 else None;r.update(status='FAIL',process=run)
 if (out/'reference').exists():r['binary_sha256']=sha(out/'reference')
 if run and run['exit_code']==0:r.update(json.loads((out/'process/stdout.log').read_text()))
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.glob('states.csv*') if f.is_file()};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
