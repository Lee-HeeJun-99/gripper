"""Exact conservative nominal bulk bounds; do not relabel failed CSG joint interfaces."""
import argparse,csv,json,sys
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());geometry=BASE/'results/bearing_geometry1873/summary.json';loads=BASE/'results/bearing_load1869/summary.json';native=BASE/'results/bearing_stroke1876/states.csv';g=json.loads(geometry.read_text());f=json.loads(loads.read_text())['reference']['initial_bearing_force_N'];c=g['configuration'];assert c['sleeve_outer_radius_mm']==1.5 and c['sleeve_inner_radius_mm']==.35 and c['radial_bore_radius_mm']==1.55 and c['return_shaft_radius_mm']==.25
 # cos(pi/32)>=1-(22/7/32)^2/2. Strict rational bound, no measured
 # distance epsilon, CSG cleanup, collision removal or tolerance adjustment.
 cosine_lower=1-(Q(22,7)/32)**2/2;shaft_to_sleeve=Q(350)*cosine_lower-250;sleeve_to_rotor=Q(1550)*cosine_lower-1500;shaft_to_rotor=Q(1550)*cosine_lower-250;assert min(shaft_to_sleeve,sleeve_to_rotor,shaft_to_rotor)>0
 ro=.0015;ri=.00035;I=np.pi*(ro**4-ri**4)/4;area=np.pi*(ro**2-ri**2);moment=f*.0018;torque=json.loads(loads.read_text())['reference']['return_torque_at_target_angle_Nm'];r=.00025
 maxomega=0.
 for row in csv.DictReader(native.open()):maxomega=max(maxomega,float(abs(np.fromstring(row['rigid_v'],sep=' ').reshape(-1,6)[:,3]).max()))
 d=dict(status='PASS_NOMINAL_BULK_BOUNDS_ONLY_JOINTS_UNQUALIFIED',configuration=c,lower_bounds_um=dict(return_shaft_to_hollow_sleeve=float(shaft_to_sleeve),sleeve_to_rotor_bore=float(sleeve_to_rotor),return_shaft_to_rotor_bore=float(shaft_to_rotor)),rational_bound=dict(cosine_lower=str(cosine_lower),shaft_to_sleeve_um=str(shaft_to_sleeve),sleeve_to_rotor_um=str(sleeve_to_rotor)),declared_joining_domains_mm=dict(root_socket_z=[-2.,-1.8],rotor_socket_z=[1.2,1.45],free_torsion_z=[-1.8,1.2]),nominal_stress_references=dict(hollow_axle_mean_shear_Pa=f/area,hollow_axle_root_bending_Pa=moment*ro/I,load_reference_N=f,assumed_force_plane_to_base_m=.0018,root_bond_mean_torsion_shear_Pa=torque/(2*np.pi*r*r*.0002),rotor_bond_mean_torsion_shear_Pa=torque/(2*np.pi*r*r*.00025)),actual_material_allowable_Pa=None,actual_bond_strength_Pa=None,actual_bearing_reaction_N=None,maximum_actual_controlled_rotor_speed_rad_s=maxomega,source_sha256=sha(Path(__file__)),inputs_sha256={str(p):sha(p) for p in (geometry,loads,native)},scope='Analytic separation for DECLARED nominal ideal circular/coplanar constructions outside named socket joints, all twist angles; conservative32facet inradius also bounded using rational pi<22/7. No CSG rerun or assertion that emitted STL topology/meshes satisfy every analytic boundary.1871/1872FAIL and1873REJECT remain. Exact-fit socket joining surfaces are NOT free-clearance regions; finite CSG artifacts there remain unresolved, not discarded by a volume floor. Stress references omit local concentration, contact stiffness, tolerances, fatigue and bond manufacture.50um bearing gap still smaller than200um inherited contact budget. No ideal-to-real bearing qualification, output/Finger routing or100g PASS.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
