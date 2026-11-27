"""New actual Root/Frame tetra mesh and finite noncoincident shoulder rows.
No reuse of historical equilibrium or deletion/fixation of original variables.
"""
import sys,json,shutil,time
import numpy as np
import gmsh
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_yshoulder_contact import evaluate

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(src.read_text());names=['F0_ROOT_BACK','OPEN_FRAME'];h=float(sys.argv[2]);assert all(sha(REPO/cad['part_references'][n]['path'])==cad['part_references'][n]['SHA256'] for n in names)
 # Record source and generated geometry hashes before meshing, no compilation.
 dump(out/'inputs.json',dict(candidate=ref(src),parts={n:cad['part_references'][n] for n in names},producer=ref(out/'producer.py'),contact_operator=ref(ROOT/'scripts/primary_yshoulder_contact.py'),h_mm=h,meaning='Actual two product bodies, geometry/contact operator validation only. Other76parts remain in assembly. Full remesh/coupled solve still required.'))
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('P1_Ycapture');vols={}
 for n in names:vols[n]=gmsh.model.occ.importShapes(str(REPO/cad['part_references'][n]['path']))
 gmsh.model.occ.synchronize();surfaces={n:[abs(t) for d,t in gmsh.model.getBoundary(v,oriented=False) if d==2] for n,v in vols.items()}
 def plane(t,axis,value):
  b=gmsh.model.getBoundingBox(2,t);return abs(b[axis]-value)<1e-5 and abs(b[axis+3]-value)<1e-5
 faces={}
 for sign in [-1,1]:
  faces[sign]={n:[t for t in surfaces[n] if plane(t,1,sign*(20 if n=='F0_ROOT_BACK' else 20.1)) and (n=='F0_ROOT_BACK' or (gmsh.model.getBoundingBox(2,t)[2]>-7.01 and gmsh.model.getBoundingBox(2,t)[5]<-2.99))] for n in names};assert all(faces[sign].values()),faces
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',h*.1);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',24);gmsh.model.mesh.generate(3)
 nt,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.asarray(nt)[order];xyz=np.asarray(xyz).reshape(-1,3)[order]
 def elements(dim,t,kind,nv):
  types,_,es=gmsh.model.mesh.getElements(dim,t);return [np.searchsorted(nt,np.asarray(e).reshape(-1,nv)) for typ,e in zip(types,es) if typ==kind]
 meshes={};saved={}
 for n in names:
  t=np.concatenate(sum([elements(3,v,4,4) for d,v in vols[n]],[]));used=np.unique(t);p=xyz[used];tt=np.searchsorted(used,t);vol=abs(np.linalg.det(p[tt[:,1:]]-p[tt[:,0,None]])).sum()/6;meshes[n]=dict(nodes=len(p),tetra=len(t),linear_tetra_volume_mm3=float(vol),CAD_volume_mm3=sum(gmsh.model.occ.getMass(3,v) for d,v in vols[n]));saved[n+'_points_mm']=p;saved[n+'_tetra']=tt
 contacts=[];work=[];allrows=[];rng=np.random.default_rng(251)
 for sign in [-1,1]:
  rt=np.concatenate(sum([elements(2,t,2,3) for t in faces[sign]['F0_ROOT_BACK']],[]));ft=np.concatenate(sum([elements(2,t,2,3) for t in faces[sign]['OPEN_FRAME']],[]));allrootnodes=np.unique(rt);rootnodes=allrootnodes[(xyz[allrootnodes,0]>=60-1e-7)&(xyz[allrootnodes,0]<=68+1e-7)&(xyz[allrootnodes,2]>=-6.4-1e-7)&(xyz[allrootnodes,2]<=-3+1e-7)];triangles=xyz[ft];picked=[];missing=[]
  for node in rootnodes:
   p=xyz[node];best=None
   for k,t in enumerate(triangles):
    e=np.cross(t[1]-t[0],t[2]-t[0]);orient=-sign*np.sign(e[1]);r=evaluate(p,t,orient,1.)
    if r['inside']:best=(k,orient,r);break
   if best is None:missing.append(int(node));continue
   k,orient,r=best;t=triangles[k];d=rng.normal(size=(4,3));d*=.005;analytic=float(r['point_gradient']@d[0]+np.sum(r['triangle_gradient']*d[1:]));errs=[]
   for eps in [1e-2,1e-3,1e-4]:
    plus=evaluate(p+eps*d[0],t+eps*d[1:],orient)['gap_mm'];minus=evaluate(p-eps*d[0],t-eps*d[1:],orient)['gap_mm'];errs.append(abs((plus-minus)/(2*eps)-analytic))
   forces=np.vstack([r['point_gradient'],r['triangle_gradient']]);pts=np.vstack([p,t]);force_error=float(np.linalg.norm(forces.sum(0)));moment_error=float(np.linalg.norm(np.cross(pts,forces).sum(0)));bad=evaluate(p+np.array([100.,0,0]),t,orient)
   row=dict(sign=sign,root_point_mm=p.tolist(),owner_triangle_mm=t.tolist(),normal_sign=float(orient),gap_mm=r['gap_mm'],barycentric=r['barycentric'].tolist(),virtual_work_error=errs,force_error_N=force_error,moment_error_Nmm=moment_error,outside_control_rejected=not bad['inside']);allrows.append(row);picked.append(k)
  contacts.append(dict(sign=sign,root_face_nodes=len(allrootnodes),excluded_outside_shoulder_footprint_nodes=len(allrootnodes)-len(rootnodes),root_nodes=len(rootnodes),owner_triangles=len(ft),mapped_rows=len(picked),missing_nodes=missing,actual_root_surface_area_mm2=sum(gmsh.model.occ.getMass(2,t) for t in faces[sign]['F0_ROOT_BACK']),actual_owner_surface_area_mm2=sum(gmsh.model.occ.getMass(2,t) for t in faces[sign]['OPEN_FRAME'])))
 gmsh.finalize();np.savez_compressed(out/'new_mesh.npz',**saved);dump(out/'rows.json',allrows);checks=dict(both_actual_surfaces=all(r['mapped_rows']>0 for r in contacts),all_root_rows_inside_actual_finite_owners=all(not r['missing_nodes'] for r in contacts),original_point1gap=all(abs(r['gap_mm']-.1)<1e-10 for r in allrows),virtual_work_1e_8=all(r['virtual_work_error'][-1]<1e-8 for r in allrows),action_reaction=all(r['force_error_N']<1e-10 and r['moment_error_Nmm']<1e-8 for r in allrows),outside_controls_rejected=all(r['outside_control_rejected'] for r in allrows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_NEW_MESH_FINITE_SHOULDER_OPERATOR_PASS' if all(checks.values()) else 'ACTUAL_P1_NEW_MESH_FINITE_SHOULDER_OPERATOR_FAIL',candidate=ref(src),inputs=ref(out/'inputs.json'),mesh=ref(out/'new_mesh.npz'),contact_rows=ref(out/'rows.json'),checks=checks,meshes=meshes,contacts=contacts,h_mm=h,elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],whole_system_release=False,accepted_elastic_equilibria=0,limitations=['Actual newRoot/Frame tetra mesh and all finite shoulder node projections only. Not a coupled physical solve or stiffness/strength/energy result.','Finite plane gap and exact virtualwork use owner triangle area derivative and independent owner vertices. Owner-domain gate rejects outside projections before evaluating physical reactions.','Other original support/motor/connector/contact constraints must be rebuilt, not silently discarded. All historical2208rows/37rigid/freegamma source matrices preserved. No sourcefield transfer.','No mesh1% or time0.1% certification from an operator identity. Full3Finger remains required.']));print(json.dumps(dict(checks=checks,meshes=meshes,contacts=contacts)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
