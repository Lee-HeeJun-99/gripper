"""Actual deformation-gradient audit of the two full100g trials, read only.
No stress/energy/allowable inferred from an uncalibrated material.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();tet=np.array(json.loads((BASE/'results/crimp_hold1904/mesh.json').read_text())['tetrahedra']);records=[];paths=[BASE/'results/crimp_hold1904/mesh.json']
 for case in ['crimp_hold1904','braked_hold1925']:
  src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();paths.extend([src/'scene.scn',src/'summary.json']);assert json.loads((src/'summary.json').read_text())['process']['exit_code']==0
  for i in range(3):
   rest=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);D0=(rest[tet[:,1:]]-rest[tet[:,0,None]]).transpose(0,2,1);inv=np.linalg.inv(D0);file=src/f'skin{i}.csv';paths.append(file);peak=dict(green_lagrange_principal_abs=0);late=dict(green_lagrange_principal_abs=0);det_min=1.;principal_min=1.;principal_max=1.;steps=0
   with file.open() as stream:
    for r in csv.DictReader(stream):
     steps+=1;t=float(r['time_s']);q=np.fromstring(r['q'],sep=' ').reshape(-1,3);D=(q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1);F=D@inv;s=np.linalg.svd(F,compute_uv=False);green=.5*(s*s-1);size=abs(green).max(1);e=int(size.argmax());value=float(size[e]);det_min=min(det_min,float(np.linalg.det(F).min()));principal_min=min(principal_min,float(s.min()));principal_max=max(principal_max,float(s.max()));item=dict(green_lagrange_principal_abs=value,time_s=t,tetrahedron=e,rest_element_centroid_m=rest[tet[e]].mean(0).tolist(),principal_stretches=s[e].tolist())
     if value>peak['green_lagrange_principal_abs']:peak=item
     if 1.6-1e-12<=t<=2.+1e-12 and value>late['green_lagrange_principal_abs']:late=item
   assert steps==800;records.append(dict(case=case,finger=i,actual_steps=steps,minimum_F_determinant=det_min,minimum_principal_stretch=principal_min,maximum_principal_stretch=principal_max,maximum_rest_D_condition_number=float(np.linalg.cond(D0).max()),peak_all_motion=peak,peak_original_holding=late))
 d=dict(status='PASS_ACTUAL_FEM_STRAIN_MEASUREMENT_ONLY' if all(r['minimum_F_determinant']>0 and np.isfinite(r['maximum_principal_stretch']) for r in records) else 'FAIL_FEM_DEFORMATION_VALIDITY',records=records,measured_material_allowable_strain=None,stress_Pa=None,actual_FEM_energy_J=None,source_sha256=sha(Path(__file__)),input_hashes={str(f.relative_to(BASE)):sha(f) for f in paths},scope='Actual tetrahedral deformation gradients and principal Green-Lagrange strains from saved q versus manufactured rest geometry. No new Native, no shape prescription or stress/energy fabrication. Positive signed volume alone is not small strain. Material allowable/fatigue/joint data absent, so no material or convergence qualification. Extreme strain would require explicit model reassessment, not ignored bad elements.');out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k not in ['input_hashes','records']},indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
