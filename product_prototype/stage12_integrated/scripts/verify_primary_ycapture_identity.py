"""Adaptive integral identity of new actual product; no tolerance relaxation."""
import json,sys,shutil
import numpy as np
from scipy.optimize import linear_sum_assignment
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,volume
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def props(shape,eps):
 p=GProp_GProps();err=BRepGProp.VolumeProperties_s(shape,p,eps,False,False);c=p.CentreOfMass();return np.array([p.Mass(),c.X(),c.Y(),c.Z()]),err

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(src.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());s={n:read(REPO/r['path']) for n,r in cad['part_references'].items()};ag=read(REPO/cad['assembly']['path']);actual=[];it=TopExp_Explorer(ag,TopAbs_SOLID)
 while it.More():actual.append(it.Current());it.Next()
 records=[];fine=None
 for eps in [1e-8,1e-10,1e-12]:
  A=np.array([props(p,eps)[0] for p in actual]);E=np.array([props(p,eps)[0] for p in s.values()]);D=np.max(abs(A[:,None,:]-E[None,:,:])/(1e-7+1e-8*abs(E[None,:,:])),axis=2);ii,jj=linear_sum_assignment(D);delta=abs(A[ii]-E[jj]);fine=dict(A=A,E=E);records.append(dict(eps=eps,max_scaled_identity_error=float(D[ii,jj].max()),maximum_volume_identity_error_mm3=float(delta[:,0].max()),maximum_centroid_error_mm=float(delta[:,1:].max()),sum_volume_difference_mm3=float(abs(A[:,0].sum()-E[:,0].sum())),max_reported_relative_integral_error=max(props(p,eps)[1] for p in actual)))
 old=json.loads((REPO/cad['parent']['path']).read_text());changes=[];deltaW=np.zeros(6)
 for row in cad['changed']:
  n=row['part_ID'];a,_=props(s[n],1e-12);b,_=props(read(REPO/old['part_references'][n]['path']),1e-12);rho=2700 if n=='OPEN_FRAME' else 7900;dm=(a[0]-b[0])*rho*1e-9;f=np.array([0,0,-dm*9.80665]);m=np.cross(a[1:]*.001,[0,0,-a[0]*rho*1e-9*9.80665])-np.cross(b[1:]*.001,[0,0,-b[0]*rho*1e-9*9.80665]);w=np.r_[f,m];deltaW+=w;changes.append(dict(part=n,adaptive_volume_mm3=float(a[0]),parent_volume_mm3=float(b[0]),delta_volume_mm3=float(a[0]-b[0]),conditional_rho_kg_m3=rho,delta_mass_kg=float(dm),delta_gravity_wrench_N_Nm=w.tolist()))
 raw=sum(volume(p) for p in s.values())-volume(ag);checks=dict(all78hashes=True,one_to_one_aggregate_identity=all(r['max_scaled_identity_error']<=1 for r in records),sum_identity_original_1e_5mm3=all(r['sum_volume_difference_mm3']<1e-5 for r in records),three_integration_levels_stable=max(abs(records[i]['sum_volume_difference_mm3']-records[-1]['sum_volume_difference_mm3']) for i in range(2))<1e-5)
 dump(out/'summary.json',dict(status='ACTUAL_P1_YCAPTURE_ADAPTIVE_IDENTITY_PASS' if all(checks.values()) else 'ACTUAL_P1_YCAPTURE_ADAPTIVE_IDENTITY_FAIL',candidate=ref(src),verifier=ref(out/'verifier.py'),checks=checks,records=records,default_integral_sum_discrepancy_mm3=raw,changed_actual_parts=changes,total_conditional_delta_gravity_wrench_N_Nm=deltaW.tolist(),required_Base_external_wrench_change_N_Nm=(-deltaW).tolist(),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Default nonadaptive volume discrepancy is retained in loads1. Adaptive integral resolves whether exact exported aggregate matches parts, not a physical strength certificate.','Densities conditional same source assumptions, not supported minima. Changed part mass/reaction delta only; no arbitrary Base cancellation or actual physical anchor.']));print(json.dumps(dict(checks=checks,records=records,raw=raw,changes=changes)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
