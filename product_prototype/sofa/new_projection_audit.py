"""Read-only installed New triangle/sphere projection reference,NOT a new solver."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
HEADER=Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Collision.Detection.Intersection/sofa/component/collision/detection/intersection/MeshNewProximityIntersection.inl')
def read(p):return list(csv.DictReader(p.open()))
def projection(tri,q):
 # Transcription of INSTALLED computeIntersection(Triangle,TSphere) barycentric
 # branch arithmetic only. Nativefeatureflags excluded and never claimedknown.
 AB=tri[:,1]-tri[:,0];AC=tri[:,2]-tri[:,0];AQ=q-tri[:,0];a=np.sum(AB*AB,axis=1);b=np.sum(AC*AC,axis=1);c=np.sum(AB*AC,axis=1);d=np.sum(AQ*AB,axis=1);e=np.sum(AQ*AC,axis=1);det=a*b-c*c;alpha=(d*b-e*c)/det;beta=(e*a-d*c)/det
 for i in range(len(tri)):
  if alpha[i]<.000001 or beta[i]<.000001 or alpha[i]+beta[i]>.999999:
   pAB=d[i]/a[i];pAC=e[i]/b[i]
   if pAB<.000001 and pAC<.0000001:alpha[i]=beta[i]=0
   elif pAB<.999999 and beta[i]<.000001:alpha[i]=pAB;beta[i]=0
   elif pAC<.999999 and alpha[i]<.000001:alpha[i]=0;beta[i]=pAC
   else:
    pBC=(e[i]-d[i]+a[i]-c[i])/(a[i]+b[i]-2*c[i])
    if pBC<.000001:alpha[i]=1;beta[i]=0
    elif pBC>.999999:alpha[i]=0;beta[i]=1
    else:alpha[i]=1-pBC;beta[i]=pBC
 return tri[:,0]+AB*alpha[:,None]+AC*beta[:,None],np.stack([1-alpha-beta,alpha,beta],axis=1)
def acute_faces(vertices,faces):
 tri=vertices[faces];angles=[]
 for i in range(3):
  a=tri[:,(i+1)%3]-tri[:,i];b=tri[:,(i+2)%3]-tri[:,i];angles.append(np.sum(a*b,axis=1)/(np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1)))
 start=np.argmax(np.array(angles),axis=0);return np.array([np.roll(f,-int(k)) for f,k in zip(faces,start)])
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/separated_rigid_sphere1570/New';root=ET.parse(src/'scene.scn').getroot();node=root.find("Node[@name='guide0']/Node[@name='collision']");v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);faces=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);q=np.fromstring(root.find("Node[@name='guide1']/MechanicalObject").get('position'),sep=' ')[:3];tri=v[faces];pred,bary=projection(tri,q);actual=trimesh.triangles.closest_point(tri,np.repeat(q[None],len(tri),axis=0));newfaces=acute_faces(v,faces);reordered,newbary=projection(v[newfaces],q);contacts=[];first=min(float(r['accepted_time_s']) for r in read(src/'detector.csv'))
 for r in read(src/'detector.csv'):
  if float(r['accepted_time_s'])!=first or '/Triangle'not in r['model0']:continue
  point=np.fromstring(r['detected_point0'],sep=' ');near=trimesh.triangles.closest_point(tri,np.repeat(point[None],len(tri),axis=0));error=np.linalg.norm(pred-point,axis=1);matches=np.flatnonzero(error<=1e-12);contacts.append(dict(pair_index=int(r['pair_index']),actual_Native_point_m=point.tolist(),minimum_point_distance_to_actual_surface_mm=float(np.linalg.norm(near-point,axis=1).min()*1000),matching_projection_candidate_triangles=matches.tolist(),candidate_barycentrics=bary[matches].tolist(),minimum_reconstruction_error_m=float(error.min()),native_point_sphere_gap_mm=float((np.linalg.norm(point-q)-.03)*1000)))
 d=dict(status='INSTALLED_PROJECTION_DIAGNOSTIC_ONLY',actual_contacts=contacts,minimum_reference_surface_sphere_gap_mm=float((np.linalg.norm(actual-q,axis=1).min()-.03)*1000),original_minimum_candidate_barycentric=float(bary.min()),original_maximum_projection_closestpoint_difference_mm=float(np.linalg.norm(pred-actual,axis=1).max()*1000),cyclic_minimum_candidate_barycentric=float(newbary.min()),cyclic_maximum_projection_closestpoint_difference_mm=float(np.linalg.norm(reordered-actual,axis=1).max()*1000),cyclic_unordered_triangle_sets_identical=bool(np.array_equal(np.sort(faces,axis=1),np.sort(newfaces,axis=1))),cyclic_normals_preserved_error=float(abs(np.cross(v[newfaces[:,1]]-v[newfaces[:,0]],v[newfaces[:,2]]-v[newfaces[:,0]])-np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])).max()),scope='Installedbranchmathreferenceonly,noSDKchanges/nativefeatureflagsassumed/noODEreplacement. Actualdetectionpointdistanceindependentfrombranchreconstruction. Multiplematchingfacetsareambiguous,notuniquelyassigned. Cyclicpermutation preservesphysicaltriangles/normals butmustbefreshNativevalidated,notafixclaim.',header_sha256=sha(HEADER),source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','detector.csv','response1.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='actual_contacts'},indent=2))
if __name__=='__main__':main()
