"""Separate FREE owner with strict interval broadphase;never bypass a hit."""
import argparse,hashlib,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--math',default='20261118_separated_path_math1369');a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_routed_release_actual1360';m=json.loads((src/'summary.json').read_text());math=ROOT/'results'/('autonomous_film_'+a.math);mp=json.loads((math/'summary.json').read_text())
 if m['status']!='PASS' or mp['status']!='PASS' or sha(ROOT/'models/film_routed_contact/SeparatedPath.h')!=mp['source_hashes']['models/film_routed_contact/SeparatedPath.h']:raise ValueError('qualified release/math required')
 for name in ('SeparatedPath.h','RotatingPlane.h'):
  key='models/film_routed_contact/'+name
  if sha(ROOT/key)!=mp['source_hashes'][key]:raise ValueError('current geometric witness differs from qualified math')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('compiled archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');shutil.copy2(ROOT/'models/film_routed_contact/SeparatedPath.h',archive/'models/film_routed_contact/SeparatedPath.h');shutil.copy2(ROOT/'models/film_routed_contact/RotatingPlane.h',archive/'models/film_routed_contact/RotatingPlane.h');cpp=archive/'models/film_three_finger_release/ThreeFilmRelease.cpp';text=cpp.read_text();old='auto event=regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);if(event)throw std::runtime_error("FREE dense numerical path has reimpact;separate event solve required,not committed");'
 if text.count(old)!=1:raise ValueError('exact free CCD source differs')
 text='#include "../film_routed_contact/SeparatedPath.h"\n'+text.replace(old,'auto certificate=regrip_routed_contact::separatedNumericalPath(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);if(!certificate.clear){'+old+'}')
 cpp.write_text(text);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};allowed={'models/film_three_finger_release/ThreeFilmRelease.cpp','models/film_routed_contact/SeparatedPath.h','models/film_routed_contact/RotatingPlane.h'}
 if any(m['source_hashes'].get(k)!=v for k,v in sources.items() if k not in allowed):raise ValueError('unrelated physical source changed')
 build=ROOT/'build'/('routed_separation_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_release','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='separate strict FREE numerical-path exclusion build ONLY',change_scope='strict separating-plane exclusion ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),parent_summary_sha256=sha(src/'summary.json'),math_summary_sha256=sha(math/'summary.json'),source_hashes=sources,configure=configure,compile=compile,build_relative=str(build.relative_to(ROOT)),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'))
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmRelease.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK mismatch')
  r.update(status='PASS',binary_sha256=sha(binary));r['identity']=hashlib.sha256(json.dumps(dict(sources=sources,binary=r['binary_sha256']),sort_keys=True).encode()).hexdigest()
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile')}))
if __name__=='__main__':main()
