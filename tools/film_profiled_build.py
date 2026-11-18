"""Separate source-bound profiled route Field/ODE; unchanged lateral provider."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 base=ROOT/'results/autonomous_film_20261118_lateral_api_build1356';b=json.loads((base/'summary.json').read_text())
 math=ROOT/'results/autonomous_film_20261118_profiled_geometry1432';m=json.loads((math/'summary.json').read_text())
 if b['status']!='PASS' or m['status']!='PASS':raise ValueError('qualified providers required')
 for f,d in b['source_hashes'].items():
  if sha(base/'sources'/f)!=d:raise ValueError('lateral archive changed')
 # The subsequent addition only enables the same passive-profile argument.
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(base/'sources',archive)
 dest=archive/'models/film_profiled_tendon';dest.mkdir(exist_ok=True);shutil.copy2(ROOT/'models/film_profiled_tendon/Route.h',dest/'Route.h')
 def transform(s):
  return s.replace('film_lateral','film_profiled').replace('regrip_lateral_tendon','regrip_profiled_tendon').replace('FilmLateral','FilmProfiled').replace('frozenLateral','frozenProfile').replace('lateralOffset','profileAmplitude').replace('registerFilmLateral','registerFilmProfiled')
 for name in ('Field.generated.cpp','Owner.cpp','Step.h','CMakeLists.txt'):(dest/name).write_text(transform((archive/'models/film_lateral_tendon'/name).read_text()))
 api=archive/'tests/test_film_profiled_api.generated.cpp';api.write_text(transform((archive/'tests/test_film_lateral_api.generated.cpp').read_text()).replace(':6)',':.5)').replace('?6:0','?.5:0'))
 cpp=archive/'diagnostics/film_three_finger/ProfiledPlan.cpp';cpp.write_text(transform((archive/'diagnostics/film_three_finger/LateralPlan.cpp').read_text()))
 build=ROOT/'build'/('film_profiled_'+a.tag);build.mkdir(exist_ok=False)
 configure=guarded(['cmake','-S',dest,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
 compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 runs=[]
 if compile and compile['exit_code']==0:
  for binary in (build/'libReGripFilmProfiledTransmission.so',build/'test_film_profiled_api'):
   deps=subprocess.check_output(['ldd',binary],text=True);(out/(binary.name+'.ldd.txt')).write_text(deps)
   if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('profiled SDK ABI mismatch')
  for value in ('0','.5'):runs.append(guarded([build/'test_film_profiled_api',value],out/('api_'+value),120))
  runs.append(guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120))
 r=dict(status='PASS' if len(runs)==3 and all(x['exit_code']==0 for x in runs) else 'FAIL',design='profiled',control_ramp_s=.01,scope='separate generated actual ForceField API and no-object Gauss owner;NOT dynamic/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},math_summary_sha256=sha(math/'summary.json'),base_provider_sha256=sha(base/'summary.json'),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),build_relative=str(build.relative_to(ROOT)),configure=configure,compile=compile,checks=runs)
 if r['status']=='PASS':r.update(binary_sha256=sha(build/'libReGripFilmProfiledTransmission.so'),reference_binary_sha256=sha(out/'reference'))
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='source_hashes'}))
if __name__=='__main__':main()
