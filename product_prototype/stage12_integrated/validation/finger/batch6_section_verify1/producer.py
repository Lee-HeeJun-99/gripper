"""Independent circle-chord quadrature and section resultant verification."""
import json,math,shutil
import numpy as np
from scipy.integrate import quad
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/finger/batch6_section_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'validation/finger/batch6_section_demand1/summary.json';d=json.loads(src.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text());w=json.loads((REPO/inp['load']['path']).read_text())
 refs=[d['producer'],d['inputs'],inp['candidate'],inp['load'],*inp['parts'].values(),*inp['dependencies']]
 checks={'hashes':all(sha(REPO/r['path'])==r['SHA256'] for r in refs)}
 errors=[]
 for r in d['sections']:
  h=r['h_mm'];a=.6 if r['z_mm']==-8 else .2*quad(lambda z:3-2*math.sqrt(1.05**2-z*z),-h/2,h/2,epsabs=1e-13)[0]/h
  errors += [abs(r['A_mm2']/a-1),abs(r['Iyy_mm4']/(a*.2**2/12)-1)]
 checks['independent_circle_chord_and_inertia']=max(errors)<1e-6
 # Use the declared limit, including the coarse/base pair.
 refinement=max(d['base_to_finest_area_relative_errors']);checks['declared_base_to_finest_limit']=refinement<inp['limits']['refinement_relative']
 F,M,N=w['equivalent_tip_wrench_N_Nmm'];gx,gw=np.polynomial.legendre.leggauss(6);x=.1*gx
 def resultant(st):
  lo,hi=st['sigma_faces_MPa'];stress=(lo+hi)/2+(hi-lo)*x/.2
  width=st['A_mm2']/.2
  return .1*width*float(gw@stress),.1*width*float(gw@(stress*x))
 residuals=[]
 for st in d['stations']:
  a,b=resultant(st);expected=M+F*(st['z_mm']-w['cut_tip_z_mm']);residuals += [abs(a-N),abs(b-expected)]
 checks['integrated_stress_resultants']=max(residuals)<inp['limits']['balance_absolute']
 pert=dict(d['stations'][0]);pert['sigma_faces_MPa']=[x*1.01 for x in pert['sigma_faces_MPa']];a,b=resultant(pert)
 checks['perturbed_stress_rejected']=max(abs(a-N),abs(b-d['stations'][0]['M_Nmm']))>1e-10
 checks['unqualified_capacity_not_promoted']=d['actual_capacity_qualified'] is False and d['allowable_MPa'] is None
 dump(out/'summary.json',dict(status='SECTION_DEMAND_VERIFIER_PASS' if all(checks.values()) else 'SECTION_DEMAND_VERIFIER_FAIL',source=ref(src),producer=ref(out/'producer.py'),checks=checks,max_chord_relative_error=max(errors),max_resultant_error=max(residuals),base_to_finest_area_relative_error=refinement,declared_limit=inp['limits']['refinement_relative'],whole_system_release=False,interpretation='Producer all_base_to_finest check used .001 whereas inputs declared .0001; strict declared limit governs. No threshold changed. Finest section values may reproduce while full refinement gate fails.'))
 print(json.dumps(dict(checks=checks,refinement=refinement,chord_error=max(errors),balance=max(residuals))));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
