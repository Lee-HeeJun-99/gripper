"""Finite actual product guide assembly and bilateral antiyaw bearing contrast.
Corner-normal unit torque response is not coupled installed thread equilibrium.
"""
import sys,json,math,shutil,os,time
import numpy as np
from scipy.optimize import brentq
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,bounds,overlap,box,cut,volume
from validate_nutseat46c import rotate
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.TopAbs import TopAbs_REVERSED

def main():
 out=ROOT/'validation/integrated/primaryP1_guide52_validationb';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_guide52/summary.json';d=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*d['part_references'].values(),d['assembly'],d['BOM']]);parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};bb={n:bounds(s) for n,s in parts.items()};rail=parts['BENCH_ANCHOR_RAIL'];stand=parts['BENCH_SUPPORT'];journal=[]
 def log(row):
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
 def query(label,a,b):
  assert not(ROOT/'runtime/STOP').exists();t=time.monotonic();log(dict(state='START',label=label));v=common(a,b);r=dict(state='COMPLETE',label=label,common_mm3=v,elapsed_s=time.monotonic()-t);journal.append(r);log(r);return v
 def hit(s,excluded):
  b=bounds(s);h=[]
  for n,q in parts.items():
   if n not in excluded and overlap(b,bb[n]):
    v=query('assembly_'+n,s,q)
    if abs(v)>1e-8:h.append(dict(part=n,common_mm3=v))
  return h
 # Exact rectangular swept envelopes of ADDED tongue/connector translations.
 # Mount bolts,nuts,keys,pins are installed only after the receiver is lowered.
 late={n for n in parts if n.startswith('BENCH_MOUNT_')};sweeps=[]
 for y in [-58.,39.]:
  for kind,s in [('tongue',box(-78,y-3,50,4,6,44)),('connector',box(-78,y-3,68,15,6,30))]:sweeps.append(dict(kind=kind,y=y,upward_start_mm=24,continuous_added_geometry_sweep=True,hits=hit(s,late|{'BENCH_ANCHOR_RAIL'})))
 insertion=[]
 for z in [24.,16.,8.,1.,0.]:insertion.append(dict(receiver_up_mm=z,receiver_stand_common_mm3=query('actual_receiver_vertical_insert_'+str(z),translate(rail,0,0,z),stand)))
 # Signed corner root on actual two rectangular guide tongues: r_y=51.5mm.
 a=brentq(lambda t:51.5*math.sin(t)+2*math.cos(t)-2.1,0,.01,xtol=1e-15);C=np.array([-76.,-9.5,63.]);lever=51.5*math.cos(a)-2*math.sin(a);probes=[];bindings=[];unit=[]
 def bind(label,s,p,expected=None):
  q=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex(),s);q.Perform();assert q.IsDone();nn=None;err=None
  if expected is not None:
   f=TopoDS.Face_s(q.SupportOnShape2(1));u,v=q.ParOnFaceS2(1);p1=BRepLProp_SLProps(BRepAdaptor_Surface(f),u,v,1,1e-9);assert p1.IsNormalDefined();n=p1.Normal();nn=np.array([n.X(),n.Y(),n.Z()])*(-1 if f.Orientation()==TopAbs_REVERSED else 1);err=float(max(abs(nn-expected)))
  bindings.append(dict(label=label,point_mm=list(p),distance_mm=q.Value(),outward_normal=None if nn is None else nn.tolist(),normal_error=err))
 for sign in [-1,1]:
  for offset in [-1e-5,1e-5]:
   angle=sign*(a+offset);posed=rotate(rail,-76,-9.5,angle);probes.append(dict(sign=sign,angle_rad=angle,relative_to_stop=offset,full_receiver_stand_common_mm3=query('finite_signed_yaw_'+str(sign)+'_'+str(offset),posed,stand)))
  posed=rotate(rail,-76,-9.5,sign*a);forces=[];w=np.zeros(6)
  for sy in [-1,1]:
   # For positive yaw lower (-Y) extreme contacts right (+X) slot wall.
   p=C+np.array([-sign*sy*2.1,sy*lever,0.]);normal=np.array([sign*sy,0.,0.]);bind(f'stand_wall_{sign}_{sy}',stand,p,normal);bind(f'receiver_corner_{sign}_{sy}',posed,p)
   magnitude=(.8/(2*math.pi))/(2*lever);force=normal*magnitude;ww=np.r_[force,np.cross(p-C,force)];w+=ww;forces.append(dict(point_mm=p.tolist(),force_on_receiver_N=force.tolist(),magnitude_N=magnitude,wrench_N_Nmm=ww.tolist()))
  target=np.array([0,0,0,0,0,-sign*.8/(2*math.pi)]);unit.append(dict(sign=sign,contacts=forces,total_wrench_N_Nmm=w.tolist(),required_unit_screw_torque_Nmm=.8/(2*math.pi),residual=float(max(abs(w-target))),interpretation='Actual two guide corner normal forces can oppose normalized screw port torque AFTERgap;NOT a coupled18bodyequilibrium or capacity'))
 # Vertical overlap and machining ligaments from actual finite solid sections.
 sections=[]
 for y in [-58.,39.]:
  for x in [-79.,-73.]:
   gauge=box(x-.1,y-2,61,0.2,4,4);sections.append(dict(x=x,y=y,gauge_volume_mm3=volume(gauge),actual_support_material_volume_mm3=query('slot_side_ligament_section',gauge,stand)))
 checks=dict(actual128hashes=True,changed_two_single_valid=all(c['valid'] and c['solids']==1 for c in d['changed']),nominal_changed_part_interferences_zero=not d['interferences'],continuous_added_geometry_insertion_clear=all(not r['hits'] for r in sweeps),five_actual_receiver_support_insert_poses_clear=all(abs(r['receiver_stand_common_mm3'])<1e-8 for r in insertion),signed_gap_below_clear=all(abs(r['full_receiver_stand_common_mm3'])<1e-8 for r in probes if r['relative_to_stop']<0),signed_gap_above_bears=all(r['full_receiver_stand_common_mm3']>1e-8 for r in probes if r['relative_to_stop']>0),actual_contact_points_bound=max(b['distance_mm'] for b in bindings)<1e-7,actual_wall_normals=max(b['normal_error'] or 0 for b in bindings)<1e-7,nonnegative_opposing_torque_wrench=all(r['residual']<1e-12 and all(f['magnitude_N']>0 for f in r['contacts']) for r in unit),slot_side_material_exists=all(abs(r['actual_support_material_volume_mm3']-r['gauge_volume_mm3'])<1e-8 for r in sections))
 result=dict(status='ACTUAL_P1_GUIDE_ASSEMBLY_AND_ANT IYAW_BEARING_LOCAL_PASS_NOT_RELEASE'.replace('ANT I','ANTI') if all(checks.values()) else 'ACTUAL_P1_GUIDE_ASSEMBLY_OR_BEARING_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),checks=checks,sweeps=sweeps,receiver_insertion=insertion,signed_yaw_contact_probes=probes,contact_bindings=bindings,unit_torque_bearing=unit,slot_side_material_sections=sections,guide_clearance_mm=.1,guide_centre_separation_mm=97,relative_yaw_stop_rad=a,contact_torque_lever_mm=2*lever,normal_per_contact_N_per_unit_axial_N=unit[0]['contacts'][0]['magnitude_N'],nominal_vertical_overlap_mm=6,old_thread_endpoint_remaining_overlap_mm=6-.05750657156371778,initial_producer_16mm_overlap_claim_rejected=True,query_count=len(journal),maximum_query_seconds=max(r['elapsed_s'] for r in journal),journal=ref(out/'journal.jsonl'),accepted_physical_product_equilibria=0,installed_capacity_N=None,minimum_material_MPa=None,actual_100g_operating_field=None,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Changed2actualsolids and finite128partinstalledassembly;no newstandardpart/substitute sourceclass invented','Continuous rectangular added-geometry sweeps plus5whole receiver/supportposes;not fulloriginal128partassemblysequence/toolrevalidation','Actualguidecontacttorque only;finitepoint/cornerpressure singularity,fillet/notch/strength unknown','Guide nominalclearance.1mm;no initialbearing/tie/preload orfixedrotation','Guide yaw changes originalthread/socket/key/gap states;old51contact multipliers MUSTNOT be transferred;freshcoupledcontacttakeup needed','Material minimum/process/slotnotch/ligament/100goperating/protectedpeak/FE/mass/mesh/time/globalenergy/host/3Fingerrelease remainunqualified'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,yaw=a,lever=2*lever,normal=unit[0]['contacts'][0]['magnitude_N'],queries=len(journal),failed_sweeps=[r for r in sweeps if r['hits']])),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
