"""Source-bound separate SOFA joint-distribution Field/ODE,0/2 API cases."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();base=ROOT/'results/autonomous_film_20261118_lateral_api_build1356';bm=json.loads((base/'summary.json').read_text());math=ROOT/'results/autonomous_film_20261118_distributed_root_matched1503';mm=json.loads((math/'summary.json').read_text())
 if bm['status']!='PASS' or mm['status']!='PASS' or sha(ROOT/'models/film_distributed_attachment/Kernel.h')!=mm['source_hashes']['models/film_distributed_attachment/Kernel.h']:raise ValueError('qualified identical new joint kernel required')
 for f,d in bm['source_hashes'].items():
  if sha(base/'sources'/f)!=d:raise ValueError('original source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(base/'sources',archive);dest=archive/'models/film_distributed_attachment';dest.mkdir();shutil.copy2(ROOT/'models/film_distributed_attachment/Kernel.h',dest/'Kernel.h')
 def transform(text):
  return text.replace('film_lateral_tendon','film_distributed_attachment').replace('regrip_lateral_tendon','regrip_distributed_attachment').replace('film_lateral','film_distributed_attachment').replace('FilmLateral','FilmDistributed').replace('frozenLateral','frozenAttachment').replace('lateralOffset','attachmentMode').replace('"Route.h"','"Kernel.h"').replace('lateral0 or6mm','attachment mode0/2').replace('outboard lateral','distributed attachment')
 for name in ('Field.generated.cpp','Step.h','Owner.cpp','CMakeLists.txt'):(dest/name).write_text(transform((archive/'models/film_lateral_tendon'/name).read_text()))
 api=archive/'tests/test_film_distributed_attachment_api.generated.cpp';api.write_text(transform((archive/'tests/test_film_lateral_api.generated.cpp').read_text()).replace(':6)',':2)').replace('?6:0','?2:0'))
 cpp=archive/'diagnostics/film_three_finger/DistributedPlan.cpp';cpp.write_text(transform((archive/'diagnostics/film_three_finger/LateralPlan.cpp').read_text()));build=ROOT/'build'/('film_distributed_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',dest,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;checks=[]
 if compile and compile['exit_code']==0:
  for binary in (build/'libReGripFilmDistributedTransmission.so',build/'test_film_distributed_attachment_api'):
   deps=subprocess.check_output(['ldd',binary],text=True);(out/(binary.name+'.ldd.txt')).write_text(deps)
   if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  for mode in ('0','2'):checks.append(guarded([build/'test_film_distributed_attachment_api',mode],out/('api_'+mode),120))
  checks.append(guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120))
 r=dict(status='PASS' if len(checks)==3 and all(c['exit_code']==0 for c in checks) else 'FAIL',design='distributed',control_ramp_s=.01,scope='NEW joint distribution actual Field/API and compiled no-object owner;NOT dynamic/wrapping',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},math_summary_sha256=sha(math/'summary.json'),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),build_relative=str(build.relative_to(ROOT)),configure=configure,compile=compile,checks=checks,nominal_total_K_per_rail=.005,root_K=.001,free_sum_K=.004,adhesive_mass=None,whole_energy='BLOCKED')
 if r['status']=='PASS':r.update(binary_sha256=sha(build/'libReGripFilmDistributedTransmission.so'),reference_binary_sha256=sha(out/'reference'))
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','checks')}))
if __name__=='__main__':main()
