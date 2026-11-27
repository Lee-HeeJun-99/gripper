"""Independent actual finite-boundary sign, projection and row-load audit.
Boundary extracted directly from tetra faces, independently of producer skfem
facet ordering. No contact solve and no signed-distance smoothness claim.
"""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_finite_surface1/summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['source_field']['path']);b=np.load(REPO/s['output']['path']);rows=json.loads((REPO/s['rows']['path']).read_text());assert len(rows)==2169;surfaces={}
 for name in sorted(set(r['owner'] for r in rows)):
  X=a[name+'_points_mm'];t=a[name+'_tetra'];o=int(a[name+'_offset']);x=X+a['u_mm'][o:o+3*len(X)].reshape(-1,3);f=np.concatenate([t[:,[1,2,3]],t[:,[0,3,2]],t[:,[0,1,3]],t[:,[0,2,1]]]);parents=np.tile(np.arange(len(t)),4);key=np.sort(f,axis=1);_,first,count=np.unique(key,axis=0,return_index=True,return_counts=True);assert count.max()==2;ix=first[count==1];tri=f[ix];p=parents[ix];v=x[tri];cross=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);flip=np.sum(cross*(v.mean(1)-x[t[p]].mean(1)),1)<0;tri[flip]=tri[flip][:,[0,2,1]];surfaces[name]=(x,tri)
 winding=[];independent_distance=[];signed=[];KKT=[];geometry=[]
 for i,row in enumerate(rows):
  x,tri=surfaces[row['owner']];v=x[tri];q=b['first_points_mm'][i];cp=b['closest_points_mm'][i];r=v-q;length=np.linalg.norm(r,axis=2);num=np.einsum('ij,ij->i',r[:,0],np.cross(r[:,1],r[:,2]));den=length.prod(1)+np.sum(r[:,0]*r[:,1],1)*length[:,2]+np.sum(r[:,1]*r[:,2],1)*length[:,0]+np.sum(r[:,2]*r[:,0],1)*length[:,1];w=float(np.sum(2*np.arctan2(num,den))/(4*np.pi));winding.append(w)
  # Independent vectorized triangle projection via least-squares Gram solve,
  # and all three bounded segments. Compute global min of this complete set.
  e=v[:,1]-v[:,0];f=v[:,2]-v[:,0];d=q-v[:,0];G=np.empty((len(tri),2,2));G[:,0,0]=np.sum(e*e,1);G[:,0,1]=G[:,1,0]=np.sum(e*f,1);G[:,1,1]=np.sum(f*f,1);rhs=np.c_[np.sum(d*e,1),np.sum(d*f,1)];st=np.linalg.solve(G,rhs);plane=v[:,0]+st[:,0,None]*e+st[:,1,None]*f;valid=(st[:,0]>=0)&(st[:,1]>=0)&(st.sum(1)<=1);dist=np.linalg.norm(q-plane,axis=1);dist[~valid]=np.inf;best=float(dist.min())
  for j in range(3):
   edge=v[:,(j+1)%3]-v[:,j];s0=np.clip(np.sum((q-v[:,j])*edge,1)/np.sum(edge*edge,1),0,1);pt=v[:,j]+s0[:,None]*edge;best=min(best,float(np.linalg.norm(q-pt,axis=1).min()))
  independent_distance.append(best);sign=-1 if abs(w)>.5 else 1;signed.append(sign*best)
  # Verify claimed point attains independent global finite distance. No
  # nearest-facet sign is promoted to topology sign at a finite corner.
  geometry.append(abs(np.linalg.norm(q-cp)-best));KKT.append(abs(abs(s['groups'][0]['min_gap_mm'])) if False else abs(abs(b['gap_mm'][i])-best))
 signed=np.array(signed);winding=np.array(winding);distance=np.array(independent_distance);pressure=b['old_pressure_N'];resolved=distance>1e-9;werr=np.minimum(abs(winding),abs(abs(winding)-1));ambiguity=~resolved|(werr>1e-5);sign_mismatch=resolved&(werr<1e-5)&(np.sign(signed)!=np.sign(b['gap_mm']));positive=(signed>1e-8)&(pressure>1e-8);inside=(signed<-1e-8);max_comp=float(np.max(abs(signed*pressure)));active_ambiguous=int(np.sum(ambiguity&(pressure>1e-8)));groups=[]
 for label in sorted(set(r['label'] for r in rows)):
  sel=np.array([r['label']==label for r in rows]);groups.append(dict(label=label,positive_gap_with_old_pressure=int(np.sum(sel&positive)),penetrations=int(np.sum(sel&inside)),ambiguous_active_rows=int(np.sum(sel&ambiguity&(pressure>1e-8))),nearest_facet_sign_mismatches=int(np.sum(sel&sign_mismatch))))
 checks=dict(all2169rows=len(rows)==2169,independent_global_distance=max(geometry)<1e-8,producer_unsigned_distance=max(KKT)<1e-8,resolved_topology_integer=float(werr[resolved].max())<1e-5,old_equilibrium_rejected=bool(max_comp>1e-8 and np.any(positive)))
 np.savez_compressed(out/'topological_geometry.npz',signed_gap_mm=signed,unsigned_distance_mm=distance,winding_number=winding,unresolved_near_surface=ambiguity,nearest_facet_sign_mismatch=sign_mismatch,old_pressure_N=pressure)
 result=dict(status='ACTUAL_P1_FINITE_SURFACE_DISTANCE_VERIFIED_OLD_STATE_REJECTED' if all(checks.values()) else 'ACTUAL_P1_FINITE_SURFACE_INDEPENDENT_CHECK_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],verifier=ref(out/'verifier.py'),output=ref(out/'topological_geometry.npz'),checks={k:bool(v) for k,v in checks.items()},contact_rows=len(rows),maximum_independent_distance_error_mm=max(geometry),maximum_producer_unsigned_distance_error_mm=max(KKT),topology_max_integer_error_resolved=float(werr[resolved].max()),near_surface_unresolved_rows=int(ambiguity.sum()),near_surface_unresolved_active_rows=active_ambiguous,nearest_facet_sign_mismatches=int(sign_mismatch.sum()),sign_mismatch_rows=np.flatnonzero(sign_mismatch).tolist(),positive_gap_with_old_pressure=int(positive.sum()),old_pressure_on_positive_gap_N=float(pressure[positive].sum()),penetrations_below_minus1e8=int(inside.sum()),minimum_signed_gap_mm=float(signed.min()),maximum_signed_gap_mm=float(signed.max()),maximum_complementarity_Nmm=max_comp,groups=groups,contact_solve_eligible=False,contact_update_attempted=False,new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Generalized winding classifies closed deformed coarse tetra boundaries. Nearsurface<=1e-9mm sign unresolved and explicitly reported, not hidden or counted as a physical PASS. This numerical classification threshold does not relax any contact/force/mesh criterion.','Producer closestfacet signs/edgeFD failures remain untouched; only unsigned closestpoint values and resolved topology signs independently checked. Normalcone/semismooth fullmovingowner pullback/finitecontact equilibrium still required.','No deletion of2169rows or sourcepart changes. Existing1%meshFAILs/source minima/Baseanchor/finitewire/friction/protector/globalenergy/full3Finger/Stage3 blocks remain.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
