"""Read-only actual finite owner-face coverage of a REJECTED P1 proposal.
A diagnostic query, never a support update, CCD, equilibrium or swept path proof.
"""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump
from primary_local_surface_support import LocalSurfaceSupport
from primary_ritz_storage import load as load_ritz

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_measured_enrichment_continuation1/summary.json';s=json.loads(src.read_text());e=np.load(REPO/s['output']['path']);field=dict(np.load(REPO/s['source_field']['path']));old=json.loads((ROOT/'validation/integrated/primaryP1_ritz_primaldual1/summary.json').read_text());r=load_ritz(json.loads((REPO/old['source']['path']).read_text()));N=len(field['u_mm']);du=np.asarray((e['proposed_x']-r['before_x'])[:N],dtype=float);names=['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'];model=LocalSurfaceSupport(field,names);pressure=np.asarray(-e['physical_dual'][:2169],dtype=float);rows=model.finite_coverage(field['u_mm']+du,pressure);dump(out/'coverage.json',rows)
 groups=[]
 for row,group in zip(rows,model.groups):
  ids=group['ids'];outside=np.asarray(row['outside_rows'],dtype=int);geo=row['outside_geometry'];groups.append(dict(label=row['label'],first=group['first'],second=group['second'],rows=row['rows'],outside_rows=len(outside),outside_active_rows=len(row['outside_active_rows']),outside_active_force_sum_N=row['outside_active_force_sum_N'],maximum_tangential_overhang_mm=max((g['tangential_overhang_mm'] for g in geo),default=0.),maximum_nearest_distance_mm=max((g['nearest_distance_mm'] for g in geo),default=0.),maximum_outside_pressure_N=float(np.max(pressure[ids[outside]])) if len(outside) else 0.))
 total=sum(g['outside_rows'] for g in groups);active=sum(g['outside_active_rows'] for g in groups);dump(out/'summary.json',dict(status='ACTUAL_P1_REJECTED_PROPOSAL_FINITE_DOMAIN_MEASURED',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],coverage=ref(out/'coverage.json'),dependency_sources={name:ref(ROOT/'scripts'/name) for name in ['primary_local_surface_support.py','primary_corotated_support.py']},groups=groups,all_original_rows=sum(g['rows'] for g in groups),outside_projected_owner_rows=total,outside_active_owner_rows=active,finite_owner_coverage_pass=total==0,physical_KKT_qualified=False,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Original planar owner-face projection coverage at rejected endpoint only. Not closed-surface signed distance, CCD, updated contact pressure/force or attached-load nonlinear update.','Outside active means pressure of the rejected linear proposal above1e-8N; these pressures are not physical measured reactions. Preserve every original row; no transfer to infinite support plane.']));print(json.dumps(dict(groups=groups,total_outside=total,total_active=active)))
if __name__=='__main__':main()
