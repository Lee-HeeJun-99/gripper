"""Independent saved actualplate load/resultant and fourfoot contact ledger."""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,ref,dump
V=ROOT/'validation/integrated';out=V/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[]
for tag in sys.argv[2:]:
 s=json.loads((V/tag/'summary.json').read_text());a=np.load(V/tag/'field.npz');quad=np.load(V/tag/'quadrature.npz');p,F,R,q=a['points_mm'],a['load_N'],a['reaction_N'],a['quadrature_force_N'];x=quad['points_mm'];weights=quad['weights_mm2'];feet=[]
 def wrench(x,f):return np.r_[f.sum(0),np.cross(x,f).sum(0)]
 for x0 in [-115.,137.]:
  for y0 in [-90.,60.]:
   mask=(x[:,0]>=x0-1e-8)&(x[:,0]<=x0+20+1e-8)&(x[:,1]>=y0-1e-8)&(x[:,1]<=y0+20+1e-8);feet.append(dict(lower_corner_xy_mm=[x0,y0],normal_N=float(q[mask,2].sum()),tangent_N=q[mask,:2].sum(0).tolist(),wrench_N_Nmm=wrench(x[mask],q[mask]).tolist(),peak_sample_pressure_MPa=float((q[mask,2]/weights[mask]).max()),area_mm2=float(weights[mask].sum())))
 applied=wrench(p,F);ground=wrench(p,R);fq=wrench(x,q);res=float(abs(applied+ground).max());pull=float(abs(ground-fq).max());rows.append(dict(source=ref(V/tag/'summary.json'),full_load_local=all(s['checks'].values()),external_wrench_N_Nmm=applied.tolist(),physical_floor_wrench_N_Nmm=ground.tolist(),quadrature_floor_wrench_N_Nmm=fq.tolist(),force_moment_residual_N_Nmm=res,quadrature_adjoint_resultant_error_N_Nmm=pull,feet=feet,all6_resultants_pass=bool(res<1e-6 and pull<1e-6)))
dump(out/'summary.json',dict(status='ACTUAL_P1_NEW_FULLPLATE_LOAD_AND_FOOT_REACTION_LEDGER',candidate=s['candidate'],producer=ref(out/'producer.py'),rows=rows,checks=dict(nonempty=bool(rows),all6physical_resultants=all(q['all6_resultants_pass'] for q in rows)),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Physical savedplate reference forces/moments, not83body operatingequilibrium or measured hardware. Prescribedupper affine reference, assumedmaterial/gravity/floorfriction retained. Peak sample pressure is not source-minimum strength or actualcontinuousmaximum pressure.']))
print(json.dumps(dict(rows=len(rows),maximum_resultant_error=max(q['force_moment_residual_N_Nmm'] for q in rows))))
