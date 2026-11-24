"""Floating-point convex clipping of actual wire facets against finite guide solid.

Each actual polygon-frustum ring is the union of convex radial wedges. This
checks entire saved triangles, not just vertices. It is NOT swept/temporal CCD.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from rounded_bore_wire import geometry,inside
def cells(inner,n=32):
 result=[];h=np.pi/n;c=np.cos(h)
 for (x0,r0),(x1,r1) in zip(inner[:-1],inner[1:]):
  slope=(r1-r0)/(x1-x0)
  for j in range(n):
   lo=j*2*np.pi/n;hi=(j+1)*2*np.pi/n;mid=(lo+hi)/2;normal=np.array([np.cos(mid),np.sin(mid)])
   A=np.array([[-1,0,0],[1,0,0],[0,np.sin(lo),-np.cos(lo)],[0,-np.sin(hi),np.cos(hi)],[0,*normal],[slope*c,*(-normal)]]);b=np.array([x0,-x1,0,0,-1.5*c,(r0-slope*x0)*c]);v=np.array([[x,r*np.cos(t),r*np.sin(t)] for x,radius in ((x0,r0),(x1,r1)) for r in (radius,1.5) for t in (lo,hi)]);result.append((A,b,v.min(0),v.max(0)))
 return result
def clip(poly,A,b):
 for normal,offset in zip(A,b):
  if len(poly)==0:return poly
  d=poly@normal+offset;output=[]
  for i,end in enumerate(poly):
   j=i-1;start=poly[j];de=d[i];ds=d[j]
   if (de<=0)!=(ds<=0):output.append(start+(end-start)*(ds/(ds-de)))
   if de<=0:output.append(end)
  poly=np.array(output).reshape(-1,3)
 return poly
def intersections(points,faces,parts,inner):
 triangles=points[faces];tmin=triangles.min(1);tmax=triangles.max(1);tested=0;hits=[]
 for k,(A,b,lower,upper) in enumerate(parts):
  ids=np.flatnonzero(np.all(tmax>=lower,axis=1)&np.all(tmin<=upper,axis=1))
  for i in ids:
   tested+=1;p=clip(triangles[i],A,b)
   if len(p):
    centre=p.mean(0);hits.append(dict(face=int(i),cell=k,intersection_polygon_vertices=len(p),centroid_mm=centre.tolist(),centroid_strictly_inside_solid=bool(inside(centre[None],inner)[0])))
 return tested,hits
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;root=ET.parse(src/'scene.scn').getroot();top=root.find("Node[@name='wire']/Node[@name='wireSurface']/MeshTopology");faces=np.fromstring(top.get('triangles'),sep=' ',dtype=int).reshape(-1,3);m,inner=geometry();eye=root.find("Node[@name='finiteEyelet']/MeshTopology");np.testing.assert_array_equal(np.fromstring(eye.get('position'),sep=' ').reshape(-1,3),m.vertices*.001+[.01,0,0]);np.testing.assert_array_equal(np.fromstring(eye.get('triangles'),sep=' ',dtype=int).reshape(-1,3),m.faces);parts=cells(inner);history=[];witness=[]
 with (src/'surface.csv').open() as f:
  for row in csv.DictReader(f):
   q=(np.fromstring(row['q'],sep=' ').reshape(-1,3)-[.01,0,0])*1000;tested,hits=intersections(q,faces,parts,inner);history.append(dict(time_s=float(row['time_s']),triangle_cell_tests=tested,nonempty_intersections=len(hits),strict_interior_centroids=sum(h['centroid_strictly_inside_solid'] for h in hits)))
   if hits and len(witness)<10:witness.append(dict(time_s=float(row['time_s']),hits=hits))
 bad=sum(r['nonempty_intersections']>0 for r in history);interior=sum(r['strict_interior_centroids']>0 for r in history);d=dict(status='FAIL_SAVED_WIRE_FACET_SOLID_INTERSECTION' if interior else 'UNQUALIFIED_BOUNDARY_CLIPPING_WITNESS' if bad else 'NO_SAVED_WIRE_FACET_SOLID_INTERSECTION_ONLY',outputs=len(history),wire_faces=len(faces),convex_cells=len(parts),outputs_with_clipping_intersections=bad,outputs_with_strict_interior_witnesses=interior,total_triangle_cell_tests=sum(r['triangle_cell_tests'] for r in history),first_witness_time_s=witness[0]['time_s'] if witness else None,scope='Actual complete savedwiretriangles clippedagainst exact polygon-frustum wedge halfspaces inmm,allGuidefaces retained. FLOATINGPOINT algorithm,noerrorfloor/area cutoff. Nonemptyboundary clipping withoutstrictinterior isUNQUALIFIED,notignored. No savedintersection would NOTcertify sweptCCD/interstepgap or beamvolume/endcaps,contactwork/material/time/mesh orgrasp. NoRaw/statecorrection.',source_sha256=sha(Path(__file__)),input_sha256={f:sha(src/f) for f in ('scene.scn','surface.csv')});(out/'history.json').write_text(json.dumps(history));(out/'witness.json').write_text(json.dumps(witness,indent=2));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
