"""Finite actual P1 thread flank traction maps; no prescribed installed fixation."""
import sys,json,math,shutil
import numpy as np
from scipy.optimize import linprog
from numpy.polynomial.legendre import leggauss
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from validate_thread49f import classification
from primary_nutseat46b import STATIONS
P=.8;K=P/(2*math.pi);RPI=4.605/2

def integrate(order):
 q,w=leggauss(order);cols=[];patch=[]
 for side in [-1,1]:
  for turn in [3,4,5]:
   for j in range(16):
    lo=2*math.pi*(turn+j/16);hi=lo+2*math.pi/16;col=np.zeros(6);area=0.;points=[]
    for qr,wr in zip(q,w):
     r=2.32+.1*qr
     for qa,wa in zip(q,w):
      a=(lo+hi)/2+(hi-lo)/2*qa;z=K*a+side*(P/4+(r-RPI)/math.sqrt(3));er=np.array([math.cos(a),math.sin(a),0]);et=np.array([-math.sin(a),math.cos(a),0]);raw=er/math.sqrt(3)+side*K/r*et+[0,0,-side];normal=raw/np.linalg.norm(raw);dA=r*np.linalg.norm(raw)*.1*(hi-lo)/2*wr*wa;pos=np.array([r*math.cos(a),r*math.sin(a),z-3.65]);col+=np.r_[normal,np.cross(pos,normal)]*dA;area+=dA;points.append([*pos[:2],z])
    cols.append(col);patch.append(dict(side=side,turn=turn,theta_range=[lo,hi],r_range_mm=[2.22,2.42],area_mm2=area,wrench_per_MPa=col.tolist(),sample=points[len(points)//2]))
 return np.array(cols).T,patch

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_flank50';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_thread49f/summary.json';cad=json.loads(cp.read_text());pre,i,x,y,zlo,zhi,parent=STATIONS[0];tip=zhi-6;bn=f'{pre}_BOLT_{i}';nn=f'{pre}_NUT_{i}';br=cad['part_references'][bn];nr=cad['part_references'][nn];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [br,nr]);b=read(REPO/br['path']);n=read(REPO/nr['path']);A,patch=integrate(8);B,_=integrate(4);C,_=integrate(16);classification_rows=[];clear=(RPI-4.456/2)/math.sqrt(3)
 for p in patch:
  xx,yy,z=p['sample'];s=p['side'];eps=1e-4
  # At hypothetical relative axial take-up -side*clear, the external
  # flank coincides with this internal flank. Only relative geometry here.
  nut=[classification(n,[x+xx,y+yy,tip+z+s*e]) for e in [-eps,eps]]
  bolt=[classification(b,[x+xx,y+yy,tip+z+s*clear+s*e]) for e in [-eps,eps]]
  classification_rows.append(dict(side=s,point_mm=[x+xx,y+yy,tip+z],nut_across=nut,bolt_across=bolt,expected_nut=['IN','OUT'],expected_bolt=['OUT','IN']))
 cases=[]
 targets=[('Fx',[1,0,0,0,0,0]),('Fy',[0,1,0,0,0,0]),('Mx',[0,0,0,1,0,0]),('My',[0,0,0,0,1,0]),('Fz_free_torque',[0,0,1,0,0,0]),('Mz_free_axial',[0,0,0,0,0,1]),('Fz_with_screw_torque',[0,0,1,0,0,-K])]
 for label,target in targets:
  target=np.array(target,dtype=float);sol=linprog(np.array([p['area_mm2'] for p in patch]),A_eq=A,b_eq=target,bounds=(0,None),method='highs');cases.append(dict(case=label,target_N_Nmm=target.tolist(),feasible=bool(sol.success),solver_status=sol.message,residual=None if not sol.success else float(max(abs(A@sol.x-target))),conditional_peak_pressure_MPa=None if not sol.success else float(max(sol.x)),patch_pressure_MPa=None if not sol.success else sol.x.tolist()))
 screw=np.array([0,0,K,0,0,1]);sv=np.linalg.svd(A,compute_uv=False);work=float(max(abs(A.T@screw)));err48=float(max(abs(A-B).flat));err816=float(max(abs(A-C).flat));checks=dict(actual_BRep_both_flanks=all(r['nut_across']==r['expected_nut'] and r['bolt_across']==r['expected_bolt'] for r in classification_rows),quadrature_4_8_16=err48<1e-9 and err816<1e-11,screw_virtual_work=work<1e-11,rank5=np.linalg.matrix_rank(A,tol=1e-10)==5,unit_transverse_and_bending_feasible=all(r['feasible'] and r['residual']<1e-9 for r in cases[:4]),axial_without_torque_rejected=not cases[4]['feasible'],torque_without_axial_rejected=not cases[5]['feasible'],unit_axial_with_torque_feasible=cases[6]['feasible'] and cases[6]['residual']<1e-9)
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_FLANK_TRACTION_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_FINITE_FLANK_TRACTION_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),actual_pair=dict(bolt=br,nut=nr),checks={k:bool(v) for k,v in checks.items()},finite_patches=patch,classification=classification_rows,cases=cases,singular_values=sv.tolist(),rank=int(np.linalg.matrix_rank(A,tol=1e-10)),screw_virtual_work_error=work,quadrature_difference_4_8=err48,quadrature_difference_8_16=err816,conditional_axial_take_up_mm=clear,required_torque_Nmm_per_N=-K,accepted_product_equilibria=0,installed_capacity_N=None,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Unit tractions on finite actual declared flanks only;not100g operating equilibrium or strength','Both side traction cone is a geometric span;opposite flank simultaneous contact NOT certified','Each loaded flank requires relative axial take-up;nut cage/head/key/pin displacement and torque reaction remain unsolved','No material minimum/root stress/preload/elastic pressure/host/global energy qualification']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},rank=int(np.linalg.matrix_rank(A,tol=1e-10)),work=work,err48=err48,err816=err816)),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
