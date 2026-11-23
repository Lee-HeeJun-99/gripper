"""Elementary support-stiffness sensitivity,NOT assembled frame FE or material selection."""
import argparse,json,math,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/product_pulley_budget757/summary.json';prior=json.loads(src.read_text());load=next(r['conditional_turn_load_N'] for r in prior['records'] if r['tension_N']==1.5 and r['load_factor']==1.);length=50.;diameter=4.;inertia=math.pi*diameter**4/64;records=[]
 for modulus in (250.,2000.,200000.):
  displacement=load*length**3/(3*modulus*inertia);records.append(dict(ASSUMED_modulus_MPa=modulus,ideal_EB_tip_deflection_mm=displacement,deflection_divided_by_length=displacement/length,ideal_root_bending_stress_MPa=load*length/(math.pi*diameter**3/32)))
 result=dict(status='IDEALIZED_STIFFNESS_SENSITIVITY_NOT_FRAME_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),load_budget_sha256=sha(src),conditional_load_N=load,benchmark_length_mm=length,benchmark_diameter_mm=diameter,records=records,actual_material_modulus_MPa=None,actual_frame_displacement_mm=None,scope='Single50mmcantilever/D4 Euler-Bernoulli idealization,NOT branched bridgegeometry/load balance. Eexamples are numerical hypotheses,NOT selectedmaterials. Large delta/L invalidates small-deflection interpretation;do not report it as actual frame deflection. Shows why CAD intersection/service success cannot approve load-bearing stiffness,fatigue or Holding.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
