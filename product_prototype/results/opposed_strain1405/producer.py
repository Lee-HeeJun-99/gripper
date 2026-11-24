"""Finite deformation invariants from actual accepted Native tetrahedra.
No allowable material strain is invented;strain is not a stress measurement.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in ('opposed_control_mid1393','opposed_open_mid1394','opposed_nonuniform_mid1398','opposed_release1401','opposed_zero_reference1403'):
  src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);mesh=json.loads((src/'mesh.json').read_text());t=np.array(mesh['tetrahedra']);local=np.array(mesh['local_positions_mm']);D0=(q0[t[:,1:]]-q0[t[:,0,None]]).transpose(0,2,1);inv=np.linalg.inv(D0);rows=list(csv.DictReader((src/'finger0.csv').open()));maximum=-1.;at=None;stretchmin=1.;stretchmax=1.;detmin=1.
  for r in rows:
   q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);D=(q[t[:,1:]]-q[t[:,0,None]]).transpose(0,2,1);F=D@inv;lam=np.linalg.svd(F,compute_uv=False);green=.5*(lam*lam-1);e=np.max(abs(green),axis=1);i=int(np.argmax(e));stretchmin=min(stretchmin,float(lam.min()));stretchmax=max(stretchmax,float(lam.max()));detmin=min(detmin,float(np.linalg.det(F).min()))
   if e[i]>maximum:maximum=float(e[i]);at=dict(time_s=float(r['time_s']),element=i,material_centroid_mm=local[t[i]].mean(0).tolist(),principal_stretches=lam[i].tolist())
  records.append(dict(case=case,outputs=len(rows),maximum_absolute_principal_Green_strain=maximum,at=at,minimum_principal_stretch=stretchmin,maximum_principal_stretch=stretchmax,minimum_determinant_ratio=detmin,allowable_material_strain=None,input_hashes={f:sha(src/f) for f in ('scene.scn','mesh.json','finger0.csv')}))
 d=dict(status='ACTUAL_ACCEPTED_ELEMENT_STRAIN_INVENTORY_ONLY',records=records,scope='F=currentedgeMatrix@inverse(restedgeMatrix),principalGreen=(stretch^2-1)/2. Native accepted coarsemesh;not measuredstress,materialallowable,strainconvergence,fullguidejointstrength or fabrication qualification. No smoothing/reset of bad states.',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
