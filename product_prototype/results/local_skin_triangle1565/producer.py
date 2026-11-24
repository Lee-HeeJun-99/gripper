"""Extract actual missed Skin facet into independent rigid triangle/sphere coupon."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_bending_coupon import guarded
def read(p):return list(csv.DictReader(p.open()))
def flat(a):return ' '.join(format(float(x),'.17g') for x in np.asarray(a).ravel())
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results/finite_hardware_normals1563';tree=ET.parse(source/'scene.scn').getroot();film=read(source/'finger0.csv');obj=read(source/'object.csv');k=next(k for k,r in enumerate(film) if float(r['time_s'])>=.0725);q=np.fromstring(film[k]['q_m'],sep=' ').reshape(-1,3);centre=np.fromstring(obj[k]['rigid_q'],sep=' ')[:3];node=tree.find("Node[@name='finger0']/Node[@name='skinCollision']");ids=np.fromstring(node.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);tri=q[ids][faces];near=trimesh.triangles.closest_point(tri,np.repeat(centre[None],len(tri),axis=0));which=int(np.linalg.norm(near-centre,axis=1).argmin());v=tri[which];origin=v.mean(0);normal=np.cross(v[1]-v[0],v[2]-v[0]);normal/=np.linalg.norm(normal);template=BASE/'results/b3_direct_rows514/1';records=[]
 for kind in ('Min','Local','LocalReversed'):
  d=out/kind;d.mkdir();root=ET.parse(template/'scene.scn').getroot()
  if kind!='Min':root.find('MinProximityIntersection').tag='LocalMinDistance'
  for i,position in enumerate((origin,centre)):
   n=root.find(f"Node[@name='guide{i}']");n.find('MechanicalObject').set('position',flat(np.r_[position,[0,0,0,1]]));n.find('MechanicalObject').set('velocity','0 0 0 0 0 0');col=n.find("Node[@name='collision']")
   if i==0:
    col.remove(col.find('SphereCollisionModel'));col.find('MechanicalObject').set('position',flat(v));ET.SubElement(col,'MeshTopology',position=flat(v),triangles='0 2 1' if kind=='LocalReversed' else '0 1 2')
    for model in ('Triangle','Line','Point'):ET.SubElement(col,model+'CollisionModel',group='1',**({'computeNormals':'1'} if model=='Point' else {}))
   else:col.find('MechanicalObject').set('position',flat(centre));col.find('SphereCollisionModel').set('radius','.03')
  for n in root.iter():
   for key,value in list(n.attrib.items()):n.set(key,value.replace(str(template),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',str(d/'scene.scn')],d/'process',60);response=read(d/'response0.csv') if (d/'response0.csv').exists() else [];logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));records.append(dict(variant=kind,process=process,error='[ERROR]'in logs,nonzero_actual_response_rows=sum(float(r['lambda_Ns'])!=0 for r in response),scene_sha256=sha(d/'scene.scn')))
 d=dict(status='ISOLATED_ACTUAL_TRIANGLE_CONTACT_CAPABILITY_ONLY',source_case=source.name,source_time_s=float(film[k]['time_s']),triangle_id=which,vertices_m=v.tolist(),normal_toward_sphere_dot=float(normal@(centre-origin)),actual_reference_triangle_sphere_gap_mm=float((np.linalg.norm(near[which]-centre)-.03)*1000),records=records,scope='Independenttwofreerigids withactualmissedSkinfacet andspherecentre asINITIALgeometry;NOFEM/cable/support/contacthistoryrestart. Deliberateinitialoverlap onlyforresponsecontract. Reversedfacet isdiagnostic,NOTwholeSkinfix orphysicalgraspvalidation.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(source/f) for f in ('scene.scn','finger0.csv','object.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
