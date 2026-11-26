"""Independent saved-traction reconstruction; does not import the LP producer."""
import argparse,json,math,sys,shutil
import numpy as np
from baseline_registry import ROOT,S1,REPO,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN
from OCP.gp import gp_Pnt

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
 assert not (ROOT/'runtime/STOP').exists()
 src=ROOT/'validation/transmission'/a.source;d=json.loads((src/'summary.json').read_text())
 out=ROOT/'validation/transmission'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 assert all(sha(REPO/v['path'])==v['SHA256'] for v in d['inputs'])
 g=d['geometry'];r=g['shaft_radius_mm']/1000;R=g['bore_radius_mm'];flat=g['D_flat_X_from_axis_mm'];lo,hi=g['minimum_engagement_Y_mm'];mid=(lo+hi)/2
 candidate=json.loads((REPO/d['candidate']['path']).read_text());hub=read(REPO/candidate['part_references']['F0_CLUTCH_INPUT_HUB']['path'])
 rw=candidate['torque_model']['nominal_drum_wire_radius_mm']/1000;ax=d['axial_force_per_unit_tendon'];rows=[]
 for n in (48,96,192):
  case=json.loads((src/f'case_{n}.json').read_text());state=np.load(src/f'state_{n}.npz');x=state['solution'];k=case['rays']
  force=np.zeros(3);moment=np.zeros(3);normal=0.;badforce=np.zeros(3);eligible=True;disk=True
  for j,w in enumerate(x[:-1]):
   if abs(w)<1e-12:continue
   theta,y=case['contact_points'][j//k];phi=2*math.pi*(j%k)/k
   c,s=math.cos(theta),math.sin(theta)
   # Direct scalar traction/lever formulas, independent of saved matrix.
   fn=np.array([-c,0,-s]);ft=np.array([-s*math.cos(phi),math.sin(phi),c*math.cos(phi)])
   f=w*(fn+ft);pos=np.array([r*c,y,r*s]);force+=f;moment+=np.cross(pos,f);normal+=w
   badforce+=w*(fn+ft*np.array([1,.99,1]))
   eligible &= r*1000*c<=flat+1e-8 and lo<=mid+y*1000<=hi
   eligible &= BRepClass3d_SolidClassifier(hub,gp_Pnt(110+(R+.001)*c,mid+y*1000,20+(R+.001)*s),1e-8).State()==TopAbs_IN
   disk &= np.linalg.norm(ft)<=1+1e-12
  T=float(x[-1]);fres=force+np.array([0,ax*T,0]);mres=moment+np.array([0,rw*T,0]);res=max(abs(fres).max(),abs(mres/rw).max(),abs(normal-1))
  upper=1/math.hypot(rw/r,ax)
  control=float(abs((badforce+np.array([0,ax*T,0]))).max())
  passed=eligible and disk and res<1e-8 and x.min()>-1e-10 and T<=upper+1e-8 and control>1e-5
  rows.append(dict(angles=n,passed=bool(passed),eligible_actual_BRep=bool(eligible),coulomb_disk=bool(disk),residual=float(res),negative_axial_traction_control_residual=control,T_lower=T,T_upper=upper,relative_bound_width=(upper-T)/upper))
 result=dict(status='SAVED_TRACTION_VERIFICATION_PASS' if all(r['passed'] for r in rows) else 'SAVED_TRACTION_VERIFICATION_FAIL',source=ref(src/'summary.json'),producer=ref(out/'producer.py'),input_hashes_pass=True,cases=rows,scope='Independent six-component force/moment, unit-normal budget, circular contact eligibility, Coulomb disks and analytic upper bound; NOT elastic closure, actual capacity or system release',acceptance_artifact_note='Predeclared criteria output renamed acceptance.json after execution; contents preserved. Archived producer.py is exact executed source, current script uses acceptance.json.',whole_system_release=False)
 dump(out/'summary.json',result);print(json.dumps(result,indent=2));return 0 if all(r['passed'] for r in rows) else 2
if __name__=='__main__':raise SystemExit(main())
