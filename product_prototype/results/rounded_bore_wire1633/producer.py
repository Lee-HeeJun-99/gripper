"""Single manufactured inner-entry fillet candidate;all collision features retained."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_bending_coupon import guarded
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def geometry(n=32,arc=4):
 R=.2;left=np.array([[-.8+R*np.cos(t),.8+R*np.sin(t)] for t in np.linspace(-np.pi,-np.pi/2,arc+1)]);right=np.array([[.8+R*np.cos(t),.8+R*np.sin(t)] for t in np.linspace(-np.pi/2,0,arc+1)]);inner=np.vstack([left,right]);profile=np.vstack([[[-1,1.5],[1,1.5]],inner[::-1]]);v=np.array([[x,r*np.cos(t),r*np.sin(t)] for x,r in profile for t in np.arange(n)*2*np.pi/n]);faces=[]
 for k in range(len(profile)):
  l=(k+1)%len(profile)
  for j in range(n):a=k*n+j;b=k*n+(j+1)%n;c=l*n+(j+1)%n;d=l*n+j;faces.extend(((a,b,c),(a,c,d)))
 m=trimesh.Trimesh(v,faces,process=False);m.fix_normals();assert m.is_watertight and m.is_winding_consistent and m.volume>0;return m,inner
def inside(points,inner,n=32):
 p=np.asarray(points);angle=(np.arange(n)+.5)*2*np.pi/n;norm=np.column_stack([np.cos(angle),np.sin(angle)]);s=(p[:,1:]@norm.T).max(1);r=np.interp(p[:,0],inner[:,0],inner[:,1]);return (abs(p[:,0])<1)&(s<1.5*np.cos(np.pi/n))&(s>r*np.cos(np.pi/n))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/wire_contact_policy1616';root=ET.parse(src/'scene.scn').getroot();m,inner=geometry();node=root.find("Node[@name='finiteEyelet']");v=m.vertices*.001+[.01,0,0];node.find('MechanicalObject').set('position',flat(v));node.find('MeshTopology').set('position',flat(v));node.find('MeshTopology').set('triangles',flat(m.faces));assert {x.tag for x in node if x.tag.endswith('CollisionModel')}=={'TriangleCollisionModel','LineCollisionModel','PointCollisionModel'}
 for n in root.iter():
  for k,vv in list(n.attrib.items()):n.set(k,vv.replace(str(src),str(out)))
 m.export(out/'rounded_bore_mm.stl');geom=dict(outer_diameter_mm=3,central_bore_diameter_mm=1.2,overall_length_mm=2,straight_bore_length_mm=1.6,inner_entry_fillet_radius_mm=.2,entry_bore_diameter_mm=1.6,segments=32,arc_segments=4,arc_chord_error_mm=float(.2*(1-np.cos(np.pi/16))),volume_mm3=float(m.volume),minimum_end_radial_wall_mm=.7,inner_profile_mm=inner.tolist(),watertight=True,winding_consistent=True);(out/'geometry.json').write_text(json.dumps(geom,indent=2));ET.ElementTree(root).write(out/'scene.scn');(out/'preflight.json').write_text(json.dumps(dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),geometry=geom,hypothesis='Actual1630sharpinner-rim LineLine reactions opposepenetratingvertex TrianglePoint rows. Replace ONLYinner90degreeentries withfiniteR.2fillets;keepALLline/triangle/pointcollisions,outerbody/corebore/material/BC/Minpolicy/dt/force/tolerances.',physical_scope='FixedGuidecoupon,newshapeNOTcalibratedwholehardware;not Guide-Guide outerchamfer1594 repeat. E/rho/friction researchassumptions. No300partCAD/grasp qualification.',forecast_s=310,forecast_basis='ActualMin77s/256Guidefaces;new768faces+roundednormals mayaltercost;420s hardlimit',child_limit_s=420,memory_GiB=4),indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1200','--hideProgressBar',str(out/'scene.scn')],out/'process',420);rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else [];logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));d=dict(status='NATIVE_ROUNDED_ENTRY_COUPON_COMPLETED_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==1200 else 'FAIL_NATIVE_ROUNDED_ENTRY_COUPON',process=proc,outputs=len(rows),source_sha256=sha(Path(__file__)),physical_validation='NOT QUALIFIED',scope='Allfiniteparts/featuresretained;independent actualvertex-solid penetration/provenance check required. STEP/fabrication/material/holding notvalidated.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
