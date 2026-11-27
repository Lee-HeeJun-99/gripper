"""Save-only review of completed fields. No equilibrium solve or new CAD."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha

def get(tag):
 p=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(p.read_text());a=np.load(REPO/s['field']['path']);return p,s,a

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'reviewer.py');pa,sa,a=get('primaryP1_chain0_h5_3');pb,sb,b=get('primaryP1_chain0_h5_point1');rows=[]
 for name in sa['elastic_bodies']:
  assert np.array_equal(a[name+'_points_mm'],b[name+'_points_mm']) and np.array_equal(a[name+'_tetra'],b[name+'_tetra']);p=a[name+'_points_mm'];t=a[name+'_tetra'];o=int(a[name+'_offset']);ua=a['u_mm'][o:o+3*len(p)].reshape(-1,3);ub=b['u_mm'][o:o+3*len(p)].reshape(-1,3);dx=p[t[:,1:]]-p[t[:,0,None]];ga=np.linalg.solve(dx,ua[t[:,1:]]-ua[t[:,0,None]]);gb=np.linalg.solve(dx,ub[t[:,1:]]-ub[t[:,0,None]]);ea=(ga+ga.transpose(0,2,1))/2;eb=(gb+gb.transpose(0,2,1))/2;rows.append(dict(part=name,relative_strain_error=float(np.linalg.norm(ea-eb)/max(np.linalg.norm(ea),1e-30)),relative_vm_error=float(np.linalg.norm(a[name+'_vm_MPa']-b[name+'_vm_MPa'])/max(np.linalg.norm(a[name+'_vm_MPa']),1e-30))))
 force_error=float(np.max(abs(a['bolt_force_N']-b['bolt_force_N'])));energy_error=abs(sa['elastic_energy_Nmm']/sb['elastic_energy_Nmm']-1);gauge_ok=all(r['relative_strain_error']<1e-8 and r['relative_vm_error']<1e-8 for r in rows) and force_error<1e-8 and energy_error<1e-8
 gap_path=ROOT/'validation/integrated/primaryP1_chain02_h5_point1/summary.json';gap=None
 if gap_path.exists():
  sg=json.loads(gap_path.read_text());gap=dict(source=ref(gap_path),status=sg['status'],checks=sg['checks'],gap_mm=sg['gap_mm'],preload_each_N=sg['preload_each_N'],bolt_force_N=sg['bolt_force_N'],contact_groups=sg['contact_groups'],conditional_stresses=sg['stresses'],motor_translation_mm=sg['motor_rigid_translation_mm'],motor_rotation_rad=sg['motor_rigid_rotation_rad'],energy_Nmm=sg['elastic_energy_Nmm'],force_residual=sg['relative_stationarity'])
  if 'field' in sg:
   f=np.load(REPO/sg['field']['path']);relative_motion=[]
   for n in sg['elastic_bodies']:
    pts=f[n+'_points_mm'];o=int(f[n+'_offset']);ug=f['u_mm'][o:o+3*len(pts)].reshape(-1,3);un=b['u_mm'][o:o+3*len(pts)].reshape(-1,3);relative_motion.append(dict(part=n,max_same_gauge_displacement_change_mm=float(np.linalg.norm(ug-un,axis=1).max())))
   gap['same_gauge_gap_contrast_motion']=relative_motion
 result=dict(status='ACTUAL_P1_SAVED_CHAIN_GAUGE_AND_GAP_REVIEW_NOT_RELEASE',candidate=sa['candidate'],reviewer=ref(out/'reviewer.py'),sources=[ref(pa),ref(pb)],gauge_equivalence_checks=dict(strain_force_energy_unchanged=gauge_ok),gauge_rows=rows,max_bolt_difference_N=force_error,relative_elastic_energy_difference=energy_error,gap=gap,preload_contrast_status='NOT_RUN_AFTER_FINE_LIMIT_EVENT',whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Savedfield reviewonly; no newsolve,geometry,physics or timeoutretry.','Point/volume gauges select different globalcoordinates,not differentstiffness. Actual sourcefixturesandcasecapacityremainunknown.','Gap islinearizedcontactlawoffsetonactualnominalCAD,notmachinedgap/finiteCCD/preloadfitcertificate.','FrozenupstreamFinger/string notrecoupled; displacementchanges cannot bepromotedto unchangednormalforce/grasp or globalenergy.'])
 dump(out/'summary.json',result);print(json.dumps(dict(gauge_equivalence=gauge_ok,gauge_rows=rows,gap_status=gap['status'] if gap else 'NO_COMPLETE_GAP_RESULT')));raise SystemExit(0 if gauge_ok else 2)
if __name__=='__main__':main()
