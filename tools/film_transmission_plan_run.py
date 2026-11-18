"""Experimental deterministic local-refinement plan;NOT adaptive-error certification."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_compiled_sources import identical_compiled_sources
def make_plan(duration,refinement,startup_epochs=1,graded=False):
 time=0.;ends=[];epochs=[]
 while time<duration:
  begin=time;target=min(begin+.0008,duration);nominal=.000025 if len(epochs)<startup_epochs else min(.00005*2**(len(epochs)-startup_epochs),.0002) if graded else .0002;step=nominal/refinement;n=round((target-begin)/step)
  if n<1:raise ValueError('invalid integer local-refinement plan')
  for i in range(n):
   end=target if i+1==n else time+step
   if not(time<end<=duration and end-time<=.001):raise ValueError('nonpositive/invalid public plan interval')
   ends.append(end);time=end
  epochs.append(target)
 if time!=duration or len(ends)>2000:raise ValueError('bounded local plan not completed')
 return ends,epochs
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=(.0002,.0008,.0016,.0032,.0064,.05),default=.0002);p.add_argument('--refinement',type=int,choices=(1,2,4),default=1);p.add_argument('--reuse');p.add_argument('--cost-pair',nargs=2);p.add_argument('--startup-epochs',type=int,choices=(1,2,4,8),default=1);p.add_argument('--graded',action='store_true');a=p.parse_args();ends,epochs=make_plan(a.duration,a.refinement,a.startup_epochs,a.graded);N=len(ends);forecast=None;cost=[]
 if a.reuse:
  prev=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((prev/'summary.json').read_text())
  if proof['status']!='PASS':raise ValueError('successful actual/standalone plan profile required')
  forecast=2*max(proof['process']['runtime_s'],proof['reference_process']['runtime_s'])*N/proof['steps']+30
  if a.cost_pair:
   measured=[]
   for name in a.cost_pair:
    path=ROOT/'results'/('autonomous_film_'+name)/'summary.json';m=json.loads(path.read_text())
    if m['status']!='PASS' or m['duration_s']!=.05 or m['binary_sha256']!=proof['binary_sha256'] or m['reference_binary_sha256']!=proof['reference_binary_sha256']:raise ValueError('same completed physical/model plan cost family required')
    measured.append(m);cost.append(dict(case=name,summary_sha256=sha(path),steps=m['steps'],actual_s=m['process']['runtime_s'],reference_s=m['reference_process']['runtime_s']))
   if min(m['steps'] for m in measured)<250 or max(m['steps'] for m in measured)<500 or N>2*max(m['steps'] for m in measured):raise ValueError('bounded two-size cost extrapolation required')
   forecast=1.2*max(max(m['process']['runtime_s'],m['reference_process']['runtime_s'])/m['steps'] for m in measured)*N+30
 elif N>8 or a.cost_pair:raise ValueError('first plan is an eight-step cost/API profile')
 parent=ROOT/'results/autonomous_film_20261118_transmission_hold50_1187';meta=json.loads((parent/'summary.json').read_text())
 if meta['status']!='PASS':raise ValueError('qualified actual base scene required')
 for name,digest in meta['raw_hashes'].items():
  if sha(parent/name)!=digest:raise ValueError('parent raw changed')
 for path,digest in meta['provider_hashes'].items():
  if sha(path)!=digest:raise ValueError('immutable provider binary changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='BLOCKED',scope='actual single-film deterministic local dt plan;NOT error-controlled adaptive/contact/grasp certificate',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),duration_s=a.duration,steps=N,refinement=a.refinement,startup_epochs=a.startup_epochs,graded_expansion=a.graded,canonical_epochs=epochs,predicted_child_runtime_s=forecast,cost_evidence=cost,parent_summary_sha256=sha(parent/'summary.json'),sdk=str(SDK),physical_input='same no-object mass/material/root/route/C2 hold Tmax.0001,ramp.01,release.05..06',root_reaction_work=None)
 if forecast is not None and forecast>480:result['failure_reason']='measured child policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',result);print(json.dumps(result));return
 archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/TransmissionPlan.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/TransmissionPlan.cpp',cpp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('film_transmission_plan_'+a.tag);reference=out/'reference'
 if a.reuse:
  if not identical_compiled_sources(proof['source_hashes'],sources):raise ValueError('ALL code/build/input closure differs')
  binary=ROOT/proof['build_relative']/'libReGripFilmTransmissionPlan.so'
  if sha(binary)!=proof['binary_sha256'] or sha(prev/'reference')!=proof['reference_binary_sha256']:raise ValueError('qualified plan binary changed')
  build=binary.parent;shutil.copy2(prev/'reference',reference);configure=compile=refcompile={'exit_code':0,'reused_from':a.reuse}
 else:
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_transmission_plan','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;binary=build/'libReGripFilmTransmissionPlan.so';refcompile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',reference],out/'reference_compile',120) if compile and compile['exit_code']==0 else None
 result.update(status='FAIL',source_hashes=sources,configure=configure,compile=compile,reference_compile=refcompile,build_relative=str(build.relative_to(ROOT)));(out/'plan.txt').write_text(str(N)+'\n'+'\n'.join(format(t,'.17g') for t in ends)+'\n');shutil.copy2(parent/'public_mass.txt',out/'public_mass.txt');write_json(out/'summary.json',result)
 if refcompile and refcompile['exit_code']==0:
  deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('plan SDK ABI mismatch')
  ref=guarded([reference,out/'plan.txt',out/'public_mass.txt',out/'reference'],out/'reference_process',480);result.update(reference_process=ref,binary_sha256=sha(binary),reference_binary_sha256=sha(reference),plan_sha256=sha(out/'plan.txt'),public_mass_sha256=sha(out/'public_mass.txt'))
  if ref['exit_code']==0:
   tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.remove(scene.find('FilmTransmissionHoldODE'));scene.set('time','0');scene.set('dt',format(ends[0],'.17g'))
   for node in scene.iter():
    if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripFilmTransmission.so'):node.set('pluginName',str(binary))
    for key,value in list(node.attrib.items()):
     if key in ('filename','displacementFilename') and value.startswith(str(parent)):node.set(key,str(out)+value[len(str(parent)):])
   ET.SubElement(scene,'FilmTransmissionPlanODE',dict(name='ode',root='@finger0/dofs',field='@finger0/assembly/filmField',filename=str(out/'actual.csv'),massFilename=str(out/'public_mass.txt'),maxSteps=str(N),planFilename=str(out/'plan.txt')));tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(N),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'));result.update(process=run,sofa_errors=errors,scene_sha256=sha(out/'scene.scn'))
   if run['exit_code']==0 and not errors:
    x=list(csv.DictReader((out/'actual.csv').open()));y=list(csv.DictReader((out/'reference.states.csv').open()));field=list(csv.DictReader((out/'film_0.csv').open()));clocks=list(csv.DictReader((out/'actual.csv.clock.csv').open()));api={k:max(float(np.max(abs(np.fromstring(a[k],sep=' ')-np.fromstring(b[k],sep=' ')))) for a,b in zip(x,y)) for k in ('q','v')};clock=len(x)==len(y)==len(clocks)==len(field)==N and all(a['time']==b['time'] and float(a['time'])==t for a,b,t in zip(x,y,ends));stage=list(csv.DictReader((out/'actual.csv.stages.csv').open()))==list(csv.DictReader((out/'reference.stages.csv').open()));Terror=max(abs(float(a['T_end'])-float(f['T_per_rail'])) for a,f in zip(x,field));momentum=max(float(r['momentum_residual']) for r in x);contexts=all(r['contexts']=='4' and r['exact_child_time']=='true' for r in clocks);result.update(status='PASS' if clock and stage and contexts and Terror==0 and max(api.values())<1e-12 and momentum<=1e-17 else 'FAIL',api_gate=1e-12,reference_max_abs=api,accumulated_clock_exact=clock,all_contexts_exact=contexts,stage_rows_exact=stage,actual_control_error_N=Terror,momentum_residual_Ns=momentum,actual_end_time_s=float(x[-1]['time']))
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_hashes','configure','compile','reference_compile','process','reference_process','raw_hashes','canonical_epochs')}))
if __name__=='__main__':main()
