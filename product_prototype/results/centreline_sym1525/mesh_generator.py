"""Conforming centreline-refined tetra meshes with matched asymmetric control.
Native FEM unchanged. Added centreline nodes remove the unavoidable odd-cell
reflection ambiguity;no unused void nodes or overlapping material copies.
"""
import json,math,xml.etree.ElementTree as ET
from collections import Counter
import numpy as np
from mechanism_candidates import world
def flat(a):return ' '.join(format(float(x),'.17g') for x in np.asarray(a).ravel())
def generate(c,symmetric):
 f=c['finger'];assert f['root_width']==f['tip_width']==24;xs=np.linspace(0,100,c['simulation']['nx']);ys=[-12,-12+f['rail_width'],0,12-f['rail_width'],12];zs=[-f['rail_thickness'],0,f['skin_thickness']];v=np.array([[x,y,z] for x in xs for y in ys for z in zs]);lookup={tuple(p):i for i,p in enumerate(v)};reflect=np.array([lookup[(x,-y,z)] for x,y,z in v]);idx=lambda i,j,k:(i*5+j)*3+k;t=[]
 for i in range(len(xs)-1):
  for j in range(2 if symmetric else 4):
   for k in range(2):
    if k==0 and j not in (0,3):continue
    ids=[idx(i+a,j+b,k+d) for a,b,d in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1))]
    for q in ((0,1,3,7),(0,3,2,7),(0,2,6,7),(0,6,4,7),(0,4,5,7),(0,5,1,7)):
     tet=[ids[n] for n in q]
     if np.linalg.det((v[tet[1:]]-v[tet[0]]).T)<0:tet[1],tet[2]=tet[2],tet[1]
     t.append(tet)
     if symmetric:
      other=reflect[tet].tolist();other[1],other[2]=other[2],other[1];t.append(other)
 used=sorted({n for tet in t for n in tet});remap={n:i for i,n in enumerate(used)};v=v[used];t=np.array([[remap[n] for n in tet] for tet in t]);faces={}
 for a,b,d,e in t:
  for face in ((b,d,e),(a,e,d),(a,b,e),(a,d,b)):faces.setdefault(tuple(sorted(face)),[]).append(face)
 assert max(map(len,faces.values()))==2;boundary=np.array([r[0] for r in faces.values() if len(r)==1]);edges=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in boundary for i in range(3));assert set(edges.values())=={2},'Nonconforming/cracked boundary';lookup={tuple(p):i for i,p in enumerate(v)};p=np.array([lookup[(x,-y,z)] for x,y,z in v]);invariant={tuple(sorted(x)) for x in t}=={tuple(sorted(x)) for x in p[t]}
 assert invariant==symmetric
 return dict(local_positions_mm=v.tolist(),tetrahedra=t.tolist(),triangles=boundary.tolist()),dict(nodes=len(v),tets=len(t),boundary_triangles=len(boundary),boundary_edge_incidence_exactly2=True,tetra_set_reflection_invariant=invariant,mirror_node_permutation=p.tolist())
def adapt(root,c,old,new):
 local=np.array(new['local_positions_mm']);oldlocal=np.array(old['local_positions_mm']);lookup={tuple(p):i for i,p in enumerate(local)};tet=np.array(new['tetrahedra']);boundary=np.array(new['triangles']);records=[]
 for i,angle in enumerate((0,120,240)):
  f=root.find(f"Node[@name='finger{i}']")
  if f is None:continue
  q=np.array([world(c,p,angle) for p in local])*.001;q[:,2]+=c['research_root_translation_z_mm']*.001;oldq=np.fromstring(f.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);oldpairs=np.fromstring(f.find('SubsetMultiMapping').get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);oldtet=np.array(old['tetrahedra']);before=np.linalg.det((oldq[oldtet[:,1:]]-oldq[oldtet[:,0,None]]).transpose(0,2,1));after=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));assert after.min()>0;ratio=after.sum()/before.sum();assert abs(ratio-1)<1e-12,'Physicalmaterialvolumechanged';existing=np.array([lookup[tuple(p)] for p in oldlocal]);assert abs(q[existing]-oldq).max()<1e-12
  anchors={int(existing[k]):int(index) for k,(owner,index) in enumerate(oldpairs) if owner==1};assert len(anchors)==36;free=[k for k in range(len(local)) if k not in anchors];freemap={k:j for j,k in enumerate(free)};pairs=[[1,anchors[k]] if k in anchors else [0,freemap[k]] for k in range(len(local))];f.find('MechanicalObject').set('position',flat(q));top=f.find('MeshTopology');top.set('position',flat(q));top.set('tetrahedra',flat(tet));top.set('triangles',flat(boundary));f.find('SubsetMultiMapping').set('indexPairs',flat(pairs));node=root.find(f"Node[@name='free{i}']");node.find('MechanicalObject').set('position',flat(q[free]));node.find('FixedProjectiveConstraint').set('indices',' '.join(str(j) for j,k in enumerate(free) if local[k,0]<=c['finger']['clamp_length']))
  skin=np.all(local[boundary,2]>=0,axis=1)
  for name,mask in (('skinCollision',skin),('railCollision',~skin)):
   faces=boundary[mask];ids=np.unique(faces);remap={int(n):j for j,n in enumerate(ids)};triangles=[[remap[int(n)] for n in face] for face in faces];n=f.find(f"Node[@name='{name}']");n.find('MechanicalObject').set('position',flat(q[ids]));n.find('SubsetMapping').set('indices',' '.join(map(str,ids)));mt=n.find('MeshTopology');mt.set('position',flat(q[ids]));mt.set('triangles',flat(triangles));mt.attrib.pop('edges',None)
  records.append(dict(finger=i,volume_ratio=ratio,reference_minimum_det_m3=float(after.min()),old_existing_node_reference_error_m=float(abs(q[existing]-oldq).max()),mapped_anchor_count=len(anchors),free_nodes=len(free)))
 return records
