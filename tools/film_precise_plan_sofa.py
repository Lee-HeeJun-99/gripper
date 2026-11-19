"""Actual SOFA bounded1ms plan, strict ALL accepted states and physical stages."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(40,80,160),default=40);p.add_argument('--reference',required=True);p.add_argument('--reuse-build');p.add_argument('--profile');a=p.parse_args();ref=ROOT/'results'/('autonomous_film_'+a.reference);rm=json.loads((ref/'summary.json').read_text());api=ROOT/'results/autonomous_film_20261119_precise_tendon_api1717';am=json.loads((api/'summary.json').read_text())
 if rm['status']!='COMPLETED_NOT_QUALIFIED' or am['status']!='PASS':raise ValueError('completed independent plan and qualified Field required')
 for parent,m in ((ref,rm),(api,am)):
  for f,d in m['source_hashes'].items():
   if sha(parent/'sources'/f)!=d:raise ValueError('immutable source changed')
 for f,d in rm['raw_hashes'].items():
  if sha(ref/f)!=d:raise ValueError('immutable reference raw changed')
 if a.steps>40:
  if not a.profile:raise ValueError('measured actual base profile required')
  pm=json.loads((ROOT/'results'/('autonomous_film_'+a.profile)/'summary.json').read_text());forecast=2*pm['process']['runtime_s']*a.steps/pm['steps']+20
  if pm['status']!='PASS' or forecast>480:raise ValueError('profile forecast blocks actual child;NOT OS exhaustion')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(ref/'sources/models',out/'sources/models');shutil.copy2(api/'sources/models/film_precise_attachment/Field.generated.cpp',out/'sources/models/film_precise_attachment/Field.generated.cpp')
 for f in ('film_precise_attachment/Owner.cpp','film_precise_tendon/Owner.cpp','film_solver_plan/Owner.cpp'):shutil.copy2(ROOT/'models'/f,out/'sources/models'/f)
 if sha(ROOT/'models/film_solver_plan/Plan.h')!=sha(out/'sources/models/film_solver_plan/Plan.h'):raise ValueError('actual plan differs from independent plan')
 folder=out/'sources/models/film_solver_plan';(folder/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.22)
project(ReGripPrecisePlan LANGUAGES CXX)
find_package(Eigen3 REQUIRED)
find_package(Sofa.Core REQUIRED)
find_package(Sofa.DefaultType REQUIRED)
find_package(Sofa.LinearAlgebra REQUIRED)
find_package(Sofa.Simulation.Core REQUIRED)
find_package(Sofa.Component.StateContainer REQUIRED)
add_library(ReGripPrecisePlan SHARED Owner.cpp ../film_precise_attachment/Field.generated.cpp)
target_compile_features(ReGripPrecisePlan PRIVATE cxx_std_17)
target_compile_options(ReGripPrecisePlan PRIVATE -O2 -ffp-contract=off)
target_link_libraries(ReGripPrecisePlan PRIVATE Eigen3::Eigen Sofa.Core Sofa.DefaultType Sofa.LinearAlgebra Sofa.Simulation.Core Sofa.Component.StateContainer)
''')
 sources={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()}
 if a.reuse_build:
  old=ROOT/'results'/('autonomous_film_'+a.reuse_build);om=json.loads((old/'summary.json').read_text());build=ROOT/om['build_relative']
  if om['status']!='PASS' or om['source_hashes']!=sources or sha(build/'libReGripPrecisePlan.so')!=om['binary_sha256']:raise ValueError('same actual binary and ALL sources required')
  compile=dict(exit_code=0,reused_build=str(build));configure=dict(exit_code=0)
 else:
  build=ROOT/'build'/('precise_plan_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',folder,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'--target','ReGripPrecisePlan','-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 r=dict(status='FAIL',scope='actual SOFA1ms free coupon ALL-state/stage API identity ONLY;NOT all-time convergence/energy/contact/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,reference_summary_sha256=sha(ref/'summary.json'),Field_API_summary_sha256=sha(api/'summary.json'),configure=configure,compile=compile,build_relative=str(build.relative_to(ROOT)),steps=a.steps,dt_s=.001/a.steps,duration_s=.001,actual_solver='FilmPreciseSolverPlanODE:Gauss4 explicit early/late plan',sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),mass_sha256=sha(ref/'public_mass.txt'),root_reaction_work=None,contact='NONE')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripPrecisePlan.so';r['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  scene=ROOT/'results/autonomous_film_20261119_precise_tendon_actual1718/scene.scn';tree=ET.parse(scene);root=tree.getroot();root.set('dt',format(.001/a.steps,'.17g'));owner=root.find('FilmPreciseTendonSubcycledODE');owner.tag='FilmPreciseSolverPlanODE';owner.set('maxSteps',str(a.steps));owner.set('endTime','.001');owner.set('filename',str(out/'actual.csv'));field=root.find('.//FilmPreciseTendon');field.set('filename',str(out/'film.csv'));field.set('displacementFilename',str(out/'displacement.csv'))
  for node in root.findall('RequiredPlugin'):
   if node.get('pluginName','').endswith('libReGripPreciseStartup.so'):node.set('pluginName',str(binary))
  tree.write(out/'scene.scn');r['scene_sha256']=sha(out/'scene.scn');r['process']=guarded(['/usr/bin/time','-v','-o',out/'resource.txt',SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480)
  errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r['sofa_errors']=errors
  if (out/'resource.txt').exists():
   for line in (out/'resource.txt').read_text().splitlines():
    if 'Maximum resident set size' in line:r['maximum_RSS_KiB']=int(line.split(':')[-1])
  if r['process']['exit_code']==0 and not errors:
   actual=list(csv.DictReader((out/'actual.csv').open()));expected=list(csv.DictReader((ref/str(a.steps)/'state.csv').open()));stages=list(csv.DictReader((out/'actual.csv.gauss4.csv').open()));truth=list(csv.DictReader((ref/str(a.steps)/'state.csv.stages.csv').open()))
   if len(actual)==len(expected)==a.steps and len(stages)==len(truth):
    state={key:max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(actual,expected)) for key in ('q','v')};stage={key:max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(stages,truth)) for key in ('q','v','reduced_physical_force_N')};clock=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(actual+stages,expected+truth));tension=max(abs(float(x['T'])-float(y['T'])) for x,y in zip(stages,truth));r.update(status='PASS' if max(state.values())<=1e-12 and max(stage.values())<=1e-12 and clock<=1e-18 and tension==0 else 'FAIL',ALL_accepted_max_abs=state,ALL_stage_max_abs=stage,clock_max_abs_s=clock,applied_tension_max_abs_N=tension,actual_stage_count=len(stages),accepted_time=float(actual[-1]['time']))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.scn','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process')}))
if __name__=='__main__':main()
