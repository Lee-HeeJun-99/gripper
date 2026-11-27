"""Actual 85-part revised P1 assembly poses and explicit threaded spin mechanism."""
import sys,json,shutil,math
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,translate
from mechanisms_stage1 import hex_axis
from validate_base_anchor36 import props
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

def spin(s,x,y,t):
 tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(x,y,0),gp_Dir(0,0,1)),t);return BRepBuilderAPI_Transform(s,tr,True).Shape()
def main():
 out=ROOT/'validation/integrated/primaryP1_nutcapture43b_validation';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists()
 cp=ROOT/'cad/exports/primaryP1_nutcapture43b/summary.json';d=json.loads(cp.read_text());refs=d['part_references'];assert len(refs)==85 and all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(v) for n,v in s.items()};rail=s['BENCH_ANCHOR_RAIL'];poses=[];rows=[]
 def hits(shape,exclude):
  b=bounds(shape);return [dict(part_ID=n,volume_mm3=v) for n in s if n not in exclude and overlap(b,bb[n]) and (v:=common(shape,s[n]))>1e-8]
 for i,(x,y) in enumerate([(-44,34),(86,34),(21,-53)]):
  assert not(ROOT/'runtime/STOP').exists();nn=f'ANCHOR_NUT_{i}';bn=f'ANCHOR_BOLT_{i}';nut=s[nn]
  for dz in (16,8,5.3,3,1,.2,0):poses.append(dict(operation='nut_top_drop_before_bolt',station=i,offset_z_mm=dz,hits=hits(translate(nut,0,0,dz),{nn,bn})))
  for dz in (-25,-10,-5,-1,0):poses.append(dict(operation='bolt_bottom_approach_smooth_envelope_only',station=i,offset_z_mm=dz,hits=hits(translate(s[bn],0,0,dz),{bn})))
  tool=hex_axis((x,y,34),(0,0,1),3.9,23.4);poses.append(dict(operation='3.9AF_tool_in_actual4AF_socket',station=i,hits=hits(tool,set())))
  stop=[]
  for sign in (-1,1):
   lo=0.;hi=.3;assert common(spin(nut,x,y,sign*hi),rail)>1e-8
   for _ in range(24):
    mid=(lo+hi)/2
    if common(spin(nut,x,y,sign*mid),rail)>1e-8:hi=mid
    else:lo=mid
   stop.append(dict(sign=sign,clear_angle_rad=lo,interference_angle_rad=hi,interference_volume_mm3=common(spin(nut,x,y,sign*hi),rail),probe_plus_001rad_volume_mm3=common(spin(nut,x,y,sign*(hi+.01)),rail)))
  # Exact nominal seat persists; added cage neither covers bolt nor nut seat.
  from primary_installed_stack42 import overlap_area
  rows.append(dict(station=i,nut=refs[nn],bolt=refs[bn],nut_seat_area_mm2=overlap_area(nut,rail,74),stops=stop))
 sd=ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json';p=json.loads(sd.read_text())['bolt']['dimensions_mm']['pitch'];lead=p/(2*math.pi)
 # q=[axial separation(mm),bolt angle(rad),nut angle(rad)].
 # Hypothetical thread is WORK compatible, not yet a physical connector.
 J=np.array([[1.,-lead,lead],[0,0,1.]])
 mode=np.array([lead,1.,0]);virtual_error=float(abs(J@mode).max())
 def equilibrium(with_bolt_lock):
  A=J.T if not with_bolt_lock else np.column_stack([J.T,[0,1,0]])
  target=np.array([1.,0,0]);r=linprog(np.zeros(A.shape[1]),A_eq=A,b_eq=target,bounds=[(None,None)]*A.shape[1],method='highs')
  return dict(feasible=bool(r.success),status=int(r.status),residual=None if not r.success else float(abs(A@r.x-target).max()),reactions=None if not r.success else r.x.tolist())
 free=equilibrium(False);locked=equilibrium(True)
 V,c=props(rail);old=json.loads((ROOT/'cad/exports/primaryP1_anchor36b/summary.json').read_text());v0,c0=props(read(REPO/old['part_references']['BENCH_ANCHOR_RAIL']['path']))
 checks=dict(actual_85part_hashes=True,final_no_interferences=not d['interferences'],all_recorded_assembly_tool_poses_clear=all(not p['hits'] for p in poses),both_rotation_stops_each_nut=all(len(r['stops'])==2 and all(t['probe_plus_001rad_volume_mm3']>1e-8 for t in r['stops']) for r in rows),nut_seats_preserved=all(abs(r['nut_seat_area_mm2']-31.6673313994)<1e-7 for r in rows),explicit_free_bolt_spin_rejected=not free['feasible'],bolt_lock_mathematical_control=locked['feasible'],spin_virtual_work=virtual_error<1e-12)
 dump(out/'summary.json',dict(status='ACTUAL_P1_NUT_CAPTURE_LOCAL_ASSEMBLY_AND_SPIN_REJECTION_NOT_RELEASE',candidate=ref(cp),verifier=ref(out/'verifier.py'),standard_source=ref(sd),actual_parts=85,checks=checks,rows=rows,assembly_poses=poses,receiver_volume_mm3=V,receiver_centroid_mm=c.tolist(),delta_receiver_volume_mm3=V-v0,conditional_delta_mass_kg_2700kg_m3=(V-v0)*2700e-9,physical_density_kg_m3=None,thread_kinematic_jacobian=J.tolist(),unrestrained_screw_mode=mode.tolist(),unit_axial_load_virtual_work_Nmm=lead,thread_pitch_mm=p,unit_thread_torque_Nmm=lead,nut_cage_only_equilibrium=free,hypothetical_bolt_lock_control=locked,virtual_work_error=virtual_error,external_support_body=None,external_mount_ports_count=4,external_mounting_fasteners_count=0,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Finite poses only;actual thread engagement/helical assembly and complete continuous assembly are not certified.','Nut pocket is removable from top,not an axial retainer. Corner-relieved flats stop nominal nut rotation after measured backlash. No contact pressure or cage strength computed.','Maximum8AF source nut used;minimum7.78AF increases backlash;source and machining tolerances not qualified.','Nut capture alone leaves bolt screw-spin mechanism. Explicit missing bolt reaction is NOT silently fixed. Mathematical locked control is not actual hardware.','External mounting ports are finite CAD holes only: no bench,fasteners,material minimum or support stiffness.','Changed receiver invalidates old receiver FE/mass/contact proofs. All original mesh/time/energy/strength failures remain. No Stage3.']))
 print(json.dumps(dict(checks=checks,rows=rows,free_bolt_equilibrium=free,delta_volume_mm3=V-v0)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
