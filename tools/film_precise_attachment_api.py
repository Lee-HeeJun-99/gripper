"""Separate actual SOFA ForceField with reference-exact displacement bonds."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();provider=ROOT/'results/autonomous_film_20261119_rail_aspect_api1654';pm=json.loads((provider/'summary.json').read_text());math=ROOT/'results/autonomous_film_20261119_attachment_math1680';mm=json.loads((math/'summary.json').read_text())
 if pm['status']!='PASS' or mm['status']!='PASS':raise ValueError('qualified source and new kernel regression required')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('archived actual source changed')
 for name in ('Elements.h',):
  if sha(ROOT/'models/film_precise_attachment'/name)!=mm['source_hashes']['models/film_precise_attachment/'+name]:raise ValueError('qualified attachment changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources',archive);shutil.copytree(ROOT/'models/film_precise_attachment',archive/'models/film_precise_attachment');folder=archive/'models/film_precise_attachment'
 code=(archive/'models/film_rail_aspect/Field.generated.cpp').read_text().replace('#include "Design.h"','#include "../film_rail_aspect/Design.h"\n#include "Elements.h"').replace('FilmAspectTendon','FilmPreciseAttachmentTendon').replace('registerFilmAspectField','registerFilmPreciseAttachmentField').replace('regrip_lateral_tendon::elements(m,q,stepT,','regrip_precise_attachment::elements(m,q,stepT,');(folder/'Field.generated.cpp').write_text(code)
 code=(archive/'tests/test_film_rail_aspect_api.generated.cpp').read_text().replace('film_rail_aspect/Field.generated.cpp','film_precise_attachment/Field.generated.cpp').replace('FilmAspectTendon','FilmPreciseAttachmentTendon');(archive/'tests/test_precise_api.generated.cpp').write_text(code)
 (folder/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.22)
project(ReGripPreciseAttachment LANGUAGES CXX)
find_package(Sofa.Core REQUIRED)
find_package(Sofa.DefaultType REQUIRED)
find_package(Sofa.LinearAlgebra REQUIRED)
find_package(Sofa.Component.StateContainer REQUIRED)
find_package(Eigen3 REQUIRED)
add_executable(test_precise_api ../../tests/test_precise_api.generated.cpp)
target_compile_features(test_precise_api PRIVATE cxx_std_17)
target_compile_options(test_precise_api PRIVATE -O2 -ffp-contract=off)
target_link_libraries(test_precise_api PRIVATE Eigen3::Eigen Sofa.Core Sofa.DefaultType Sofa.LinearAlgebra Sofa.Component.StateContainer)
''');build=ROOT/'build'/('precise_attachment_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',folder,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;run=guarded([build/'test_precise_api','.1'],out/'api',120) if compile and compile['exit_code']==0 else None
 r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='actual SOFA Force/dForce/matrix/FD/query purity ONLY;NOT dynamic owner/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},actual_baseline_summary_sha256=sha(provider/'summary.json'),kernel_math_summary_sha256=sha(math/'summary.json'),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),configure=configure,compile=compile,process=run,build_relative=str(build.relative_to(ROOT)),binary_sha256=sha(build/'test_precise_api') if (build/'test_precise_api').exists() else None,selected_design=None)
 if run and run['exit_code']==0:
  dependencies=subprocess.check_output(['ldd',build/'test_precise_api'],text=True);(out/'ldd.txt').write_text(dependencies)
  if 'not found' in dependencies or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in dependencies.splitlines()):raise ValueError('SDK ABI mismatch')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process')}))
if __name__=='__main__':main()
