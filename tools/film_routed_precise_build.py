"""Separate archived generic owner with QUERY-local identical Q/H reuse."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();provider=ROOT/'results/autonomous_film_20261118_routed_resume1278';proof=json.loads((provider/'summary.json').read_text());math=ROOT/'results/autonomous_film_20261118_precise_cache_math1337';mp=json.loads((math/'summary.json').read_text())
 if proof['status']!='PASS' or mp['status']!='PASS' or sha(ROOT/'models/film_routed_contact/PreciseQueryCache.h')!=mp['source_hashes']['models/film_routed_contact/PreciseQueryCache.h']:raise ValueError('qualified original routed owner and exact cache unit test required')
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('qualified generic source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');header=archive/'models/film_routed_contact/PreciseQueryCache.h';shutil.copy2(ROOT/'models/film_routed_contact/PreciseQueryCache.h',header);path=archive/'models/film_three_finger/SharedFilmSystem.h';text=path.read_text()
 changes={'#include "PreciseDistanceOrder.h"':'#include "PreciseDistanceOrder.h"\n#include "../film_routed_contact/PreciseQueryCache.h"\n#include <optional>','std::vector<TriangleCoordinates>exact;':'std::vector<TriangleCoordinates>exact;std::optional<PreciseQueryCache>queryCache;auto compare=[&](unsigned a,unsigned b){if(!queryCache)throw std::runtime_error("query cache used before exact geometry");return queryCache->compare(a,b,[&]{return order(exact[a],exact[b]);});};','id=0;for(unsigned k=1;k<exact.size();++k)if(order(exact[k],exact[id])<0)id=k;':'queryCache.emplace(exact);id=0;for(unsigned k=1;k<exact.size();++k)if(compare(k,id)<0)id=k;','(!preciseTies||order(exact[k],exact[id])==0)':'(!preciseTies||compare(k,id)==0)'}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('exact selector generation anchor differs')
  text=text.replace(old,new)
 path.write_text(text);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};allowed={'models/film_three_finger/SharedFilmSystem.h','models/film_routed_contact/PreciseQueryCache.h'}
 if any(proof['source_hashes'].get(k)!=d for k,d in sources.items() if k not in allowed):raise ValueError('unrelated physical source changed')
 build=ROOT/'build'/('routed_precise_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_resume','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='separate query-local precise-order cache build/math ONLY;NOT adopted speed/physical qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,provider_summary_sha256=sha(provider/'summary.json'),math_summary_sha256=sha(math/'summary.json'),configure=configure,compile=compile,build_relative=str(build.relative_to(ROOT)),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),force_hessian_or_contact_law_changed=False,cache_lifetime='one immutable exact-coordinate geometry query;no cross-state key/tolerance')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmResume.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('cache build SDK ABI mismatch')
  r.update(status='PASS',binary_sha256=sha(binary))
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile')}))
if __name__=='__main__':main()
