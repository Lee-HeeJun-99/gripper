"""Single actual nonlinear transmission coupon and same-kernel API reference.

No object/contact: isolates actuation/attachment from impact and friction.
"""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_compiled_sources import identical_compiled_sources
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,default=8);p.add_argument('--duration',type=float,default=.0008);p.add_argument('--bond',type=float,choices=(.0001,.001,.01),default=.001);p.add_argument('--offset',type=float,choices=(-5.,5.),default=5.);p.add_argument('--reuse');p.add_argument('--common',action='store_true');p.add_argument('--scheme',choices=('midpoint','gauss'),default='midpoint');p.add_argument('--hold',action='store_true');p.add_argument('--cost-pair',nargs=2);a=p.parse_args()
 if a.hold and (a.scheme!='gauss' or not a.common):raise ValueError('separate longer-HOLD input requires Gauss/common scene and journal')
 if not 1<=a.steps<=2000 or not 0<a.duration<=.05 or a.duration/a.steps>.001:raise ValueError('bounded coupon step/time')
 if a.scheme=='gauss' and not a.common:raise ValueError('Gauss comparison requires exact common observation time')
 parent=ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002';tree=ET.parse(parent/'scene.scn');scene=tree.getroot();ledger=json.loads((ROOT/'reports/FILM_CONTACT_EVIDENCE_20261118_three_film_recovery_v12.json').read_text())
 provider={}
 for plugin in scene.findall('RequiredPlugin'):
  path=plugin.get('pluginName','')
  if path.startswith('/') and not path.endswith('libReGripThreeFilmEvent.so'):
   key=str(__import__('pathlib').Path(path).relative_to(ROOT));digest=ledger['files'].get(key)
   if not digest or sha(path)!=digest:raise ValueError('immutable SDK/provider binary differs:'+key)
   provider[path]=digest
 mass=parent/'public_mass_reference.txt'
 mass_ledger=json.loads((ROOT/'reports/FILM_CONTACT_EVIDENCE_20261118_three_film_v10.json').read_text())
 if sha(mass)!=mass_ledger['files'].get(str(mass.relative_to(ROOT))):raise ValueError('original public mass snapshot differs from its V10 ledger')
 forecast=None;cost_evidence=None
 if a.cost_pair and not a.reuse:raise ValueError('calibrated cost needs qualified reused source/binary')
 if a.reuse:
  prev=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((prev/'summary.json').read_text())
  if proof['status']!='PASS':raise ValueError('successful actual/reference profile required')
  forecast=2*max(proof['process']['runtime_s'],proof['reference_process']['runtime_s'])*a.steps/proof['steps']+30
  if a.cost_pair:
   measured=[];cost_evidence=[]
   for name in a.cost_pair:
    path=ROOT/'results'/('autonomous_film_'+name)/'summary.json';m=json.loads(path.read_text())
    if m['status']!='PASS' or m['steps']<250 or m['duration_s']!=a.duration or m.get('longer_hold_input',False)!=a.hold or m['binary_sha256']!=proof['binary_sha256'] or m['reference_binary_sha256']!=proof['reference_binary_sha256'] or m['bond_stiffness_N_mm']!=a.bond or m['guide_offset_mm']!=a.offset:raise ValueError('complete same-input exact-binary large cost samples required')
    measured.append(m);cost_evidence.append(dict(case=name,summary_sha256=sha(path),steps=m['steps'],reference_runtime_s=m['reference_process']['runtime_s'],actual_runtime_s=m['process']['runtime_s']))
   if max(m['steps'] for m in measured)<500 or len({m['steps'] for m in measured})!=2 or a.steps>2*max(m['steps'] for m in measured):raise ValueError('two measured sizes>=250/500,at most2x extrapolation')
   forecast=1.2*max(max(m['process']['runtime_s'],m['reference_process']['runtime_s'])/m['steps'] for m in measured)*a.steps+30
  if forecast>480:raise ValueError('measured child runtime forecast exceeds480s')
 elif a.steps>8:raise ValueError('first execution is an eight-step profile,not an unprofiled long run')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/Transmission.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/Transmission.cpp',cpp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('film_transmission_'+a.tag);reference=out/'reference'
 if a.reuse:
  if not identical_compiled_sources(proof['source_hashes'],sources):raise ValueError('unchanged ALL-model code/build/input closure required;documentation is separate')
  binary=ROOT/proof['build_relative']/'libReGripFilmTransmission.so'
  if sha(binary)!=proof['binary_sha256'] or sha(prev/'reference')!=proof['reference_binary_sha256']:raise ValueError('qualified binary changed')
  shutil.copy2(prev/'reference',reference);build=binary.parent;configure=compile=refcompile={'exit_code':0,'reused_from':a.reuse}
 else:
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_transmission','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;binary=build/'libReGripFilmTransmission.so';refcompile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',reference],out/'reference_compile',120) if compile and compile['exit_code']==0 else None
 result=dict(scheme=a.scheme,common_endpoint=a.common,status='FAIL',scope='actual single Film/Rails/Tendon rest coupon,NO object/contact;NOT wrapping/grasp/time approval',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,sdk=str(SDK),provider_hashes=provider,steps=a.steps,duration_s=a.duration,dt_s=a.duration/a.steps,bond_stiffness_N_mm=a.bond,guide_offset_mm=a.offset,material=dict(E_MPa=250,nu=0,skin_mm=.05,rail_mm=.1,measured=False),mass_kg=.001,volume_mm3=439.3397917746089/3,control=dict(maximum_N_per_rail=.0001,ramp_s=.01,release_begin_s=.02,release_end_s=.03,C2=True),root='station0 fixed xyz;station1z=.25 station2z;other3D DOFs free',solver='separate Gauss-Legendre order4 with unchanged physical force/Hessian' if a.scheme=='gauss' else 'existing System::smooth(false) implicit midpoint;dummy algebraic rigid block discarded',configure=configure,compile=compile,reference_compile=refcompile,predicted_child_runtime_s=forecast,build_relative=str(build.relative_to(ROOT)),root_reaction_work=None,contact='OFF/not present',legacy_sampled_work='separate origin,NOT stage work')
 result['longer_hold_input']=a.hold
 result['calibrated_cost_evidence']=cost_evidence
 if cost_evidence:result['cost_forecast_model']='maximum observed seconds/step at two complete large sizes,+20% slowdown margin,+30s overhead;UNCHANGED480s hard child timeout,not900s exception'
 if a.hold:result['control'].update(release_begin_s=.05,release_end_s=.06)
 write_json(out/'summary.json',result)
 if refcompile and refcompile['exit_code']==0:
  deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  shutil.copy2(mass,out/'public_mass.txt');result['public_mass_sha256']=sha(mass)
  ref=guarded([reference,str(a.steps),str(a.duration),str(a.bond),str(a.offset),out/'reference',out/'public_mass.txt']+(['gauss_hold'] if a.hold else ['gauss'] if a.scheme=='gauss' else ['common'] if a.common else []),out/'reference_process',480);result.update(reference_process=ref,binary_sha256=sha(binary),reference_binary_sha256=sha(reference))
  if ref['exit_code']==0:
   for node in list(scene):
    if node.tag=='Node' and node.get('name')!='finger0' or node.tag.endswith('ODE'):scene.remove(node)
    elif node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('libReGripThreeFilmEvent.so'):node.set('pluginName',str(binary))
   for node in scene.iter():
    if node.tag=='FilmRailTendon':node.set('bondStiffness',str(a.bond));node.set('guideOffset',str(a.offset))
    if node.tag=='FilmRailTendon' and a.hold:node.set('releaseBegin','.05');node.set('releaseEnd','.06')
    for key,value in list(node.attrib.items()):
     if key in ('filename','displacementFilename') and value.startswith(str(parent)):node.set(key,str(out)+value[len(str(parent)):])
   scene.set('dt',format(a.duration/a.steps,'.17g'));scene.set('time','0');owner=ET.SubElement(scene,'FilmTransmissionGaussODE' if a.scheme=='gauss' else 'FilmTransmissionAlignedODE' if a.common else 'FilmTransmissionODE',dict(name='ode',root='@finger0/dofs',field='@finger0/assembly/filmField',filename=str(out/'actual.csv'),massFilename=str(out/'public_mass.txt'),maxSteps=str(a.steps)));owner.set('endTime',format(a.duration,'.17g')) if a.common else None;tree.write(out/'scene.scn')
   if a.hold:owner.tag='FilmTransmissionHoldODE';tree.write(out/'scene.scn')
   run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'));result.update(process=run,sofa_errors=errors,scene_sha256=sha(out/'scene.scn'))
   if run['exit_code']==0 and not errors:
    actual=list(csv.DictReader((out/'actual.csv').open()));expected=list(csv.DictReader((out/'reference.states.csv').open()));fields=list(csv.DictReader((out/'film_0.csv').open()))
    if len(actual)!=a.steps or len(expected)!=a.steps or len(fields)!=a.steps:raise ValueError('complete actual/reference/field journal required')
    api={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};clock=all(x['time']==y['time'] for x,y in zip(actual,expected));Terror=max(abs(float(x['T_end'])-float(f['T_per_rail'])) for x,f in zip(actual,fields));residual=max(float(x['momentum_residual']) for x in actual);result.update(status='PASS' if max(api.values())<1e-12 and clock and Terror==0 and residual<=1e-17 else 'FAIL',api_gate=1e-12,reference_max_abs=api,accumulated_clock_exact=clock,actual_endpoint_control_error_N=Terror,momentum_residual_Ns=residual,actual_end_time_s=float(actual[-1]['time']))
    if a.scheme=='gauss':
     actual_stages=list(csv.DictReader((out/'actual.csv.stages.csv').open()));expected_stages=list(csv.DictReader((out/'reference.stages.csv').open()));stage_ok=len(actual_stages)==len(expected_stages)==2*a.steps and actual_stages==expected_stages;result['actual_stage_rows_exact']=stage_ok
     if not stage_ok:result['status']='FAIL'
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.txt','.csv')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_hashes','configure','compile','reference_compile','process','reference_process','raw_hashes','provider_hashes')}))
if __name__=='__main__':main()
