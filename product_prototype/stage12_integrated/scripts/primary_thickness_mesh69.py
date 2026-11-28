"""Affine thickness-metric remeshing of the exact same imported plate solid.
Scale CAD z before meshing then invert ALL coordinates. Material/geometry unchanged.
This is an anisotropic discretization contrast, not physical plate thickening.
"""
import gmsh,numpy as np
from baseline_registry import dump,ref

def meshpart(path,h,curv,scale,out):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('same_actual_P1_thickness_metric')
 vs=gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize();V=sum(gmsh.model.occ.getMass(d,t) for d,t in vs)
 bounds=np.array([gmsh.model.occ.getBoundingBox(d,t) for d,t in vs]);gmsh.model.occ.dilate(vs,0,0,-170,1,1,scale);gmsh.model.occ.synchronize();scaledV=sum(gmsh.model.occ.getMass(d,t) for d,t in vs)
 assert abs(scaledV/(V*scale)-1)<1e-10
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',.04);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',curv);gmsh.model.mesh.generate(3)
 nt,p,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.array(nt)[order];p=np.array(p).reshape(-1,3)[order];p[:,2]=-170+(p[:,2]+170)/scale
 ty,_,e=gmsh.model.mesh.getElements(3);t=np.concatenate([np.searchsorted(nt,np.array(a).reshape(-1,4)) for k,a in zip(ty,e) if k==4]);ty,_,e=gmsh.model.mesh.getElements(2);tri=np.concatenate([np.searchsorted(nt,np.array(a).reshape(-1,3)) for k,a in zip(ty,e) if k==2]);gmsh.finalize();ids=np.unique(t);p,t,tri=p[ids],np.searchsorted(ids,t),np.searchsorted(ids,tri)
 vol=abs(np.linalg.det(p[t[:,1:]]-p[t[:,0,None]]))/6
 np.savez_compressed(out/'mesh.npz',points_mm=p,tetra=t,surface_triangles=tri)
 dump(out/'mesh_geometry.json',dict(source_STEP=ref(path),thickness_metric_scale=scale,inverse_affine_origin_mm=[0,0,-170],CAD_volume_mm3=V,scaled_CAD_volume_mm3=scaledV,physical_tetra_volume_mm3=float(vol.sum()),relative_volume_error=float(abs(vol.sum()/V-1)),nodes=len(p),tetra=len(t),original_CAD_bounds_mm=bounds.tolist(),physical_mesh_bounds_mm=np.r_[p.min(0),p.max(0)].tolist(),mesh=ref(out/'mesh.npz'),physical_geometry_changed=False,material_changed=False,scope='Affine CAD pullback; exact same surfaces before linear facet approximation. No material fit or constraint change.'))
 return p,t,tri,V
