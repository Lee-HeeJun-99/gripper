"""Conditional analytical sizing requirements,not measured strength or FEM qualification."""
import argparse,json,math,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def budget(tension,turn_rad,pin_diameter,arm_thickness,arm_width,arm_length,span,load_factor):
 if min(tension,pin_diameter,arm_thickness,arm_width,arm_length,span,load_factor)<=0 or not 0<turn_rad<math.pi:raise ValueError('invalid explicit sizing assumptions')
 load=2*tension*math.sin(turn_rad/2)*load_factor
 return dict(tension_N=tension,turn_angle_deg=math.degrees(turn_rad),load_factor=load_factor,conditional_turn_load_N=load,double_shear_pin_average_MPa=load/(2*math.pi*pin_diameter**2/4),fork_bearing_average_MPa=load/(2*pin_diameter*arm_thickness),fork_arm_EB_root_stress_MPa=(load/2*arm_length)/(arm_width*arm_thickness**2/6),pin_simple_supported_center_load_bending_MPa=(load*span/4)/(math.pi*pin_diameter**3/32))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results/product_pulley_fork754/summary.json';module=json.loads(source.read_text());d=module['pin_diameter_mm'];records=[budget(T,math.pi/2,d,1.,3.,5.,2.8,SF) for T in (.5,1.5,3.) for SF in (1.,2.)]
 result=dict(status='CONDITIONAL_LOAD_REQUIREMENTS_NOT_STRENGTH_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),module_sha256=sha(source),records=records,measured_turn_load_N=None,material_allowable_stress_MPa=None,measured_fatigue_cycles=None,approved_material=None,scope='Equal static tension on both branches,90degree turn,massless frictionless wire ASSUMPTIONS. Fork two arms share load equally,5mmcantilever,3x1mmsection;pin simply supported2.8mmspan centralpointload. These are independent elementary idealizations,NOT actual FEM/fillet-stress,joint stiffness,bearing friction,impact,axle retention or stress-concentration proof. MPa=N/mm2;loadfactor is explicit design scenario,not physical input change.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps([r for r in records if r['tension_N']==1.5],indent=2))
if __name__=='__main__':main()
