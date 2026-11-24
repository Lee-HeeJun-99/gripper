"""ONLY two missing static coupon cells; reuse already completed diagonal cells."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from raytrace_finite_surface import close_wire,flat
csv.field_size_limit(16*1024*1024)
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/finite_surface_capability1665/control';records=[]
 for caps,aggregate in ((False,True),(True,False)):
  d=out/('open_aggregate' if aggregate else 'closed_partition');d.mkdir();root=ET.parse(src/'scene.scn').getroot();col=root.find("Node[@name='wire']/Node[@name='wireSurface']");originalq=np.fromstring(col.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);originalf=np.fromstring(col.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)
  if caps:
   q,f,volume=close_wire(originalq,originalf);col.find('MechanicalObject').set('position',flat(q));col.find('MeshTopology').set('position',flat(q));col.find('MeshTopology').set('triangles',flat(f))
  if aggregate:
   guide=root.find("Node[@name='finiteEyelet']");original=np.fromstring(guide.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);parts=[]
   for node in list(guide.findall('Node')):parts.extend(np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3).tolist());guide.remove(node)
   assert sorted(map(tuple,parts))==sorted(map(tuple,original));ET.SubElement(guide,'TriangleCollisionModel',moving='0',simulated='0',group='2')
  for n in root.iter():
   for k,value in list(n.attrib.items()):n.set(k,value.replace(str(src),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');(d/'geometry.json').write_bytes((src/'geometry.json').read_bytes());(d/'preflight.json').write_text(json.dumps(dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(d/'scene.scn'),caps=caps,Guide_aggregate=aggregate,wire_original_vertices=len(originalq),wire_original_faces=len(originalf),change='ONLYcaps OR ONLYGuideTriangleownershipfromsame1665staticinitialreference;alloriginalfaces/Line/Pointfeatures retained. Sameassumedrigidmass/inertia,dt,mu0,distances,solver. NOTelasticwire/grasp/historyrestart.',reuse_completed_other_cells=['finite_surface_capability1665/control','raytrace_finite_surface1668/closed_control'],SDK='/home/ubuntu/SOFA/v26.06.00',memory_GiB=4,child_limit_s=60),indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',str(d/'scene.scn')],d/'process',60);rows=read(d/'states.csv') if (d/'states.csv').exists() else [];logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));r=dict(caps=caps,Guide_aggregate=aggregate,process=proc,outputs=len(rows),status='NATIVE_STATIC_FACTORIAL_EXECUTION_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==2 else 'FAIL_NATIVE_FACTORIAL');records.append(r);(d/'summary.json').write_text(json.dumps(r,indent=2))
 d=dict(status='STATIC_MISSING_FACTORIAL_CELLS_EXECUTED_ONLY',records=records,source_sha256=sha(Path(__file__)),scope='Factorialcauseisolation atknowninitialgeometry,notactuation/grasp. Independentcompletefacettest needed;no repeatofcompleteddiagonalcells.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
