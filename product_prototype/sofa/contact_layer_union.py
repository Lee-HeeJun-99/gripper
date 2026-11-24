"""Exterior of bonded Skin+Rail+layer volume,not disabled hardware collision.

Shared material-interface triangles cancel exactly by vertex identity. All other
original exterior triangles remain. Single collision surface avoids treating a
perfectly bonded interface as an independent unilateral contact constraint.
"""
import xml.etree.ElementTree as ET
import numpy as np
from b3_contact_layer_native import add,flat

def exterior(mesh,g):
 old=np.array(mesh['tetrahedra']);count=len(mesh['local_positions_mm']);pad=np.array(g['tetrahedra']);parents=g['bottom_Skin_parent_indices'];remap=np.array([parents[k//2] if k%2==0 else count+k//2 for k in range(len(g['local_positions_mm']))]);new=remap[pad];faces={}
 for part,tets in [('original',old),('layer',new)]:
  for a,b,c,d in tets:
   for f in ((b,c,d),(a,d,c),(a,b,d),(a,c,b)):faces.setdefault(tuple(sorted(f)),[]).append((f,part))
 assert max(map(len,faces.values()))<=2
 boundary=[v[0] for v in faces.values() if len(v)==1];interfaces=[key for key,v in faces.items() if len(v)==2 and v[0][1]!=v[1][1]]
 expected={tuple(sorted(f)) for f in g['triangles'] if all(k%2==0 for k in f)};expected={tuple(sorted(remap[list(f)])) for f in expected};assert set(interfaces)==expected and len(interfaces)==g.get('expected_interface_triangles',24)
 original=set(map(lambda f:tuple(sorted(f)),mesh['triangles']));retained={tuple(sorted(f)) for f,part in boundary if part=='original'};assert retained==original-set(interfaces)
 used=sorted({int(v) for f,_ in boundary for v in f});inv={k:i for i,k in enumerate(used)};tri=np.array([[inv[k] for k in f] for f,_ in boundary]);edges={}
 for f in tri:
  for a,b in zip(f,np.roll(f,-1)):edges[tuple(sorted([int(a),int(b)]))]=edges.get(tuple(sorted([int(a),int(b)])),0)+1
 assert set(edges.values())=={2},'exterior must be closed manifold'
 return dict(used=used,triangles=tri.tolist(),face_material=[p for _,p in boundary],interface_triangles_cancelled=len(interfaces),original_exterior_triangles=len(original),original_exterior_retained=len(retained),new_layer_exterior_triangles=sum(p=='layer' for _,p in boundary),closed_edge_incidence=2,original_node_count=count)

def apply_union(root,mesh,g,out):
 d=exterior(mesh,g);count=d['original_node_count']
 for i in range(3):
  film=root.find(f"Node[@name='finger{i}']");old_faces=set()
  for label in ('skinCollision','railCollision'):
   n=film.find(f"Node[@name='{label}']");ids=np.fromstring(n.find('SubsetMapping').get('indices'),sep=' ',dtype=int);tt=np.fromstring(n.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);old_faces.update(tuple(sorted(f)) for f in ids[tt]);film.remove(n)
  assert old_faces=={tuple(sorted(f)) for f in mesh['triangles']},'old collision coverage must equal original exterior'
  q0=np.fromstring(film.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);allq=np.vstack([q0,np.array(g['world_reference_m'][i])[1::2]])
  layer=root.find(f"Node[@name='contactLayer{i}']")
  for n in list(layer):
   if n.tag in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):layer.remove(n)
  surface=add(layer,'Node',name='exterior');add(surface,'MeshTopology',name='topology',position=flat(allq[d['used']]),triangles=flat(d['triangles']));add(surface,'MechanicalObject',name='surface',template='Vec3d',position=flat(allq[d['used']]));pairs=[]
  for k in d['used']:pairs.extend([0,k] if k<count else [1,2*(k-count)+1])
  add(surface,'SubsetMultiMapping',template='Vec3d,Vec3d',input=f'@../../finger{i}/dofs @../dofs',output='@surface',indexPairs=' '.join(map(str,pairs)),mapMatrices=1)
  for model in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):add(surface,model,group=1)
 for observer in list(root):
  if observer.tag=='NativeContactRows' and any('/skinCollision/'in v or '/railCollision/'in v for v in observer.attrib.values()):root.remove(observer)
 add(root,'NativeContactRows',solver='@constraints',body='@object/rigid',filename=out/'composite_rows.csv',**{f'film{i}':f'@contactLayer{i}/exterior/surface' for i in range(3)})
 return d
