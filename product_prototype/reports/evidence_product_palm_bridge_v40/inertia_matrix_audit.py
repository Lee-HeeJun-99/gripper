"""Independent Native assembled rotational operator vs M-hB/2-h²K/2."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from inertia_contact_audit import matrix
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def skew(w):return np.array([[0,-w[2],w[1]],[w[2],0,-w[0]],[-w[1],w[0],0]])
def tangent(I,w):
 B=skew(I@w)-skew(w)@I;K=np.column_stack([-skew(w)@(skew(e)@I-I@skew(e))@w for e in np.eye(3)]);return K,B
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_inertia_matrix635');p.add_argument('--reference',default='b3_inertia_force_trap627');p.add_argument('--operator',choices=('installed-header','trapezoidal-chain-rule'),default='installed-header');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;base=json.loads((BASE/'results'/a.reference/'summary.json').read_text());records=[]
 # q_new=q_old+h/2(v_old+v_new), average force h/2 gives h²/4 K.
 # Header's h²/2 formula is retained as a separately selectable failed hypothesis.
 kweight=.25 if a.operator=='trapezoidal-chain-rule' else .5
 for variant in (0,1):
  d=src/str(variant);root=ET.parse(d/'scene.scn').getroot();public=read(d/'matrix.csv');states=[read(d/f'guide{i}.csv') for i in (0,1)];mass=[read(d/f'mass{i}.csv') for i in (0,1)];initial=[vec(root.find(f"./Node[@name='guide{i}']/MechanicalObject").get('position')) for i in (0,1)];oldpoints=[vec(root.find(f"./Node[@name='guide{i}']/Node[@name='massQuadrature']/MechanicalObject").get('position')).reshape(-1,3) for i in (0,1)]
  for k,state in enumerate(states[0]):
   t=float(state['time_s']);rows=[r for r in public if float(r['time_s'])==t];A=np.zeros((12,12))
   if len(rows)!=144:raise ValueError('incomplete actual public matrix')
   for r in rows:A[int(r['row']),int(r['column'])]=float(r['value'])
   for i in (0,1):
    q=initial[i] if k==0 else vec(states[i][k-1]['rigid_q']);v=np.array(base['initial'][i]['v']) if k==0 else vec(states[i][k-1]['rigid_v']);M=matrix(oldpoints[i],q[:3],base['assumed_mass_kg']);I=M[3:,3:];K,B=tangent(I,v[3:]);dt=base['dt_s'];change=-dt/2*B-dt*dt*kweight*K;expected=I+change;actual=A[6*i+3:6*i+6,6*i+3:6*i+6];basis=np.column_stack([(dt*B).ravel(),(dt*dt*K).ravel()]);coeff,_,rank,_=np.linalg.lstsq(basis,(actual-I).ravel(),rcond=None);records.append(dict(variant=variant,body=i,time_s=t,rotation_operator_abs_error_kg_m2=float(np.max(abs(actual-expected))),rotation_operator_relative_error=float(np.linalg.norm(actual-expected)/np.linalg.norm(expected)),isolated_tangent_correction_relative_error=float(np.linalg.norm(actual-I-change)/np.linalg.norm(change)),translation_operator_relative_error=float(np.linalg.norm(A[6*i:6*i+3,6*i:6*i+3]-M[:3,:3])/np.linalg.norm(M[:3,:3])),nonsymmetric_rotation_operator_norm_kg_m2=float(np.linalg.norm(actual-actual.T)),fitted_B_dt_coefficient=float(coeff[0]),fitted_K_dt2_coefficient=float(coeff[1]),coefficient_fit_rank=int(rank),coefficient_fit_relative_residual=float(np.linalg.norm(basis@coeff-(actual-I).ravel())/np.linalg.norm(actual-I))));oldpoints[i]=vec(mass[i][k]['q']).reshape(-1,3)
 result=dict(status='PASS_ACTUAL_NATIVE_ROTATIONAL_OPERATOR' if max(r['isolated_tangent_correction_relative_error'] for r in records)<1e-9 else 'FAIL_ACTUAL_NATIVE_OPERATOR',scope='Read-only actual Native EigenSparseLU12x12 matrix. Independent old mapped mass and world K/B. Rotation/translational blocks normalized SEPARATELY;no mixed-unit dilution/floors. Not full ODE/mass-derivative/Newton/contact/global energy qualification.',producer_sha256=sha(Path(__file__)),records=records,maximum_rotation_abs_error_kg_m2=max(r['rotation_operator_abs_error_kg_m2'] for r in records),maximum_rotation_relative_error=max(r['rotation_operator_relative_error'] for r in records),maximum_isolated_tangent_correction_relative_error=max(r['isolated_tangent_correction_relative_error'] for r in records),maximum_translation_relative_error=max(r['translation_operator_relative_error'] for r in records))
 result.update(operator_hypothesis=a.operator,case=a.case,reference=a.reference,source_summary_sha256=sha(BASE/'results'/a.reference/'summary.json'))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
