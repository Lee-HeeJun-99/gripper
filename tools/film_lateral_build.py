"""Source-bound separate lateral Field/ODE generation from original API path."""
import argparse,json,re,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_routed_generate import generate
def apply_control(archive,reference,ramp):
 if ramp==.01:return
 path=archive/'models/film_lateral_tendon/Step.h';text=path.read_text();anchor='// Same projected virtual-work assembly and Gauss map;ONLY cable geometry new.'
 if text.count(anchor)!=1 or text.count('holdControl().sample')!=2:raise ValueError('frozen lateral stage-control adapter differs')
 text=text.replace(anchor,anchor+'\ninline regrip_film_impact::EventControl slowControl(){auto input=holdControl();input.ramp=.04;return input;}').replace('holdControl().sample','slowControl().sample');path.write_text(text)
 path=archive/'models/film_lateral_tendon/Owner.cpp';text=path.read_text();anchor=' Step advance('
 if text.count(anchor)!=1:raise ValueError('unique owner-control override anchor required')
 path.write_text(text.replace(anchor,' regrip_film_impact::EventControl prescribedControl()const override{return slowControl();}\n'+anchor))
 text=reference.read_text()
 if text.count('holdControl().sample')!=2:raise ValueError('reference control journal differs')
 reference.write_text(text.replace('holdControl().sample','slowControl().sample'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--control-ramp',type=float,choices=(.01,.04),default=.01);a=p.parse_args();math=ROOT/'results/autonomous_film_20261118_lateral_math_geometry1353';mp=json.loads((math/'summary.json').read_text())
 if mp['status']!='PASS' or sha(ROOT/'models/film_lateral_tendon/Route.h')!=mp['source_hashes']['models/film_lateral_tendon/Route.h']:raise ValueError('qualified same lateral potential required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(ROOT/'tools/film_routed_generate.py',out/'base_generator.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));tests=archive/'tests';tests.mkdir();shutil.copy2(ROOT/'tests/test_film_rail_tendon_api.cpp',tests/'test_film_rail_tendon_api.cpp');old=generate(archive)
 def transform(text):
  for before,after in (('regrip_routed_tendon','regrip_lateral_tendon'),('FilmRoutedTendon','FilmLateralTendon'),('registerFilmRoutedField','registerFilmLateralField'),('routeAmplitude','lateralOffset'),('frozenAmplitude','frozenLateral'),('amplitude','lateral'),('4.5','6'),('quadratic','outboard lateral'),('film_routed_tendon','film_lateral_tendon')):text=text.replace(before,after)
  return text
 generated=archive/'models/film_lateral_tendon/Field.generated.cpp';generated.write_text(transform((archive/'models/film_routed_tendon/Field.generated.cpp').read_text()));api=tests/'test_film_lateral_api.generated.cpp';api.write_text(transform((tests/'test_film_routed_api.generated.cpp').read_text()));cpp=archive/'diagnostics/film_three_finger/LateralPlan.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(transform((ROOT/'diagnostics/film_three_finger/RoutedPlan.cpp').read_text()));apply_control(archive,cpp,a.control_ramp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('film_lateral_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_lateral_tendon','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;api0=api6=refcompile=None
 if compile and compile['exit_code']==0:
  for binary in (build/'libReGripFilmLateralTransmission.so',build/'test_film_lateral_api'):
   deps=subprocess.check_output(['ldd',binary],text=True);(out/(binary.name+'.ldd.txt')).write_text(deps)
   if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('lateral SDK ABI mismatch')
  api0=guarded([build/'test_film_lateral_api','0'],out/'api_baseline',120);api6=guarded([build/'test_film_lateral_api','6'],out/'api_candidate',120);refcompile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120)
 r=dict(status='PASS' if all(x and x['exit_code']==0 for x in (configure,compile,api0,api6,refcompile)) else 'FAIL',design='lateral',control_ramp_s=a.control_ramp,scope='separate lateral actual Force/dForce/matrix/query-purity API and compiled no-object Gauss owner;NOT dynamic/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,base_generation=old,generated_field_sha256=sha(generated),generated_api_sha256=sha(api),generated_reference_sha256=sha(cpp),math_summary_sha256=sha(math/'summary.json'),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),build_relative=str(build.relative_to(ROOT)),configure=configure,compile=compile,api_baseline=api0,api_candidate=api6,reference_compile=refcompile,physical_route='0/6mm objective outboard lateral offset;constant5mm normal offset',original_Assembly_layout='UNCHANGED',total_hardware_volume_mass='NOT MEASURED;only core matched',dynamics='NOT RUN',whole_energy='BLOCKED')
 if compile and compile['exit_code']==0:r.update(binary_sha256=sha(build/'libReGripFilmLateralTransmission.so'),api_binary_sha256=sha(build/'test_film_lateral_api'))
 if refcompile and refcompile['exit_code']==0:r['reference_binary_sha256']=sha(out/'reference')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','base_generation','configure','compile','api_baseline','api_candidate','reference_compile')}))
if __name__=='__main__':main()
