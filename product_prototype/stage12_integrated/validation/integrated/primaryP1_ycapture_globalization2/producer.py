"""Product geometry local-search contract and archived path negative control.
No proposed old field is adopted on new CAD; this is not a nonlinear update.
"""
import sys,json,shutil
import numpy as np
from scipy import sparse
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_ritz_storage import load as load_ritz
from primary_yshoulder_contact import evaluate,local_step_bound

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_measured_enrichment_continuation1/summary.json';s=json.loads(src.read_text());e=np.load(REPO/s['output']['path']);field=np.load(REPO/s['source_field']['path']);old=json.loads((ROOT/'validation/integrated/primaryP1_ritz_primaldual1/summary.json').read_text());r=load_ritz(json.loads((REPO/old['source']['path']).read_text()));dx=e['proposed_x']-r['before_x'];names=['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'];ds=[]
 for n in names:
  p=field[n+'_points_mm'];o=int(field[n+'_offset']);ds.append(np.asarray(dx[o:o+len(p)*3].reshape(-1,3),float))
 mo=int(field['motor_offset']);alpha=local_step_bound(ds,np.asarray(dx[mo+3:mo+6],float));relative=ds[1].mean(0)-ds[0].mean(0);first_touch=.1/abs(relative[1]);A=sparse.load_npz(REPO/old['physical_A']['path']);p=np.load(REPO/old['problem']['path']);eq=np.isfinite(p['upper'])&(p['upper']==p['lower']);hist=[]
 for t in [0,alpha,first_touch,1.]:
  z=r['before_x']+t*dx;g=A@z-p['lower'];hist.append(dict(alpha=float(t),historical_original_equality_max_mm=float(abs(g[eq]).max()),historical_original_inequality_min_mm=float(g[~eq].min()),historical_original_row_count=len(g)))
 contact=ROOT/'validation/integrated/primaryP1_ycapture_mesh3/summary.json';cs=json.loads(contact.read_text());rows=json.loads((REPO/cs['contact_rows']['path']).read_text());samples=[]
 for a in [0,alpha,first_touch,1.]:
  values=[];outside=0
  for row in rows:
   point=np.array(row['root_point_mm'])+a*relative;tri=np.array(row['owner_triangle_mm']);z=evaluate(point,tri,row['normal_sign']);values.append(z['gap_mm']);outside+=not z['inside']
  samples.append(dict(alpha=float(a),nominal_new_product_rigid_root_translation_mm=(a*relative).tolist(),finite_shoulder_gap_min_mm=min(values),outside_projected_owner_rows=int(outside)))
 checks=dict(original2208rows_retained=A.shape[0]==2208,all_original_sourcehashes=all(sha(REPO/s[k]['path'])==s[k]['SHA256'] for k in ['candidate','source_field','output']),free_RootY_gamma_nonzero=abs(float(dx[-1]))>99,original_local_translation_limit=abs(max(np.linalg.norm(d,axis=1).max() for d in ds)*alpha-.05)<1e-10,local_limit_precedes_real_contact=0<alpha<first_touch<1,full_archived_escape_rejected=samples[-1]['finite_shoulder_gap_min_mm']<-99,local_new_geometry_gap_positive=samples[1]['finite_shoulder_gap_min_mm']>.049,local_model_operator_hash=sha(ROOT/'scripts/primary_yshoulder_contact.py')==json.loads((REPO/cs['inputs']['path']).read_text())['contact_operator']['SHA256'])
 checks={k:bool(v) for k,v in checks.items()}
 dump(out/'summary.json',dict(status='ACTUAL_P1_GEOMETRY_LOCAL_SEARCH_CONTRACT_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_GEOMETRY_LOCAL_SEARCH_CONTRACT_FAIL',candidate=cs['candidate'],historical_rejected_path=ref(src),historical_source_field=s['source_field'],new_contact_source=ref(contact),checks=checks,local_alpha=float(alpha),first_nominal_shoulder_touch_alpha=float(first_touch),historical_full_RootY_gamma_mm=float(dx[-1]),historical_relative_Root_translation_mm=relative.tolist(),new_nominal_geometry_direction_samples=samples,historical_allrow_audit=hist,original_unit_acceptance=dict(fullforce_N=1e-8,finitegap_mm=1e-10,localmodel_translation_mm=.05,localmodel_rotation_rad=.05,finiteowner_required=True,cone_sign_required=True,complementarity_required=True,Armijo_required=True),all2208_original_rows_preserved=True,old_sourcefield_applied_to_new_CAD=False,solver_launches=0,accepted_equilibria=0,actual_support_updates=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Algorithmic localmodel bound is not a physical spring/fixation or reaction. Keep RootY/gamma free and original physical rows/37rigid modes; new contact comes from actual shoulder faces with0.1mmgap.','Historical path and new nominal rigid-direction geometry tests are distinct. NO interpolation/reuse of old sourcefield as a newCAD equilibrium, no newmodel P/q or force solution.','A positive gap after truncation does not clear original allrow/fullforce/gauge/conesign/complementarity/Armijo prerequisites or certify physical step.','Newmesh must rebuild all original physical interfaces plus shoulder rows and finiteowner validity; no row deletion/pressure transfer onto unsupported infinite planes. Search boundary multipliers not physical reactions.']));print(json.dumps(dict(checks=checks,alpha=alpha,first_touch=first_touch,samples=samples,historical=hist)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
