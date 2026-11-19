"""Same historical FD/objectivity gates for independent displacement-frame bonds."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--precise-tendon',action='store_true');p.add_argument('--extended',action='store_true');p.add_argument('--current-ad',action='store_true');a=p.parse_args()
 provider=ROOT/'results/autonomous_film_20261119_rail_aspect_api1654';pm=json.loads((provider/'summary.json').read_text())
 if pm['status']!='PASS':raise ValueError('qualified baseline required')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('baseline source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_precise_attachment',archive/'models/film_precise_attachment');tests=archive/'tests';tests.mkdir();original=ROOT/'tests/test_film_lateral.cpp';shutil.copy2(original,tests/'original_test_film_lateral.cpp');code=original.read_text()
 old='else elements(m,q,.001,lateral,visit)'
 if code.count(old)!=1:raise ValueError('historical test adapter changed')
 code=code.replace('#include "../models/film_lateral_tendon/Route.h"','#include "../models/film_precise_attachment/Elements.h"').replace(old,'else regrip_precise_attachment::elements(m,q,.001,lateral,visit)')
 if a.precise_tendon:
  shutil.copytree(ROOT/'models/film_precise_tendon',archive/'models/film_precise_tendon');code=code.replace('film_precise_attachment/Elements.h','film_precise_tendon/Route.h').replace('regrip_precise_attachment::elements','regrip_precise_tendon::elements')
 if a.extended or a.current_ad:
  if not a.precise_tendon:raise ValueError('separate precise tendon variant only')
  for name in ('AD.h','MembraneAD.h'):shutil.copy2(ROOT/'models/film_shell'/name,archive/'models/film_shell'/name)
 cpp=tests/'precise.generated.cpp';cpp.write_text(code);binary=out/'test';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off',*(['-DREGRIP_FILM_EXTENDED_AD'] if a.extended else []),'-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary],out/'process',480) if compile['exit_code']==0 else None
 r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='original force/Hessian FD,rigid objectivity,force/moment balance and old baseline absolute gates;NOT SOFA/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},binary_sha256=sha(binary) if binary.exists() else None,baseline_summary_sha256=sha(provider/'summary.json'),compile=compile,process=run,metrics=json.loads((out/'process/stdout.log').read_text()) if run and run['exit_code']==0 else None,physical_parameters='historical test unchanged:100mm,21rows,E250MPa,nu0,bondK.001N/mm,T.001N,lateral0/6mm',variant='reference-exact displacement-frame attachment;unchanged shell and tendon',selected_design=None)
 r['variant']='extended local AD precise tendon/attachment;original FD/balance/objectivity gates unchanged' if a.extended else 'precise tendon and attachment' if a.precise_tendon else r['variant']
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
