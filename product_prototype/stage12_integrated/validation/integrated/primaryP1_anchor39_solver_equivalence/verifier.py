"""Independent same-contact-space QP solver contrast; no optimization imports."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');paths=[ROOT/'validation/integrated'/s for s in sys.argv[2:]];d=[json.loads((p/'summary.json').read_text()) for p in paths];assert len(d)==2
 ops=[dict(np.load(REPO/x['operators']['path'])) for x in d];geo=[json.loads((REPO/x['geometry']['path']).read_text()) for x in d];assert d[0]['candidate']==d[1]['candidate']
 points=[[(p['label'],p['exact_CAD_centroid_mm'],p['direction']) for p in g['patches']] for g in geo];same=points[0]==points[1];rows=[]
 if same:
  for a,b in zip(d[0]['rows'],d[1]['rows']):
   assert a['case']==b['case'] and a['external_wrench_N_Nmm']==b['external_wrench_N_Nmm'];pa=np.array(a['contact_forces_N']);pb=np.array(b['contact_forces_N']);work=abs(a['total_strain_work_Nmm']/b['total_strain_work_Nmm']-1);bolt=float(np.linalg.norm(np.array(a['bolt_tension_N'])-b['bolt_tension_N'])/max(np.linalg.norm(b['bolt_tension_N']),1e-30));energy_norm=float(np.sqrt(max((pa-pb)@ops[1]['C']@(pa-pb),0)/max(pb@ops[1]['C']@pb,1e-30)));rows.append(dict(case=a['case'],work_relative=work,bolt_relative=bolt,contact_energy_norm_relative=energy_norm,force_vector_relative=float(np.linalg.norm(pa-pb)/max(np.linalg.norm(pb),1e-30)),numerical1e_minus7_work_bolt=work<1e-7 and bolt<1e-7))
 checks=dict(identical_material_points=same,compliance_relative_1e_minus12=same and np.linalg.norm(ops[0]['C']-ops[1]['C'])/np.linalg.norm(ops[0]['C'])<1e-12,all14_numerical1e_minus7=bool(rows) and all(r['numerical1e_minus7_work_bolt'] for r in rows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_SAME_CONTACT_SOLVER_EQUIVALENCE_PASS_LOCAL' if all(checks.values()) else 'ACTUAL_P1_SAME_CONTACT_SOLVER_EQUIVALENCE_FAIL',candidate=d[0]['candidate'],sources=[ref(p/'summary.json') for p in paths],verifier=ref(out/'verifier.py'),checks=checks,rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Numerical solver contrast on exactly same physical contact basis;not mesh/contact-domain/physicalsupport convergence.','Original local force/gap criteria independently audited;solver success flags alone are insufficient.','No claim that close objective certifies unique pressure or that a mismatch relaxes original1e-7numerical contrast.']))
 print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
