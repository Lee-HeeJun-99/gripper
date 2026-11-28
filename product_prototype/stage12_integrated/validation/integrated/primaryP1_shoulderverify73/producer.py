"""Independent actual CAD/contact/element/wrench and three-mesh audit.
No solve, no edits to producer fields, no release authority.
"""
import sys,json,time,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
from skfem import MeshTet
from primary_keeper_coupled71 import pointdist
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read

def restrict(poly,axis,value,positive):
 if not poly:return []
 r=[]
 prev=poly[-1];pv=(prev[axis]-value)*(1 if positive else -1)
 for cur in poly:
  cv=(cur[axis]-value)*(1 if positive else -1)
  if (cv>=0)!=(pv>=0):r.append(prev+(cur-prev)*(pv/(pv-cv)))
  if cv>=0:r.append(cur)
  prev,pv=cur,cv
 return r

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_shoulder73a/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);keeper=read(REPO/cad['part_references']['ROOT_SOCKET_KEEPER']['path']);host=read(REPO/cad['part_references']['F0_ROOT_BACK']['path']);rows=[];probes=np.array([[x,y,z] for x in [59.25,60,61,62,63,64,65.5] for y in [-17,-12,-6,0,6,12,17] for z in [2.3,3.] ]);allprobe=[]
 rects=[(57.,58.95,-2.,2.),(61.05,63.,-2.,2.),(58.95,61.05,-2.,-1.05),(58.95,61.05,1.05,2.)]
 for tag in ['primaryP1_shouldercoarse73','primaryP1_shoulderfine73','primaryP1_shoulderfinest73']:
  root=ROOT/'validation/integrated'/tag;d=json.loads((root/'summary.json').read_text());a=np.load(root/'field.npz');p=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];tri=a['boundary_triangles'];f=a['gravity_nodal_force_N'];c=a['contact_nodal_force_N'];lam=a['normal_force_N'];features=json.loads((root/'contact_features.json').read_text());pos=p+u
  xyz=p[t];mat=np.ones((len(t),4,4));mat[:,:,1:]=xyz;iv=np.linalg.inv(mat);grad=iv[:,1:,:].transpose(0,2,1);vol=abs(np.linalg.det(mat))/6;D=np.einsum('tai,taj->tij',u[t],grad);eps=(D+D.transpose(0,2,1))/2;mu=200000/(2*1.3);la=200000*.3/(1.3*.4);stress=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);element=np.einsum('tij,taj,t->tai',stress,grad,vol);internal=np.zeros_like(p)
  for j in range(4):np.add.at(internal,t[:,j],element[:,j])
  force=internal-c-f;energy=float(np.sum(stress*eps*vol[:,None,None]/2));wrench=np.r_[(f+c).sum(0),np.cross(pos-[60,0,-1],f+c).sum(0)];loadcontrol=float(abs(internal-c-1.01*f).max());netinternal=np.r_[internal.sum(0),np.cross(p-[60,0,-1],internal).sum(0)]
  contact=[]
  for i,feat in enumerate(features):
   if lam[i]<=1e-9:continue
   nd=feat['triangle'];b=np.array(feat['barycentric']);point=b@p[nd];deformed=b@pos[nd];contact.append(dict(row=i,normal_force_N=float(lam[i]),reference_keeper_distance_mm=pointdist(keeper,point),reference_Root_distance_mm=pointdist(host,point),deformed_Root_distance_mm=pointdist(host,deformed)))
  # Reclip deformed facets to actual finite Root lands, rather than accepting
  # reference material trim. Every retained polygon vertex controls the planegap.
  bottom=tri[np.all(abs(p[tri,2]+1)<1e-8,axis=1)];gaps=[]
  for nd in bottom:
   for xl,xh,yl,yh in rects:
    poly=list(pos[nd])
    for ax,limit,sign in [(0,xl,True),(0,xh,False),(1,yl,True),(1,yh,False)]:poly=restrict(poly,ax,limit,sign)
    gaps.extend(float(v[2]+1) for v in poly)
  min_gap=min(gaps);m=MeshTet(p.T,t.T);ids=m.element_finder()(probes[:,0],probes[:,1],probes[:,2]);assert np.all(ids>=0);bary=np.einsum('pi,pij->pj',np.c_[np.ones(len(probes)),probes],iv[ids]);samples=np.einsum('pa,pai->pi',bary,u[t[ids]]);allprobe.append(samples)
  checks=dict(independent_element_residual=float(abs(force).max())<1e-8,independent_energy=abs(energy-d['static_energy_Nmm'])<1e-12,all6_deformed_body_wrench=float(abs(wrench).max())<1e-8,linear_internal_force_moment=float(abs(netinternal).max())<1e-8,altered_gravity_rejected=loadcontrol>1e-8,complete_postdeformation_finite_land_gap=min_gap>=-1e-9,reference_active_traction_on_both_actual_solids=all(max(q['reference_keeper_distance_mm'],q['reference_Root_distance_mm'])<1e-7 for q in contact),deformed_active_traction_on_actual_Root=all(q['deformed_Root_distance_mm']<1e-7 for q in contact),original_multipliers_nonnegative=float(lam.min())>=-1e-9,source_checks=all(d['checks'].values()))
  rows.append(dict(source=ref(root/'summary.json'),field=ref(root/'field.npz'),checks={k:bool(v) for k,v in checks.items()},nodes=len(p),tetra=len(t),energy_Nmm=energy,conditional_weight_N=float(-f[:,2].sum()),original_residual_N=float(abs(force).max()),deformed_wrench_residual_N_Nmm=wrench.tolist(),postdeformation_finite_land_min_gap_mm=min_gap,altered_gravity_control_residual_N=loadcontrol,active_contact=contact,maximum_active_deformed_Root_distance_mm=max(q['deformed_Root_distance_mm'] for q in contact),max_stress_MPa=d['max_element_vonMises_MPa']))
 comparisons=[]
 for i,j in [(0,1),(1,2),(0,2)]:
  scalar=abs(rows[i]['energy_Nmm']-rows[j]['energy_Nmm'])/abs(rows[j]['energy_Nmm']);delta=allprobe[i]-allprobe[j];vector=float(np.linalg.norm(delta)/np.linalg.norm(allprobe[j]));comparisons.append(dict(pair=[i,j],energy_relative_finest_denominator=scalar,original_energy_1percent_pass=scalar<=.01,raw98probe_vector_relative_L2=vector,raw98probe_max_vector_difference_mm=float(np.linalg.norm(delta,axis=1).max()),raw98probe_vector_1percent_pass=vector<=.01,whole_domain_vector_computed=False,physical_spatial_gate_pass=False))
 np.savez_compressed(out/'probe_vectors.npz',material_probe_mm=probes,raw_displacement_mm=np.array(allprobe));dependencies=[ROOT/'scripts/primary_shoulder_elastic73b.py',ROOT/'scripts/primary_keeper_finite72.py',ROOT/'scripts/primary_keeper_coupled71.py',S1/'scripts/incremental_stage1.py',S1/'scripts/build_stage1.py',ROOT/'scripts/baseline_registry.py'];dump(out/'summary.json',dict(status='ACTUAL_P1_SHOULDER_INDEPENDENT_LOCAL_AUDIT_SPATIAL_FAIL',candidate_reference=ref(cp),producer=ref(out/'producer.py'),dependencies=[ref(p) for p in dependencies],rows=rows,comparisons=comparisons,all_local_checks_pass=all(all(r['checks'].values()) for r in rows),probe_vectors=ref(out/'probe_vectors.npz'),physical_spatial_gate_pass=False,time_gate_pass=False,global_energy_gate_pass=False,newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Raw98fixedmaterial3vectorprobes; not whole-domain integration or certified motion. All pair/basefinest comparisons retained, no adjacent-onlyPASS.','Same exactCADtotalmass at allmeshes through derivedtributaries; no fittedmaterialdensity. MeshCG/curveddomain still approximate.','Independent localgravity checks do not certify rigidRoot compliance, sourceallowables, all83equilibria, bolt/nut/thread/preload, dynamicenergy or actual100g grasp.']));print(json.dumps(dict(rows=[dict(nodes=r['nodes'],checks=r['checks']) for r in rows],comparisons=comparisons)));return 0 if all(all(r['checks'].values()) for r in rows) else 2
if __name__=='__main__':sys.exit(main())
