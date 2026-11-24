"""One documented stock RayTrace/Octree capability contrast,not wire/grasp dynamics."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_bending_coupon import guarded
csv.field_size_limit(16*1024*1024)
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def read(p):return list(csv.DictReader(p.open()))
def close_wire(q,f):
 n=len(q);q=np.vstack([q,q[:16].mean(0),q[-16:].mean(0)]);caps=[]
 for j in range(16):caps.extend(((n,(j+1)%16,j),(n+1,n-16+j,n-16+(j+1)%16)))
 f=np.vstack([f,caps]);m=trimesh.Trimesh(q*1000,f,process=False);assert m.is_watertight and m.is_winding_consistent and m.volume>0;return q,f,float(m.volume)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/finite_surface_capability1665/control';sdk=Path('/home/ubuntu/SOFA/v26.06.00');records=[]
 for ray in (False,True):
  d=out/('ray' if ray else 'closed_control');d.mkdir();root=ET.parse(src/'scene.scn').getroot();col=root.find("Node[@name='wire']/Node[@name='wireSurface']");q=np.fromstring(col.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);old=np.fromstring(col.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);q,f,volume=close_wire(q,old);col.find('MechanicalObject').set('position',flat(q));col.find('MeshTopology').set('position',flat(q));col.find('MeshTopology').set('triangles',flat(f));guide=root.find("Node[@name='finiteEyelet']");original=np.fromstring(guide.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);parts=[]
  for node in list(guide.findall('Node')):parts.extend(np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3).tolist());guide.remove(node)
  assert sorted(map(tuple,parts))==sorted(map(tuple,original));ET.SubElement(guide,'TriangleOctreeCollisionModel' if ray else 'TriangleCollisionModel',moving='0',simulated='0',group='2')
  if ray:root.find('BVHNarrowPhase').tag='RayTraceNarrowPhase';col.find('TriangleCollisionModel').tag='TriangleOctreeCollisionModel'
  assert all(col.find(k+'CollisionModel') is not None and guide.find(k+'CollisionModel') is not None for k in ('Line','Point'))
  for n in root.iter():
   for k,value in list(n.attrib.items()):n.set(k,value.replace(str(src),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');(d/'geometry.json').write_bytes((src/'geometry.json').read_bytes());pre=dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(d/'scene.scn'),wire_original_faces=len(old),wire_faces=len(f),wire_added_cap_faces=32,closed_wire_volume_mm3=volume,Guide_exact_oriented_face_union=True,guide_faces=len(original),ray=ray,change='BOTH variants:close physicalfinitewireendcaps,2newendcentrepoints/32facesfarfromGuide,andaggregateexactGuidefacets intoONEclosedmodel. Rayvariant ONLY replacesBVH+Triangle models bydocumentedstockRayTraceNarrowPhase+TriangleOctree models. OriginalALLLine/Pointfeatures stayenabled;whetherRayalgorithm uses them isNOTassumed.',assumptions='Sameinitialstaticactualwitness geometry/freeRigidwire/inertia assumption,NOTBeam/cable/history/grasp. Minintersection andallphysicaldistances/dt/friction/tolerances unchanged. Algorithm/modelcontract changes together;not isolatedoneparameterphysics superiorityclaim.',installed_documentation_sha256={str(f):sha(f) for f in [sdk/'include/Sofa.Component.Collision.Detection.Algorithm/sofa/component/collision/detection/algorithm/RayTraceNarrowPhase.h',sdk/'share/sofa/examples/Component/Collision/Detection/RayTraceCollision.scn']},SDK=str(sdk),steps=2,memory_GiB=4,child_limit_s=60);(d/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded([str(sdk/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',str(d/'scene.scn')],d/'process',60);rows=read(d/'states.csv') if (d/'states.csv').exists() else [];logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));response=read(d/'response_rows.csv') if (d/'response_rows.csv').exists() else [];pairs={}
  for r in response:
   if float(r['lambda_Ns'])!=0:key=r['model0']+' | '+r['model1'];pairs[key]=pairs.get(key,0)+1
  record=dict(ray=ray,process=proc,outputs=len(rows),Native_execution_valid=proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==2,actual_nonzero_response_pairs=pairs);records.append(record);(d/'summary.json').write_text(json.dumps(dict(**record,status='NATIVE_CAPABILITY_EXECUTION_ONLY',scope='Do notinferphysicalcontactcorrectnessfromzeroexit ornonzerorows;independentsolid/facetgeometry required.'),indent=2))
 result=dict(status='STOCK_RAYTRACE_CAPABILITY_TRIALS_ONLY',records=records,source_sha256=sha(Path(__file__)),scope='Native installed alternativealgorithm/modelcontract,notcustomsolver. Samephysicalclosedsolid inbothvariants;allsourcefacetsandLine/Pointmodels retained. No actualwireforce/sliding/grasp/time/mesh/material qualification. Independentfeaturegeometry andresponsecoverage required.');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
