"""Virtual fixed sphere overlay of actual NO-OBJECT trajectories,not contact."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_routed_run import parameter_value
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--amplitude',type=float,choices=(0.,.5,2.,4.5,6.),required=True);p.add_argument('--design',choices=('quadratic','lateral','profiled','distributed'),default='quadratic');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m.get('design','quadratic')!=a.design or a.amplitude not in {'quadratic':(0.,4.5),'lateral':(0.,6.),'profiled':(0.,.5),'distributed':(0.,2.)}[a.design]:raise ValueError('geometry route must match actual physical design')
 if m['status']!='PASS' or parameter_value(m)!=a.amplitude:raise ValueError('complete matching actual route required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual raw changed')
 provider=ROOT/'results'/('autonomous_film_'+(m['source_provider_case'] if a.design in ('profiled','distributed') else '20261118_lateral_api_build1356' if a.design=='lateral' else '20261118_routed_math_api1240'));proof=json.loads((provider/'summary.json').read_text())
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('routed physical source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(provider/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/RoutedGeometry.cpp';cpp.parent.mkdir(parents=True);text=(ROOT/'diagnostics/film_three_finger/RoutedGeometry.cpp').read_text()
 if a.design in ('lateral','profiled','distributed'):
  old='auto p=m.guide(local,part,i,-offset(m,i,amplitude));'
  if text.count(old)!=1:raise ValueError('geometry guide expression changed')
  text=text.replace('#include "../../models/film_routed_tendon/Step.h"','#include "../../models/film_lateral_tendon/Step.h"').replace('using namespace regrip_routed_tendon;','using namespace regrip_lateral_tendon;').replace(old,'auto p=guide(m,local,part,i,amplitude);')
  if a.design=='profiled':text=text.replace('film_lateral_tendon/Step.h','film_profiled_tendon/Step.h').replace('regrip_lateral_tendon','regrip_profiled_tendon')
  if a.design=='distributed':text=text.replace('film_lateral_tendon/Step.h','film_distributed_attachment/Step.h').replace('using namespace regrip_lateral_tendon;','using namespace regrip_distributed_attachment;').replace('auto p=guide(m,local,part,i,amplitude);','auto p=regrip_lateral_tendon::guide(m,local,part,i,6.);')
 cpp.write_text(text);rows=list(csv.DictReader((src/'actual.csv').open()));(out/'samples.txt').write_text(str(len(rows))+'\n'+'\n'.join(r['time']+' '+r['q'] for r in rows)+'\n');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'geometry'],out/'compile',120);run=guarded([out/'geometry',out/'samples.txt',str(a.amplitude),out/'geometry.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='VIRTUAL original fixed R30sphere overlay on actual NO-OBJECT states;NOT actual contact/wrapping/CCD',design=a.design,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),amplitude_mm=a.amplitude,compile=compile,process=run,source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},contact_force=None,contact_area=None,wire_radius=None,guide_body_clearance=None)
 r['design_parameter_value']=a.amplitude;r['design_parameter_units']='dimensionless' if a.design=='distributed' else 'mm'
 if a.design=='distributed':r['amplitude_mm']=None
 if run and run['exit_code']==0:
  values=list(csv.DictReader((out/'geometry.csv').open()));triangle=min(float(v['triangle_buffer_gap_mm']) for v in values);wire=min(float(v['wire_centreline_physical_gap_mm']) for v in values);r.update(status='PASS' if len(values)==len(rows) else 'FAIL',minimum_triangle_buffer_gap_mm=triangle,minimum_wire_centreline_physical_gap_mm=wire,sampled_virtual_geometry_feasible=triangle>=-1e-10 and wire>=0,endpoint=values[-1],binary_sha256=sha(out/'geometry'),raw_hashes={'geometry.csv':sha(out/'geometry.csv')},continuous_path_clearance='NOT QUALIFIED')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
