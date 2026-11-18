"""Separate routed Field/Owner build + independent math and ACTUAL SOFA APIs."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_routed_generate import generate
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--core-only',action='store_true');a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(ROOT/'tools/film_routed_generate.py',out/'generator.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));tests=archive/'tests';tests.mkdir()
 for name in ('test_film_rail_tendon_api.cpp','test_film_routed.cpp'):shutil.copy2(ROOT/'tests'/name,tests/name)
 cpp=archive/'diagnostics/film_three_finger/RoutedPlan.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/RoutedPlan.cpp',cpp);generated=generate(archive,core_only=a.core_only);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};write_json(out/'generated_source_manifest.json',generated);build=ROOT/'build'/('film_routed_'+a.tag);build.mkdir(exist_ok=False)
 mathcompile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off',tests/'test_film_routed.cpp','-o',out/'math'],out/'math_compile',120);mathrun=guarded([out/'math'],out/'math_process',120) if mathcompile['exit_code']==0 else None
 configure=compile=refcompile=api0=api45=None
 if mathrun and mathrun['exit_code']==0:
  configure=guarded(['cmake','-S',archive/'models/film_routed_tendon','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
  if compile and compile['exit_code']==0:
   for binary in (build/'libReGripFilmRoutedTransmission.so',build/'test_film_routed_api'):
    deps=subprocess.check_output(['ldd',binary],text=True);(out/(binary.name+'.ldd.txt')).write_text(deps)
    if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('routed SDK ABI mismatch')
   api0=guarded([build/'test_film_routed_api','0'],out/'api_baseline',120);api45=guarded([build/'test_film_routed_api','4.5'],out/'api_candidate',120);refcompile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120)
 result=dict(status='PASS' if all(p and p['exit_code']==0 for p in (mathcompile,mathrun,configure,compile,api0,api45,refcompile)) else 'FAIL',scope='independent routed full mechanics and actual Force/dForce/matrix/query-purity APIs;NOT scene/dynamics/clearance/grasp qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,generated_source_identity=generated,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),build_relative=str(build.relative_to(ROOT)),math_compile=mathcompile,math_process=mathrun,configure=configure,compile=compile,api_baseline=api0,api_candidate=api45,reference_compile=refcompile,original_Assembly_layout='UNCHANGED;no new member or legacy Field source modification',material_volume='same modeled core only;wire/guide mass and volume NOT MEASURED',dynamics='NOT RUN',full_wire_clearance='BLOCKED:finite radius/guide bodies/unmodeled collision',full_time='NOT RUN for new route',whole_energy='BLOCKED')
 if compile and compile['exit_code']==0:result.update(binary_sha256=sha(build/'libReGripFilmRoutedTransmission.so'),api_binary_sha256=sha(build/'test_film_routed_api'))
 if refcompile and refcompile['exit_code']==0:result['reference_binary_sha256']=sha(out/'reference')
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_hashes','math_compile','math_process','configure','compile','api_baseline','api_candidate','reference_compile')}))
if __name__=='__main__':main()
