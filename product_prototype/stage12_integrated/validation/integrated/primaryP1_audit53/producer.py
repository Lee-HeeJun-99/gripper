"""Independent saved point-wrench reconstruction and minimum-L1 separating twist."""
import json,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,ref,dump
out=ROOT/'validation/integrated/primaryP1_audit53';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_bore53/summary.json';d=json.loads(sp.read_text());names=d['body_names'];O=np.array(d['origin_mm']);F=np.array(d['external_load']);cols=[];errors=[]
for r in d['contacts']:
 c=np.zeros((18,6));i=names.index(r['body_i']);j=names.index(r['body_j'])
 for s in r.get('quadrature',[dict(point_mm=r.get('point_mm'),normal=r.get('force_on_i'),area_mm2=r.get('weight'))]):
  f=np.array(s['normal'])*s['area_mm2'];w=np.r_[f,np.cross(np.array(s['point_mm'])-O,f)];c[i]+=w;c[j]-=w
 cols.append(c.ravel());errors.append(float(max(abs(c.ravel()-r['column']))))
A=np.array(cols).T;n=108
# Minimize L1 witness;one receiver/support relative work. Support zero is rigid gauge for witness only.
U=np.vstack([np.c_[-A.T,np.zeros((A.shape[1],n))],np.c_[np.eye(n),-np.eye(n)],np.c_[-np.eye(n),-np.eye(n)] ]);b=np.zeros(len(U));bounds=[(None,None)]*n+[(0,None)]*n
for i in range(102,108):bounds[i]=(0,0)
for i,name in enumerate(names):
 if 'SPLIT_PIN' in name:
  for k in range(6):bounds[i*6+k]=(0,0)
r=linprog(np.r_[np.zeros(n),np.ones(n)],A_ub=U,b_ub=b,A_eq=np.r_[F,np.zeros(n)][None,:],b_eq=[1.],bounds=bounds,method='highs');assert r.success;v=r.x[:n];cert=dict(external_positive_work=float(F@v),minimum_contact_work=float(min(A.T@v)),body_twists=[dict(body=name,twist=v[i*6:i*6+6].tolist()) for i,name in enumerate(names)])
# Conditional planar statics:adding constrained Rx/Ry ports exposes search-subspace scope only.
ports=np.zeros((108,2*18));
for i in range(18):ports[i*6+3,i*2]=1;ports[i*6+4,i*2+1]=1
B=np.c_[A,ports];s=linprog(np.ones(B.shape[1]),A_eq=B,b_eq=-F,bounds=[(0,None)]*A.shape[1]+[(None,None)]*ports.shape[1],method='highs')
checks=dict(independent_columns=max(errors)<1e-10,positive_external_work=abs(F@v-1)<1e-8,nonnegative_contact_work=min(A.T@v)>-1e-8,original_full108DOF_infeasible=not d['solution']['feasible']);dump(out/'summary.json',dict(status='ACTUAL_P1_FRESH_ENDPOINT_INDEPENDENT_FARKAS_AUDIT_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_ENDPOINT_AUDIT_FAIL',candidate=d['candidate'],producer=ref(out/'producer.py'),source=ref(sp),checks=checks,independent_column_error=max(errors),Farkas_certificate=cert,planar_with_unimplemented_pitch_roll_ports_feasible=bool(s.success),conditional_port_residual=None if not s.success else float(max(abs(B@s.x+F))),unimplemented_pitch_roll_ports=None if not s.success else s.x[A.shape[1]:].reshape(18,2).tolist(),whole_system_release=False,newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0,limitations=['Gaugefixedsupport only for constructing relativeworkwitness;actualstatics has no declaredsupportfixation','Certificate rejects this finite310contactset/pose only;not productfailure orcompletecontactsequence','Conditionalplanarports are unimplemented and NEVER physicalreactions','Sourcepose also has pininterference independentlyrecorded;no physicalendpointqualification']));print(json.dumps(dict(checks=checks,certificate=cert,planar=s.success)))
