"""Conforming edge bisection of the same actual plate's fixed polyhedral domain.
Separates volume approximation from curved boundary re-tessellation. This is
NOT an exact curved CAD domain or a curved-boundary convergence certificate.
"""
import numpy as np,json
from baseline_registry import ROOT,ref,dump

def meshpart(path,h,curv,level,out):
 src=ROOT/'validation/integrated/primaryP1_bothfast68h5';s=json.loads((src/'summary.json').read_text());a=np.load(src/'field.npz');p=a['points_mm'].copy();t=a['tetra'].copy();originalp=p.copy();originalt=t.copy();journals=[]
 for depth in range(int(level)):
  edges=np.unique(np.sort(np.concatenate([t[:,[i,j]] for i in range(4) for j in range(i+1,4)]),axis=1),axis=0);d=p[edges[:,1]]-p[edges[:,0]];length=np.linalg.norm(d,axis=1);selected=edges[(abs(d[:,2])/length>.85)&(abs(d[:,2])>2.5/(2**depth))&(p[edges].mean(1)[:,2]>-138.000001)];newpoints=[];splits=0
  for i,j in selected:
   assert not(ROOT/'runtime/STOP').exists()
   mask=np.any(t==i,axis=1)&np.any(t==j,axis=1);old=t[mask];assert len(old)>0
   k=len(p)+len(newpoints);newpoints.append((p[i]+p[j])/2);left=old.copy();right=old.copy();left[left==i]=k;right[right==j]=k;t=np.concatenate([t[~mask],left,right]);splits+=len(old)
  if newpoints:p=np.concatenate([p,np.array(newpoints)])
  journals.append(dict(depth=depth+1,selected_original_edges=len(selected),tetra_splits=splits,nodes=len(p),tetra=len(t)));dump(out/f'selected_edges_{depth+1}.json',selected.tolist())
 faces=np.concatenate([t[:,[0,1,2]],t[:,[0,1,3]],t[:,[0,2,3]],t[:,[1,2,3]]]);sortedfaces=np.sort(faces,axis=1);uniq,index,count=np.unique(sortedfaces,axis=0,return_index=True,return_counts=True);assert set(count.tolist())<=set([1,2]);tri=faces[index[count==1]]
 V=s['CAD_volume_mm3'];vol=abs(np.linalg.det(p[t[:,1:]]-p[t[:,0,None]]))/6;V0=abs(np.linalg.det(originalp[originalt[:,1:]]-originalp[originalt[:,0,None]]))/6
 # Midpoint edge bisection preserves all old facets, including original curved
 # surface chord errors. The new midpoint lies in its original edge/facet.
 originalfloor=np.unique(originalt[np.all(abs(originalp[originalt,2]+170)<1e-7,axis=1)]) if False else a['floor_nodes'];newfloor=np.unique(tri[np.all(abs(p[tri,2]+170)<1e-7,axis=1)])
 assert np.array_equal(originalfloor,newfloor);assert abs(vol.sum()/V0.sum()-1)<1e-12
 np.savez_compressed(out/'mesh.npz',points_mm=p,tetra=t,surface_triangles=tri)
 dump(out/'mesh_geometry.json',dict(source_STEP=ref(path),source_polyhedral_field=ref(src/'field.npz'),levels=int(level),journals=journals,nodes=len(p),tetra=len(t),fixed_polyhedral_volume_mm3=float(V0.sum()),refined_volume_mm3=float(vol.sum()),relative_polyhedral_volume_error=float(abs(vol.sum()/V0.sum()-1)),CAD_volume_mm3=V,relative_CAD_volume_error=float(abs(vol.sum()/V-1)),physical_floor_nodes_unchanged=True,all_boundary_faces_incidence_1_or_2=True,mesh=ref(out/'mesh.npz'),policy='Conforming bisection ALL incident tetra for each selected original edge; cosine z>.85, dz>2.5/2^depth mm, midpoint z>-138mm. Originalpolyhedral domain exactly retained; no claim boundary chords are exact CAD. Material/load/contact criteria unchanged.'))
 return p,t,tri,V
