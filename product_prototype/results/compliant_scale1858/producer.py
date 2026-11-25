"""Necessary scale check, never turn micro-load Native result into grasp capacity."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 paths=[BASE/'results/dorsal_compression1847/summary.json',BASE/'results/root_torsion1853/summary.json',BASE/'results/compliant_rotor1855/summary.json']
 wrench,torsion,static=[json.loads(f.read_text()) for f in paths];c=torsion['configuration'];L=c['length_m'];r=c['radius_m'];G=c['G_Pa'];theta=c['target_angle_rad'];k=G*c['J_m4']/L
 moments=np.array([abs(row['closing_axis_moment_Nm']) for row in wrench['records']]);assert np.allclose(moments,.009,rtol=1e-12,atol=0)
 M=float(moments.max());required_r=(2*M*L/(np.pi*G*theta))**.25
 assert abs(k*theta-c['applied_moment_Nm'])<=1e-18
 # Independent constitutive identities only; not a simulation of giant strain.
 records=[]
 for label,radius in [('coupon_radius',r),('radius_matching_reference_moment_at_target_angle',required_r)]:
  J=np.pi*radius**4/2;stiffness=G*J/L;linear_theta=M/stiffness;gamma=radius*linear_theta/L
  records.append(dict(design=label,radius_mm=radius*1000,stiffness_Nm_per_rad=stiffness,linear_constitutive_reference_angle_rad=linear_theta,reference_outer_shear_strain=gamma,linear_reference_shear_stress_Pa=G*gamma,shaft_volume_mm3=np.pi*radius**2*L*1e9,actual_allowable_shear_strain=None,actual_allowable_stress_Pa=None))
 d=dict(status='BLOCKED_FULL_LOAD_MATERIAL_AND_OUTPUT_INTERFACE_NOT_QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),inputs={str(f.relative_to(BASE)):sha(f) for f in paths},reference_moment_Nm=M,reference_tension_N_per_cable=1.5,load_reference='Actual REST paired-cable closing wrench from1847; not minimum motor demand and not torque necessarily applied to pivot in a loaded transmission',target_angle_rad=theta,coupon_operating_moment_Nm=c['applied_moment_Nm'],moment_to_coupon_operating_moment_ratio=M/c['applied_moment_Nm'],records=records,compound_coupon=dict(input_dead_load_N=static['reference']['input_dead_load_N'],opposing_output_dead_load_N=static['reference']['output_resisting_dead_load_N'],ratio_1p5N_to_input=1.5/static['reference']['input_dead_load_N']),scope='Necessary independent SI scale illustration, no Native rerun or physical allowable assumption. Reference torque is a load scale, not a validated replacement architecture requirement. At large strain linear constitutive extrapolation is NOT a credible prediction; it forbids promotion of0.25mm shaft to full-load capability. Enlarged radius is not selected hardware: strain, fatigue, bond, compound bending, actual torque balance and supported compression path unqualified. No100g Holding PASS.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
