"""Actual saved wire-edge/Guide-facet crossing vs installed registered pair coverage."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from rounded_bore_wire import geometry
csv.field_size_limit(16*1024*1024)
def segment_triangle(a,b,triangles):
 v=triangles[:,0];u=triangles[:,1]-v;w=triangles[:,2]-v;n=np.cross(u,w);direction=b-a;den=n@direction;valid=den!=0;t=np.full(len(triangles),np.nan);t[valid]=np.sum(n[valid]*(v[valid]-a),axis=1)/den[valid];q=a+t[:,None]*direction;d=q-v;uu=np.sum(u*u,axis=1);ww=np.sum(w*w,axis=1);uw=np.sum(u*w,axis=1);du=np.sum(d*u,axis=1);dw=np.sum(d*w,axis=1);det=uu*ww-uw*uw;s=(du*ww-dw*uw)/det;r=(dw*uu-du*uw)/det;mask=valid&(t>0)&(t<1)&(s>=0)&(r>=0)&(s+r<=1);return np.flatnonzero(mask),q,t,s,r
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/wire_local_mesh_pilot1655';reference=BASE/'results/wire_local_mesh_facet_reference1660/points.json';w=json.loads(reference.read_text());times={r['time_s'] for r in w};poses={}
 with (src/'surface.csv').open() as f:
  for r in csv.DictReader(f):
   t=float(r['time_s'])
   if t in times:poses[t]=(np.fromstring(r['q'],sep=' ').reshape(-1,3)-[.01,0,0])*1000
 root=ET.parse(src/'scene.scn').getroot();faces=np.fromstring(root.find("Node[@name='wire']/Node[@name='wireSurface']/MeshTopology").get('triangles'),sep=' ',dtype=int).reshape(-1,3);m,_=geometry();records=[];seen=set()
 for r in w:
  key=(r['time_s'],r['wire_face'])
  if key in seen:continue
  seen.add(key);v=poses[key[0]][faces[key[1]]]
  for edge in range(3):
   ids,points,t,s,b=segment_triangle(v[edge],v[(edge+1)%3],m.triangles)
   for i in ids:records.append(dict(time_s=key[0],wire_face=key[1],wire_edge_vertices=[int(faces[key[1],edge]),int(faces[key[1],(edge+1)%3])],guide_face=int(i),segment_fraction=float(t[i]),guide_triangle_barycentric=[float(1-s[i]-b[i]),float(s[i]),float(b[i])],intersection_point_mm=points[i].tolist()))
 registry=BASE/'results/finite_surface_capability1665/probe/registry.csv';rr=list(csv.DictReader(registry.open()));pair=[r for r in rr if r['class0']=='LineCollisionModel' and r['class1']=='TriangleCollisionModel'];assert pair and all(r['supported']=='0' for r in pair);d=dict(status='ACTUAL_WIRE_EDGE_GUIDE_FACET_CROSSING_WITH_NULL_NATIVE_PAIR' if records else 'UNQUALIFIED_NO_EDGE_FACET_WITNESS',actual_segment_triangle_crossings=len(records),unique_wire_faces=len(seen),actual_registered_LineTriangle_supported=False,scope='Read-only geometry atactual1655acceptedstates;strictsegmentinterior andtrianglebarycentrics,no artificialerrorfloor. ActualregisteredMinLineTriangleNULL,butrelatedpoint/linepairs stillrespond:NOTproof ofsolewholegraspfailurecause or impossibilityofallNativealgorithms. Notnewcontactlaw/solver orstaticposegraspclaim.',source_sha256=sha(Path(__file__)),input_sha256={'scene':sha(src/'scene.scn'),'surface':sha(src/'surface.csv'),'witness':sha(reference),'registry':sha(registry)});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'crossings.json').write_text(json.dumps(records,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
