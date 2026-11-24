"""Independent ray/nearest-triangle check of clipping witnesses on actual Native facets."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from rounded_bore_wire import geometry
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='rounded_partitioned_full1650');p.add_argument('--witness-case',default='rounded_partitioned_surface1651');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;wsrc=BASE/'results'/a.witness_case;witness=json.loads((wsrc/'witness.json').read_text());times={r['time_s'] for r in witness};actual={}
 with (src/'surface.csv').open() as f:
  for row in csv.DictReader(f):
   t=float(row['time_s'])
   if t in times:actual[t]=(np.fromstring(row['q'],sep=' ').reshape(-1,3)-[.01,0,0])*1000
 root=ET.parse(src/'scene.scn').getroot();faces=np.fromstring(root.find("Node[@name='wire']/Node[@name='wireSurface']/MeshTopology").get('triangles'),sep=' ',dtype=int).reshape(-1,3);m,_=geometry();points=[];triangles=[];meta=[]
 for r in witness:
  for h in r['hits']:
   points.append(h['centroid_mm']);triangles.append(actual[r['time_s']][faces[h['face']]]);meta.append(dict(time_s=r['time_s'],wire_face=h['face']))
 points=np.array(points);triangles=np.array(triangles);nearest=trimesh.triangles.closest_point(triangles,points);face_error=np.linalg.norm(nearest-points,axis=1)*.001;bary=trimesh.triangles.points_to_barycentric(triangles,points);ray=m.contains(points);_,depth,guide_face=trimesh.proximity.closest_point(m,points);proven=ray&(depth>0)&(face_error<=1e-12)&np.all(bary>=0,axis=1)&np.all(bary<=1,axis=1);records=[]
 for i,r in enumerate(meta):r.update(point_mm=points[i].tolist(),on_actual_wire_face_error_m=float(face_error[i]),wire_barycentric=bary[i].tolist(),independent_guide_ray_inside=bool(ray[i]),inside_guide_depth_mm=float(depth[i]),nearest_guide_face=int(guide_face[i]),interior_wire_face_witness=bool(proven[i]));records.append(r)
 d=dict(status='FAIL_INDEPENDENT_NATIVE_WIRE_FACET_INSIDE_GUIDE' if proven.any() else 'UNQUALIFIED_NO_INDEPENDENT_INTERIOR_WITNESS',case=a.case,witness_case=a.witness_case,checked_points=len(points),independently_proven_interior_wire_face_points=int(proven.sum()),maximum_actual_wire_face_error_m=float(face_error.max()),minimum_proven_interior_depth_mm=float(depth[proven].min()) if proven.any() else None,maximum_proven_interior_depth_mm=float(depth[proven].max()) if proven.any() else None,scope='Independent installed trimesh raycontainment+nearest actualGuide triangleinmm,actualNativeWiretriangle barycentrics/plane. No newNative/prescribedstate/area cutoffs orgeometryerrorfloor. A strictlyinterior pointonactualsavedwirefacet provespenetration evenwhenALLsavedverticesoutside. Prefix-derived witnesses explicitly tested against actualFULL1650 savedq,not blindly transferred. NotCCD/wholegrasp/material/time/meshPASS.',source_sha256=sha(Path(__file__)),input_sha256={'scene':sha(src/'scene.scn'),'surface':sha(src/'surface.csv'),'witness':sha(wsrc/'witness.json')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'points.json').write_text(json.dumps(records,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
