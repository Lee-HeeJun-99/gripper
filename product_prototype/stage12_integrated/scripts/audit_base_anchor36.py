"""Independent pressure-direction/force/work audit on actual P1 anchor solids.
Imports neither LP producer nor its face/normal extraction implementation.
"""
import json,sys,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN
from OCP.gp import gp_Pnt

def inside(s,p):return BRepClass3d_SolidClassifier(s,gp_Pnt(*map(float,p)),1e-9).State()==TopAbs_IN
def main():
 src=ROOT/'validation/integrated'/sys.argv[1]/'summary.json';out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists()
 result=json.loads(src.read_text());cad=json.loads((REPO/result['candidate']['path']).read_text());base=read(REPO/cad['part_references']['TEST_BASE']['path']);rail=read(REPO/cad['part_references']['BENCH_ANCHOR_RAIL']['path'])
 patches=json.loads((REPO/result['patches']['path']).read_text());tr=json.loads((REPO/result['tractions']['path']).read_text());mass=json.loads((REPO/result['mass']['path']).read_text());normals=[];rows=[];ear=[]
 for level,cells in patches['levels'].items():
  for c in cells:
   if not c['label'].startswith('key'):continue
   p=np.array(c['point_mm']);n=np.array(c['direction']);eps=1e-5
   normals.append(dict(level=level,label=c['label'],point_mm=p.tolist(),base_inward=inside(base,p+eps*n),rail_inward=inside(rail,p-eps*n)))
 for level,cases in tr.items():
  for name,case in cases.items():
   if not case['success']:continue
   count=3 if 'ANCHOR_BOLT_2' in cad['part_references'] else 2
   w=np.zeros(6);work=np.zeros(6);receive=np.zeros(6);er=[np.zeros(6) for _ in range(count)];positive=True
   for ray in case['rays']:
    p=np.array(ray['point_mm'])*.001;n=np.array(ray['direction']);f=ray['pressure_MPa']*ray['area_mm2']*n
    positive &= ray['pressure_MPa']>=0 and ray['area_mm2']>0
    w+=np.r_[f,np.cross(p,f)]
    receiver=p.copy()
    if ray['label'].startswith('bolt'):receiver[2]=.074
    receive+=np.r_[-f,np.cross(receiver,-f)]
    for k in range(6):
     v=np.eye(3)[k] if k<3 else np.cross(np.eye(3)[k-3],p)
     work[k]+=f@v
    station=2 if ray['point_mm'][1]<-43 else int(ray['point_mm'][0]>20)
    root=np.array([21,-42,63] if station==2 else [-44 if station==0 else 86,23,63])*.001
    er[station]+=np.r_[f,np.cross(p-root,f)]
   external=np.array(case['external_wrench_N_Nm']);res=w+external
   rows.append(dict(level=level,case=name,positive=bool(positive),force_residual_N=float(max(abs(res[:3]))),moment_residual_Nm=float(max(abs(res[3:]))),six_motion_work_error_J=float(max(abs(work-w))),receiver_wrench_error_N_Nm=float(max(abs(receive-external)))))
   if name=='conditional_frozen_contact_plus_nominal_gravity':
    for station,r in enumerate(er):
     # Actual ear root20x6mm; unnotched nominal section demand ONLY.
     # A20mm body-to6mm-ear junction is not a beam allowable or stress bound.
     M=r[3:]*1000
     ear.append(dict(level=level,station=station,root_wrench_N_Nm=r.tolist(),area_mm2=120,Ix_mm4=360,Iz_mm4=4000,nominal_normal_demand_MPa=abs(r[1])/120+abs(M[0])*3/360+abs(M[2])*10/4000,nominal_transverse_shear_MPa=1.5*float(np.hypot(r[0],r[2]))/120,notch_factor=None,certified_allowable_MPa=None,capacity_qualified=False))
 force=max(r['force_residual_N'] for r in rows);moment=max(r['moment_residual_Nm'] for r in rows)
 checks=dict(candidate_hash=sha(REPO/result['candidate']['path'])==result['candidate']['SHA256'],new_artifact_hashes=all(sha(REPO/result[k]['path'])==result[k]['SHA256'] for k in ('patches','tractions','mass')),actual_key_normals_point_into_both_solids=all(r['base_inward'] and r['rail_inward'] for r in normals),all_pressures_nonnegative=all(r['positive'] for r in rows),force_original1e_minus8=force<1e-8,moment_original1e_minus10=moment<1e-10,six_independent_work_checks=all(r['six_motion_work_error_J']<1e-12 for r in rows),receiver_full_wrench=all(r['receiver_wrench_error_N_Nm']<1e-10 for r in rows))
 dump(out/'normal_witnesses.json',normals);dump(out/'summary.json',dict(status='ACTUAL_ANCHOR_INDEPENDENT_FORCE_DIRECTION_WORK_PASS' if all(checks.values()) else 'ACTUAL_ANCHOR_INDEPENDENT_AUDIT_FAIL',candidate=result['candidate'],source=ref(src),verifier=ref(out/'verifier.py'),checks=checks,force_max_N=force,moment_max_Nm=moment,normals_tested=len(normals),rejected_normals=sum(not(r['base_inward'] and r['rail_inward']) for r in normals),normal_witnesses=ref(out/'normal_witnesses.json'),rows=rows,ear_nominal_section_demands=ear,LP_mesh_original1percent=all(c['original1percent'] for c in result['mesh_contrasts']),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Independent finite-solid normal orientation and integrated virtual work checks do not establish elastic pressure/finite compliance/thread/preload/material support.','20x6mm root section demand ignores local3D notch/warping and elastic pressure redistribution;no allowable or safetyfactor,no strength PASS.','Pressure-bound mesh FAIL preserved independently of force/work checks. Whole83part gravity and frozen contact sensitivity are not actual newly solved operating load.','Receiver receives all6wrench components;finite external rail attachment remains absent,never filled with a fixedDOF or counterload.']))
 print(json.dumps(dict(checks=checks,normals=len(normals),rejected=sum(not(r['base_inward'] and r['rail_inward']) for r in normals))));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
