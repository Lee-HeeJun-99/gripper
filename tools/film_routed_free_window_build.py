"""Explicit separated FREE horizon extension;unchanged physical/control law."""
import argparse,hashlib,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();provider=ROOT/'results/autonomous_film_20261118_routed_rotating_build1383';m=json.loads((provider/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_routed_unload_end1391';pm=json.loads((parent/'summary.json').read_text())
 if m['status']!='PASS' or pm['status']!='PASS' or pm['binary_sha256']!=m['binary_sha256']:raise ValueError('actual complete released C2 endpoint and exact compiled provider required')
 for f,d in m['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('compiled physical source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');cpp=archive/'models/film_three_finger_release/ThreeFilmRelease.cpp';text=cpp.read_text();anchor=' std::string inputCheckpointMagic()const override{return "REGRIP_ROUTED_FREE_V3";}'
 if text.count(anchor)!=1:raise ValueError('unique FREE-only horizon extension anchor required')
 cpp.write_text(text.replace(anchor,anchor+'\n double maximumResumeEndTime()const override{return .05;}'))
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 if any(m['source_hashes'].get(k)!=d for k,d in sources.items() if k!='models/film_three_finger_release/ThreeFilmRelease.cpp'):raise ValueError('unrelated physical source changed')
 build=ROOT/'build'/('routed_free_window_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_release','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='FREE-only bounded50ms endpoint extension build;NOT longer actual dynamics or time/energy qualification',change_scope='explicit FREE endpoint50ms ONLY',maximum_resume_end_s=.05,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),parent_summary_sha256=sha(parent/'summary.json'),parent_binary_sha256=pm['binary_sha256'],source_hashes=sources,configure=configure,compile=compile,build_relative=str(build.relative_to(ROOT)),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),control='UNCHANGED original C2 Tmax.0001,ramp.01,release.02..03;zero tension after.03',physical_source_change='virtual maximumResumeEndTime override ONLY in FREE class;no guard counter manipulation')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmRelease.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK mismatch')
  r.update(status='PASS',binary_sha256=sha(binary));r['identity']=hashlib.sha256(json.dumps(dict(sources=sources,binary=r['binary_sha256']),sort_keys=True).encode()).hexdigest()
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile')}))
if __name__=='__main__':main()
