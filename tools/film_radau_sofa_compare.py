"""Actual sole-owner Radau state versus independent nonlinear FEM state."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reference',required=True);a=p.parse_args();case=ROOT/'results'/('autonomous_film_'+a.case);ref=ROOT/'results'/('autonomous_film_'+a.reference);meta=json.loads((case/'identity.json').read_text());rm=json.loads((ref/'summary.json').read_text())
 if json.loads((case/'summary.json').read_text())['status']!='PASS' or rm['status']!='PASS' or not meta.get('persistent_radau') or meta['radau_reference']!=a.reference:raise ValueError('completed actual and qualified independent source required')
 modes=json.loads((ROOT/'results'/('autonomous_film_'+rm['modal_input'])/'summary.json').read_text())
 if modes['actual_case']!=meta['source_case'] or meta['duration']!=rm.get('horizon',.000009765625):raise ValueError('actual initial-state source or physical window differs')
 if np.linalg.norm(np.fromstring(meta['initial_body_velocity'],sep=' ')[3:])!=0:raise ValueError('coordinate comparison qualifies zero-spin coupon only;do not invent angular coordinates')
 for name,digest in rm['sources'].items():
  if name.endswith('.h') and name not in ('models/film_coupled_contact/ReintegratedBirth.h','models/film_coupled_contact/ReintegratedStep.h') and meta['sources'].get(name)!=digest:raise ValueError('compiled reference source drift:'+name)
 r=next(r for r in csv.DictReader((ref/'states.csv').open()) if int(r['steps'])==meta['steps']);s=list(csv.DictReader((case/'coupled.states.csv').open()))[-1];q=np.fromstring(r['q'],sep=' ');v=np.fromstring(r['v'],sep=' ');nx=int(ET.parse(case/'scene.scn').find('.//FilmRailTendon').get('nx'));nf=3*(nx-1)*11-11;local=np.fromstring(s['local_displacement'],sep=' ').reshape(-1,3);velocity=np.fromstring(s['local_velocity'],sep=' ').reshape(-1,3);actualQ=[];actualV=[]
 for offset,ny in ((0,5),(5*nx,3),(8*nx,3)):
  for i in range(1,nx):
   for j in range(ny):
    for d in range(3):
     if i!=1 or d!=2:actualQ.append(local[offset+i*ny+j,d]);actualV.append(velocity[offset+i*ny+j,d])
 actualQ.extend(np.fromstring(s['body_center'],sep=' '));actualQ.extend([0,0,0]);actualV.extend(np.fromstring(s['body_velocity'],sep=' '));actualV.extend(np.fromstring(s['body_omega'],sep=' '));stages=list(csv.DictReader((case/'coupled.stages.csv').open()));errors=dict(position=float(np.max(abs(np.array(actualQ)-q))),velocity=float(np.max(abs(np.array(actualV)-v))),end_force=abs(float(stages[-1]['normal_force'])-float(r['normal_force'])))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');status='PASS' if max(errors.values())<1e-12 else 'FAIL';write_json(out/'summary.json',dict(status=status,scope='actual isolated persistent Radau versus independent FEM;NOT global time/energy/grasp',case=a.case,reference=a.reference,errors=errors,actual_sources={f:sha(case/f) for f in ('identity.json','scene.scn','coupled.states.csv','coupled.rows.csv','coupled.stages.csv')},reference_hash=sha(ref/'states.csv')));print(json.dumps(dict(status=status,errors=errors)))
if __name__=='__main__':main()
