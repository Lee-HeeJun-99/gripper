"""CAD-derived ideal root pulley loads and blank physical measurements,not strength approval."""
import argparse,csv,json,math,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,sha

def root_load(record,tension):
 route=np.array(record['route_mm'],dtype=float);centre=np.array(record['centre_mm'],dtype=float)
 if tension<0 or len(route)<4 or not np.isfinite(route).all() or not np.isfinite(centre).all():raise ValueError('finite route and nonnegative tension required')
 if min(np.linalg.norm(route[0]-route[1]),np.linalg.norm(route[-1]-route[-2]))==0:raise ValueError('undefined branch direction')
 u=(route[0]-route[1]);u/=np.linalg.norm(u)
 v=(route[-1]-route[-2]);v/=np.linalg.norm(v)
 force=tension*(u+v)
 moment=np.cross((route[1]-centre)*.001,tension*u)+np.cross((route[-2]-centre)*.001,tension*v)
 expected=2*tension*math.sin(math.radians(record['turn_angle_deg'])/2)
 return dict(part=record['part'],centre_mm=centre.tolist(),branch_unit_vectors=[u.tolist(),v.tolist()],force_N=force.tolist(),force_norm_N=float(np.linalg.norm(force)),angle_reference_force_N=expected,force_reference_error_N=float(abs(np.linalg.norm(force)-expected)),ideal_spin_moment_Nm=moment.tolist(),ideal_moment_norm_Nm=float(np.linalg.norm(moment)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 source=BASE/'results/product_root_fork780/summary.json';data=json.loads(source.read_text());records=[root_load(r,1.5) for r in data['records']]
 passed=len(records)==6 and max(r['force_reference_error_N'] for r in records)<1e-12 and max(r['ideal_moment_norm_Nm'] for r in records)<1e-12
 # A geometric load screen only:ideal pin with central transverse force and two simple supports.
 force=max(r['force_norm_N'] for r in records);d=.001;span=.0028;area=math.pi*d*d/4
 screen=dict(ASSUMED_pin_diameter_m=d,ASSUMED_support_span_m=span,ideal_double_shear_stress_Pa=force/(2*area),ideal_central_load_bending_stress_Pa=(force*span/4)/(math.pi*d**3/32),material_allowable_stress_Pa=None,actual_support_boundary_condition=None,safety_factor=None,actual_preload_N=None,actual_thread_pullout_N=None,scope='Ideal simply-supported pin central-load screen,NOT actual boss/fork load distribution or strength qualification.')
 fields=['part','tension_in_N','tension_out_N','axle_force_x_N','axle_force_y_N','axle_force_z_N','spin_torque_Nm','radial_deflection_m','axial_endplay_m','cycle_count','wire_diameter_m','wire_min_bend_radius_m','material_batch','instrument','calibration_reference','uncertainty','measured_at','status']
 with (out/'physical_measurements_TEMPLATE.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in records:w.writerow(dict(part=r['part'],status='NOT MEASURED'))
 result=dict(status='PASS_CAD_IDEAL_LOAD_REFERENCE_ONLY' if passed else 'FAIL_LOAD_REFERENCE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x.relative_to(BASE)):sha(x) for x in (Path(__file__),source)},tension_per_branch_N=1.5,records=records,pin_screen=screen,actual_measurements=None,scope='Reference CAD root route780 preserved;V39 root pulley centres/pitch unchanged. Frictionless equal branch tension is a research assumption,not motor sizing or measured tension. Route directions from actual CAD data,NOT dynamic force prediction. No measured modulus/friction/retention or component approval;whole actuation clearance and B3 physics Gates remain open.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
