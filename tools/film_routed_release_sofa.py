"""Actual bounded routed release;reuse existing commit/checkpoint/Free owner."""
import argparse,csv,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();ref=ROOT/'results/autonomous_film_20261118_routed_release_quarter1355';proof=json.loads((ref/'summary.json').read_text());prefix=ROOT/'results/autonomous_film_20261118_routed_release_prefix1349';pm=json.loads((prefix/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_routed_edge_unload1346';m=json.loads((parent/'summary.json').read_text());checkpoint=prefix/'input.checkpoint'
 if proof['status']!='PASS' or proof['grid']!=128 or proof['input_checkpoint_sha256']!=sha(checkpoint) or pm['actual_summary_sha256']!=sha(parent/'summary.json') or not pm['accepted_prefix_qv_time_exact']:raise ValueError('qualified bounded128 release and exact actual accepted prefix required')
 for f,d in proof['source_hashes'].items():
  if sha(ref/'sources'/f)!=d:raise ValueError('qualified release source changed')
 for f,d in proof['raw_hashes'].items():
  if sha(ref/f)!=d:raise ValueError('qualified release state changed')
 tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2]);end=time+dt
 if tokens[0]!='REGRIP_ROUTED_EDGE_V2' or dt!=.0002 or time!=pm['actual_time_s']:raise ValueError('qualified actual clock/schema differs')
 forecast=2*proof['process']['runtime_s']+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ref/'sources/models',archive/'models');path=archive/'models/film_three_finger_release/ThreeFilmRelease.cpp';text=path.read_text();text=re.sub(r'\bThreeFilm[A-Za-z0-9_]*ODE\b',lambda x:'Routed'+x.group(),text)
 text=text.replace('#include "../film_three_finger_resume/AccelerationRelease.h"','#include "../film_three_finger_resume/AccelerationRelease.h"\n#include "../film_routed_contact/AdmissibleRelease.h"')
 if text.count('"REGRIP_FREE_V3"')!=2 or text.count('dt!=.0001')!=2:raise ValueError('explicit routed FREE schema/dt source anchors differ')
 text=text.replace('"REGRIP_FREE_V3"','"REGRIP_ROUTED_FREE_V3"').replace('dt!=.0001','dt!=.0002')
 start='readActual(s,q,v);double window=dt/5;';finish='  if(gap< -1e-10||momentum>1e-17)'
 if text.count(start)!=1 or text.count(finish)!=1:raise ValueError('release composition source bounds differ')
 i,j=text.index(start),text.index(finish)
 replacement='''readActual(s,q,v);auto composed=regrip_routed_release::resolve(s,q,v,last,dt,edges,128);const auto&release=composed.release;const auto&after=composed.after;const double finish=last+dt,remaining=finish-release.endTime;Eigen::VectorXd middle=(release.q+after.q)/2;double gap=composed.minimumGap,momentum=composed.momentumBound;
  std::ofstream preJournal(filename.getValue()+".release.pre.csv");preJournal<<std::setprecision(17)<<"time,weight_s,finger,force,gap,normal_velocity,q,v\\n";
  for(unsigned k=0;k<3;++k){const auto&x=k?composed.pre.stages[k-1].q:q;const auto&vel=k?composed.pre.stages[k-1].v:v;auto geo=edgeGeometry(s,x,edges);for(unsigned f=0;f<3;++f){preJournal<<last+composed.preH*(k==0?0:k==1?.5:1)<<','<<composed.preH*(k==1?2./3:1./6)<<','<<f<<','<<(k?composed.pre.stages[k-1].force(f):composed.pre.initialForce(f))<<','<<geo.gap(f)<<','<<geo.J.row(f).dot(vel);quote(preJournal,x);quote(preJournal,vel);preJournal<<'\\n';}}preJournal.flush();
  std::ofstream composition(filename.getValue()+".release.composition.csv");composition<<std::setprecision(17)<<"pre_h_s,admissible_root_lo_s,admissible_root_hi_s,RK_window_s,RK_grid,RK_actual_end_time_s,free_remaining_s\\n"<<composed.preH<<','<<composed.rootLo<<','<<composed.rootHi<<','<<composed.window<<",128,"<<release.endTime<<','<<remaining<<'\\n';composition.flush();
'''
 text=text[:i]+replacement+text[j:]
 changes={'extern "C" {':'void registerFilmRoutedField(sofa::core::ObjectFactory*);\nextern "C" {','void registerObjects(sofa::core::ObjectFactory*f){':'void registerObjects(sofa::core::ObjectFactory*f){registerFilmRoutedField(f);','return "ReGripThreeFilmRelease";':'return "ReGripRoutedThreeFilmRelease";','EXPERIMENTAL isolated20us three-row acceleration complementarity release plus80us free midpoint;NOT full time/energy/grasp':'EXPERIMENTAL bounded routed admissible Lobatto then40us RK128 acceleration release and free remainder;NOT full time/energy/grasp'}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('routed release registration anchor differs')
  text=text.replace(old,new)
 path.write_text(text);cmake=archive/'models/film_three_finger_release/CMakeLists.txt';text=cmake.read_text();anchor='SHARED ThreeFilmRelease.cpp)'
 if text.count(anchor)!=1:raise ValueError('release CMake differs')
 cmake.write_text(text.replace(anchor,'SHARED ThreeFilmRelease.cpp ../film_routed_tendon/Field.generated.cpp)'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('routed_release_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_release','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='actual bounded routed DEFORMED contact release ONLY;NOT whole time/energy/recovery/wrapping/holding/lift/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,reference_summary_sha256=sha(ref/'summary.json'),prefix_summary_sha256=sha(prefix/'summary.json'),source_checkpoint_sha256=sha(checkpoint),configure=configure,compile=compile,predicted_child_runtime_s=forecast,start_time_s=time,dt_s=dt,expected_end_time_s=end,RK_grid=128,time_scheme='admissible compressive Lobatto pre +40us existing RK4 acceleration LCP +free midpoint to exact macro end',momentum_metric='sum of segment residual norms;NOT separately measured global vector defect',sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),root_reaction_work=None,legacy_sampled_work='NOT restored;exclude ALL sampled-work values',old_trials='1346/1347/1350/1352 FAIL remain')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmRelease.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('release SDK ABI mismatch')
  token=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),checkpoint=sha(checkpoint),reference=sha(ref/'summary.json')),sort_keys=True).encode()).hexdigest();before=tokens.copy();tokens[4]=token;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[:4]+tokens[5:]!=before[:4]+before[5:]:raise ValueError('physical checkpoint payload changed')
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmEdgeODE');owner.tag='RoutedThreeFilmAccelerationReleaseODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',token);owner.set('endTime',format(end,'.17g'));owner.attrib.pop('ownerCostFilename',None)
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmPrimitive.so'):
    if sha(node.get('pluginName'))!=m['binary_sha256']:raise ValueError('parent executable changed')
    node.set('pluginName',str(binary))
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
  tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),build_relative=str(build.relative_to(ROOT)),identity=token,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'),physical_checkpoint_payload_exact=True)
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
  write_json(out/'summary.json',dict(r,status='NOT RUN'))
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',480);r.update(process=run,sofa_errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log')))
  if run['exit_code']==0 and not r['sofa_errors']:
   actual=list(csv.DictReader((out/'three.states.csv').open()));expected=next(csv.DictReader((ref/'states.csv').open()));api={k:float(np.max(abs(np.fromstring(actual[0][k],sep=' ')-np.fromstring(expected[k],sep=' ')))) for k in ('q','v')};clock=float(actual[0]['time'])==float(expected['time'])==end;metrics=next(csv.DictReader((out/'three.release.metrics.csv').open()));composition=next(csv.DictReader((out/'three.release.composition.csv').open()));stages=list(csv.DictReader((out/'three.release.stages.csv').open()));reference_stages=list(csv.DictReader((ref/'states.csv.rk.csv').open()));stage_exact=all(x['time']==y['time'] and x['weight_s']==y['weight_s'] and x['mask']==y['mask'] and all(np.array_equal(np.fromstring(x[k],sep=' '),np.fromstring(y[k],sep=' ')) for k in ('q','v','force')) for x,y in zip(stages,reference_stages));minimum=min(float(np.min(np.fromstring(z['force'],sep=' '))) for z in stages);snapshots=list(out.glob('three.checkpoint_*.txt'));valid=len(actual)==1 and len(stages)==len(reference_stages)==512 and stage_exact and max(api.values())<1e-12 and clock and minimum>=0 and float(metrics['minimum_gap_mm'])>=-1e-10 and float(metrics['momentum_Ns'])<=1e-17 and metrics['final_active_mask']=='0' and float(metrics['outgoing_normal_velocity_min_mm_s'])>0 and len(snapshots)==1 and snapshots[0].read_text().startswith('REGRIP_ROUTED_FREE_V3 ');r.update(status='PASS' if valid else 'FAIL',reference_max_abs=api,accumulated_clock_exact=clock,all_RK_stage_states_forces_exact=stage_exact,minimum_applied_normal_force_N=minimum,release_metrics=metrics,composition=composition,api_gate=1e-12,velocity_jump_applied=False)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes')}))
if __name__=='__main__':main()
