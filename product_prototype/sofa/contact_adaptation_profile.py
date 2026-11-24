"""One nonuniform manufactured-curvature candidate,initial Skin/FEM gate only.

Keeps70–100mm span,total40deg androot14deg;redistributes curvature linearly
from2*mean at70mm tozeroat100mm. NOT prescribed dynamic wrapping.
"""
import argparse,json,math,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.integrate import quad
import trimesh
from analyse import BASE,sha
from mechanism_candidates import world,stl
def candidate(c,p,angle):
 x,y,z=p;start=70.;L=30.;total=math.radians(40.)
 if x>start:
  u=(x-start)/L;phi=total*(2*u-u*u);X=start+L*quad(lambda t:math.cos(total*(2*t-t*t)),0,u,epsabs=1e-12)[0];Z=L*quad(lambda t:math.sin(total*(2*t-t*t)),0,u,epsabs=1e-12)[0];x,z=X-z*math.sin(phi),Z+z*math.cos(phi)
 tilt=math.radians(c['palm']['root_angle_deg']);x,z=x*math.cos(tilt)-z*math.sin(tilt),x*math.sin(tilt)+z*math.cos(tilt);a=math.radians(angle);r=c['palm']['mount_radius']-z;return [r*math.cos(a)+y*math.sin(a),r*math.sin(a)-y*math.cos(a),-x]
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';c=json.loads((src/'config.json').read_text());m=json.loads((src/'mesh.json').read_text());root=ET.parse(src/'scene.scn').getroot();local=np.array(m['local_positions_mm']);tet=np.array(m['tetrahedra']);faces=np.array(m['triangles']);centre=np.array(c['simulation']['sphere_center_mm']);R=c['simulation']['sphere_radius_mm'];margin=c['simulation']['contact_distance_mm'];records=[]
 for i,angle in enumerate((0,120,240)):
  old=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)*1000;generated=np.array([world(c,p,angle) for p in local]);assert abs(old-generated).max()<1e-10;q=np.array([candidate(c,p,angle) for p in local]);near=trimesh.triangles.closest_point(q[faces],np.repeat(centre[None],len(faces),axis=0));gaps=np.linalg.norm(near-centre,axis=1)-R;k=int(np.argmin(gaps));weights=trimesh.triangles.points_to_barycentric(q[faces[k]][None],near[k][None])[0];det=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));old_det=np.linalg.det((old[tet[:,1:]]-old[tet[:,0,None]]).transpose(0,2,1));records.append(dict(finger=i,minimum_initial_surface_gap_mm=float(gaps[k]),nearest_material_mm=(weights@local[faces[k]]).tolist(),minimum_signed_tet_determinant_mm3=float(det.min()),reference_volume_ratio=float(det.sum()/old_det.sum()),initial_gate_pass=bool(gaps[k]>=margin and det.min()>0)));stl(out/f'candidate_reference_finger{i}.stl',q,faces);(out/f'candidate_q0_finger{i}_mm.json').write_text(json.dumps(q.tolist()))
 d=dict(status='PASS_INITIAL_SKIN_FEM_GATE_ONLY' if all(r['initial_gate_pass'] for r in records) else 'REJECT_INITIAL_SKIN_FEM_GATE',records=records,hypothesis='Advance inward tangent atmid-distal material beforeterminal byredistributing same40deg over same70–100mm,not increasing totalangle/startlength/force',reference_assumption='New manufactured stress-free material;not observed actuation',curvature_law='phi(u)=40deg*(2u-u^2),kappa=2*(40deg/30mm)*(1-u)',unchanged='100mmlength,24to12width,skin.1/rail.5mm,root14deg/radius50/layout120',guide_mapping_and_hardware_transform='NOT IMPLEMENTED_BEFORE_SKIN_GATE',wire_guide_clearance='NOT MEASURED',Native_grasp='NOT RUN',scope='Initial physicalsurface triangles/sphere andFEM signedvolumes. No stress/strainorNativegrasp,dynamicclearance,sharedCADassembly,100gHoldingorWrappinglevelPASS. Existingmodeluntouched.',physical_validation='NOT QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','mesh.json','config.json')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
