"""One-factor equal-core-volume rail designs;reuse existing strict FD/objectivity."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();provider=ROOT/'results/autonomous_film_20261119_stationary_gauss_resume1637';pm=json.loads((provider/'summary.json').read_text())
 if pm['status']!='PASS':raise ValueError('qualified physical baseline required')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('baseline source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_rail_aspect',archive/'models/film_rail_aspect');tests=archive/'tests';tests.mkdir();text=(ROOT/'tests/test_film_lateral.cpp').read_text();shutil.copy2(ROOT/'tests/test_film_lateral.cpp',tests/'original_test_film_lateral.cpp');old='Assembly m(21);m.guideOffset=5;m.guideIntervals=4;m.rootGuideSecondOrder=true;'
 if text.count(old)!=1:raise ValueError('exact existing test layout required')
 text=text.replace('#include "../models/film_lateral_tendon/Route.h"','#include "../models/film_lateral_tendon/Route.h"\n#include "../models/film_rail_aspect/Design.h"').replace('int main(){try{','int main(int argc,char**argv){try{').replace(old,'auto m=regrip_rail_aspect::design(std::stod(argv[1]));').replace('m.elements(q,.001,visit)','m.elements(q,.0001,visit)').replace('elements(m,q,.001,lateral,visit)','elements(m,q,.0001,lateral,visit)');cpp=tests/'test_rail_aspect.generated.cpp';cpp.write_text(text);compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'test'],out/'compile',120);runs={}
 if compile['exit_code']==0:
  for h in (.075,.1,.125):
   folder=out/('rail'+str(h));run=guarded([out/'test',str(h)],folder,480);runs[str(h)]=dict(process=run,metrics=json.loads((folder/'stdout.log').read_text()) if run['exit_code']==0 else None)
 r=dict(status='PASS' if len(runs)==3 and all(x['process']['exit_code']==0 for x in runs.values()) else 'FAIL',scope='implemented equal-volume rail-aspect candidates FD/force-Hessian/objectivity ONLY;NOT nonlinear dynamic/wrapping/SOFA/grasp improvement',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),baseline_summary_sha256=sha(provider/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,trials=runs,binary_sha256=sha(out/'test') if (out/'test').exists() else None,thicknesses_mm=[.075,.1,.125],core_volume_three_fingers_mm3=439.3397917746089,comparison='same skin/material/core cross-sectional area,T100uN per rail,root map/attachment stiffness/guide offsets;rail width and through-thickness offsets follow declared geometry',material='E250MPa,nu0,assumed not measured PET/TPU',mechanism='physical rail dimensions,NOT Young modulus tuning or fictitious jamming',actual_SOFA='NOT RUN',nonlinear_performance='NOT RUN',selected_design=None);write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','trials')}))
if __name__=='__main__':main()
