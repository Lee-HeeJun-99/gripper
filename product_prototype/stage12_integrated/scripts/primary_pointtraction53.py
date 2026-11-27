"""Actual bound quadrature points with independent nonnegative forces.
Tests uniform-patch restriction;not elastic finitepressure or operating qualification.
"""
import json,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,ref,dump
out=ROOT/'validation/integrated/primaryP1_pointtraction53';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_contact53c/summary.json';d=json.loads(sp.read_text());O=np.array(d['origin_mm']);names=d['body_names'];F=np.array(d['external_load']);cols=[];records=[]
for r in d['contacts']:
 if 'quadrature' not in r:cols.append(r['column']);records.append(dict(label=r['label'],body_i=r['body_i'],body_j=r['body_j'],point_mm=r['point_mm'],normal=r['force_on_i'],area_weight=r['weight']));continue
 for j,s in enumerate(r['quadrature']):
  f=np.array(s['normal']);w=np.r_[f,np.cross(np.array(s['point_mm'])-O,f)];col=np.zeros((18,6));col[names.index(r['body_i'])]+=w;col[names.index(r['body_j'])]-=w;cols.append(col.ravel().tolist());records.append(dict(label=r['label']+'_q'+str(j),body_i=r['body_i'],body_j=r['body_j'],point_mm=s['point_mm'],normal=s['normal'],area_weight=s['area_mm2']))
A=np.array(cols).T
# Scale moment equations by actual100mm span to avoid unit scaling dominating feasibility.
scale=np.tile([1.,1.,1.,.01,.01,.01],18)
def solve(ix):
 r=linprog(np.ones(len(ix)),A_eq=scale[:,None]*A[:,ix],b_eq=-scale*F,bounds=(0,None),method='highs');return dict(feasible=bool(r.success),message=r.message,indices=ix,reactions_N=None if not r.success else r.x.tolist(),unscaled_residual=None if not r.success else float(max(abs(A[:,ix]@r.x+F))))
s=solve(list(range(len(records))));controls=[]
for p in ['guide','thread','socket','keycage','nutcage']:
 controls.append(dict(removed=p,**solve([i for i,r in enumerate(records) if not r['label'].startswith(p)])))
cert=None
if not s['feasible']:
 r=linprog(np.r_[np.zeros(108),np.ones(108)],A_ub=np.vstack([np.c_[-A.T,np.zeros((A.shape[1],108))],np.c_[np.eye(108),-np.eye(108)],np.c_[-np.eye(108),-np.eye(108)]]),b_ub=np.zeros(A.shape[1]+216),A_eq=np.r_[F,np.zeros(108)][None,:],b_eq=[1.],bounds=[(None,None)]*108+[(0,None)]*108,method='highs')
 if r.success:cert=dict(twist=r.x[:108].tolist(),external_positive_work=float(F@r.x[:108]),minimum_contact_work=float(min(A.T@r.x[:108])))
dump(out/'summary.json',dict(status='ACTUAL_P1_BOUND_POINT_TRACTION_CONDITIONAL_UNIT_PASS_NOT_RELEASE' if s['feasible'] and s['unscaled_residual']<1e-8 else 'ACTUAL_P1_BOUND_POINT_TRACTION_UNIT_FAIL',candidate=d['candidate'],producer=ref(out/'producer.py'),source=ref(sp),actual_bound_thread_points=4*192,actual_contact_columns=len(records),DOFs=108,point_contacts=records,columns=cols,external_load=F.tolist(),solution=s,removed_path_controls=controls,Farkas_certificate=cert,uniform_patch_parent_feasible=d['solution']['feasible'],whole_system_release=False,newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0,normalized_conditional_equilibria=int(s['feasible']),limitations=['IndependentnonnegativeGauss-pointforcesareanexpandedrigidcone,notelasticpressure,continuouscontact,materialcapacity or100goperatingload','Allpointpositions/normalsboundbyparentactualBRepjournals;olduniformpatchconstraintisacomparison,notphysicalcriteriarelaxation','No friction/preload/fixedrotation/hostfixture added;all108DOFs retained','Furthercontact/forcefieldconvergence,actualoffaxis takeup/pinpath/fullassembly/mesh/time/globalenergy remainunqualified']));print(json.dumps(dict(feasible=s['feasible'],residual=s['unscaled_residual'],contacts=len(records),certificate=cert is not None)))
