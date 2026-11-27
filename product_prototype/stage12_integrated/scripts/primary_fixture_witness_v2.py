"""Independent actual key contact derivatives and saved uniform-traction virtual work.
Reconstruct forces by pressure*finite area; don't accept solver success as evidence.
"""
import json,sys,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,box,cut
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

def W(p,f):return np.r_[f,np.cross(np.array(p)*.001,f)]
def main():
 out=ROOT/'validation/integrated/primaryP1_fixture_witness2';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'cad/exports/primaryP1_fixture13/summary.json';cad=json.loads(src.read_text());r=ROOT/'validation/integrated/primaryP1_fixture_verify3/summary.json';d=json.loads(r.read_text());data=json.loads((REPO/d['tractions']['path']).read_text());patches=json.loads((REPO/d['patches']['path']).read_text())
 ground=read(REPO/cad['part_references']['GROUND_PLATE']['path']);base=read(REPO/cad['part_references']['TEST_BASE']['path'])
 dump(out/'inputs.json',dict(candidate=ref(src),result=ref(r),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),d['tractions'],d['patches']],criteria=dict(area_relative_max=1e-6,force_N_max=1e-8,moment_Nm_max=1e-10,work_J_max=1e-12,mesh_relative_max=.01)))
 derivatives=[]
 for h in (.001,.002):
  for axis,area in ((0,30.),(1,18.)):
   for sign in (-1,1):
    shift=np.zeros(3);shift[axis]=sign*h;v=common(translate(ground,*shift),base);derivatives.append(dict(h_mm=h,axis=axis,sign=sign,overlap_mm3=v,area_from_volume_mm2=v/h,expected_area_mm2=area,relative_error=abs(v/h/area-1)))
 # A nominal gap is not engaged shear: remove a0.02mm layer from both key sides
 # of the BASE pocket only. This is an in-memory physical counterexample, no old CAD edit.
 gapped=cut(base,box(-48.02,-6,45.99,.02,12,3.22),box(-40,-6,45.99,.02,12,3.22))
 gap_overlap=[common(translate(ground,h,0,0),gapped) for h in (-.001,.001)]
 source=ROOT/'validation/transmission/primaryP1_corner_demand_loads1/summary.json';loads=json.loads(source.read_text())['rows'][-1]
 ext=np.array([loads['frame_total_external_force_XZ_N'][0],0,loads['frame_total_external_force_XZ_N'][1],0,loads['frame_total_external_couple_about_Y_Nm'],0])
 # Six independent unit rigid virtual motions; local surface velocity exactly
 # equals translation + rotation cross actual position. Six work values = wrench.
 rows=[];negatives=[];face_dist=[]
 for level in data['levels']:
  rr=level['result'];groundW=np.zeros(6);baseW=np.zeros(6);work=np.zeros(6);press=[]
  for t in rr['active_uniform_tractions']:
   f=t['pressure_MPa']*t['area_mm2']*np.array(t['normal_on_ground']);p=np.array(t['centroid_mm']);groundW+=W(p,f);q=p.copy()
   if t['patch'].startswith('head'):q[2]=66
   baseW+=W(q,-f);press.append(t['pressure_MPa']>=0 and t['area_mm2']>0)
   for k in range(6):
    tr=np.eye(3)[k] if k<3 else np.zeros(3);rot=np.eye(3)[k-3] if k>=3 else np.zeros(3);vel=tr+np.cross(rot,p*.001);work[k]+=float(f@vel)
   if t['patch'].startswith('key'):
    v=BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex();dist=BRepExtrema_DistShapeShape(v,ground);dist.Perform();dist2=BRepExtrema_DistShapeShape(v,base);dist2.Perform();face_dist.append(max(dist.Value(),dist2.Value()))
  # Removing key shear or reversing one saved normal must break equilibrium.
  key=next(t for t in rr['active_uniform_tractions'] if t['patch'].startswith('key'));keyW=W(key['centroid_mm'],np.array(key['normal_on_ground'])*key['pressure_MPa']*key['area_mm2'])
  negatives.append(dict(divisions=level['divisions'],omitted_key_force_residual_N=float(np.linalg.norm((groundW-keyW+ext)[:3])),reversed_key_force_residual_N=float(np.linalg.norm((groundW-2*keyW+ext)[:3]))))
  rows.append(dict(divisions=level['divisions'],ground_residual_N_Nm=(groundW+ext).tolist(),base_receives_N_Nm=baseW.tolist(),base_difference_N_Nm=(baseW-ext).tolist(),virtual_work_error=float(np.max(abs(work-groundW))),nonnegative_pressures=all(press)))
 # Actual finite full-face witness, not an LP limiting point: pressure stress and
 # bolt nominal stress are demanded values, no allowable. Source thread maximum
 # runout and effective engagement not inferred from smooth major envelopes.
 coarse=data['levels'][0]['result'];head=[t for t in coarse['active_uniform_tractions'] if t['patch'].startswith('head')];nominal=[]
 for t in head:
  nominal.append(dict(station=t['patch'],axial_N=t['normal_force_N'],head_bearing_MPa=t['pressure_MPa'],nut_bearing_MPa=t['normal_force_N']/data['nut_bearing'][int(t['patch'][4:])]['area_mm2'],source_minimum_allowable=None,effective_thread_engagement_mm=None,qualified=False))
 checks=dict(all_contact_derivatives=all(x['relative_error']<1e-6 for x in derivatives),nominal_gap_rejects_initial_key_shear=max(gap_overlap)<1e-8,all_pressure_integrations_balance=all(max(abs(x) for x in z['ground_residual_N_Nm'][:3])<1e-8 and max(abs(x) for x in z['ground_residual_N_Nm'][3:])<1e-10 for z in rows),base_full_wrench=all(max(abs(x) for x in z['base_difference_N_Nm'])<1e-9 for z in rows),six_virtual_work_checks=all(z['virtual_work_error']<1e-12 for z in rows),nonnegative_pressures=all(z['nonnegative_pressures'] for z in rows),key_traction_centroids_on_both_solids=max(face_dist)<1e-7,corrupt_tractions_rejected=all(z['omitted_key_force_residual_N']>1e-3 and z['reversed_key_force_residual_N']>1e-3 for z in negatives),source_hashes=all(sha(REPO/v['path'])==v['SHA256'] for v in (d['candidate'],d['tractions'],d['patches'])))
 mesh_fail=not d['checks']['reaction_bound_mesh_1pct']
 result=dict(status='PRIMARY_FIXTURE_INDEPENDENT_WRENCH_WITNESS_PASS_MESH_FAIL' if all(checks.values()) and mesh_fail else 'PRIMARY_FIXTURE_WITNESS_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks=checks,contact_derivatives=derivatives,gapped_key_overlaps_mm3=gap_overlap,rows=rows,negative_controls=negatives,actual_bolt_demand=nominal,key_peak_pressure_not_qualified=True,conditional_full_face_key_pressure_MPa=coarse['key_total_compression_N']/30,mesh_fail_preserved=d['mesh'],actual_source_load=ref(source),whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['No nominal major-shank stress is substituted for certified thread core/flank/engagement strength','Uniform finite-face tractions give a feasible reference,not a compliant physical distribution or installed preload','Key nominal0gap is critical; shown0.02mm gap eliminates initial shear contact. Fit/tolerance and elastic contact must be solved','Finite Base requires explicit opposite external grip wrench,not hidden support or verified laboratory anchorage'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,actual_bolt_demand=nominal,contact_derivatives=derivatives)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
