"""Isolated quarter-guide profile; preserve old tests and immutable evidence."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
 shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'))
 source=(ROOT/'tests/test_film_lateral.cpp').read_text()
 source=source.replace('film_lateral_tendon/Route.h','film_profiled_tendon/Route.h').replace('using namespace regrip_lateral_tendon;','using namespace regrip_profiled_tendon;')
 source=source.replace('if(original)m.elements(q,.001,visit);','if(original)regrip_lateral_tendon::elements(m,q,.001,6,visit);').replace('for(double lateral:{0.,6.})','for(double lateral:{0.,.5})').replace('m.cableLength(q)','regrip_lateral_tendon::length(m,q,6)')
 test=archive/'tests/test_profile.cpp';test.parent.mkdir();test.write_text(source)
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',test,'-o',out/'test'],out/'compile',120)
 run=guarded([out/'test'],out/'process',480) if compile['exit_code']==0 else None
 r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='profiled-route independent FD/objectivity/zero-profile parity ONLY;NOT actual SOFA/contact/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,normal_offsets_mm=[5.5,5,4.5,5,5.5],outboard_mm=6,core_material_volume_unchanged=True,hardware_mass=None,matched_work=False,actual_SOFA='NOT RUN')
 if run and run['exit_code']==0:r.update(metrics=json.loads((out/'process/stdout.log').read_text()),binary_sha256=sha(out/'test'))
 geom=(ROOT/'diagnostics/film_three_finger/LateralGeometry.cpp').read_text().replace('film_lateral_tendon/Route.h','film_profiled_tendon/Route.h').replace('using namespace regrip_lateral_tendon;','using namespace regrip_profiled_tendon;').replace('for(double lateral:{0.,6.})','for(double lateral:{0.,.5})').replace('route(m,zero,1,lateral,','elements(m,zero,1,lateral,')
 gp=archive/'diagnostics/film_three_finger/ProfileGeometry.cpp';gp.parent.mkdir(parents=True);gp.write_text(geom)
 gc=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',gp,'-o',out/'geometry'],out/'geometry_compile',120)
 gr=guarded([out/'geometry'],out/'geometry_process',480) if gc['exit_code']==0 else None
 r.update(geometry_compile=gc,geometry_process=gr)
 if not gr or gr['exit_code']:r['status']='FAIL'
 else:r['geometry_csv']=(out/'geometry_process/stdout.log').read_text()
 r['source_hashes']={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='source_hashes'}))
if __name__=='__main__':main()
