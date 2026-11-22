"""Actual saved drum geometry and conditional winding budget, not motor selection."""
import argparse,json,math,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def winding(barrel_radius,wire_diameter,stroke,tension,wires=2):
 if not all(math.isfinite(v) and v>0 for v in (barrel_radius,wire_diameter,stroke,tension,wires)):raise ValueError('positive finite inputs required')
 r=barrel_radius+wire_diameter/2
 return dict(effective_radius_mm=r,angle_rad=stroke/r,turns=stroke/r/(2*math.pi),ideal_torque_Nm=wires*tension*r/1000,ideal_work_J=wires*tension*stroke/1000)

def inspect(shape):
 if shape['op']!='transform':raise ValueError('declared drum frame required')
 s=shape['shape']
 if s['op']!='difference' or len(s['items'])!=2:raise ValueError('unsupported drum topology')
 positive,bore=s['items']
 if positive['op']!='union' or len(positive['items'])!=4 or bore['op']!='cylinder':raise ValueError('unsupported channel topology')
 barrel,*flanges=positive['items']
 if any(x['op']!='cylinder' or x['xy']!=barrel['xy'] for x in [barrel,*flanges,bore]):raise ValueError('nonconcentric drum')
 z=sorted(x['z'] for x in flanges);gaps=[z[i+1][0]-z[i][1] for i in range(2)]
 if min(gaps)<=0:raise ValueError('closed winding channel')
 return dict(barrel_radius_mm=barrel['radius'],flange_radius_mm=[x['radius'] for x in flanges],channel_free_axial_width_mm=gaps,shaft_bore_D_mm=2*bore['radius'],frame=shape['matrix'])

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/product_remaining_lead953/full_assembly_recipe.json';parts=json.loads(src.read_text())['parts'];drums=[p for p in parts if p['group']=='drum'];records=[]
 for p0 in drums:
  dims=inspect(p0['shape']);records.append(dict(part=p0['name'],geometry=dims,conditional_scenarios=[dict(ASSUMED_wire_diameter_mm=d,ASSUMED_stroke_mm=s,ASSUMED_tension_N=1.5,**winding(dims['barrel_radius_mm'],d,s,1.5)) for d in (.45,.5) for s in (3.,8.)]))
 result=dict(status='DRUM_GEOMETRY_AND_IDEAL_BUDGET_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src)},records=records,actual_loaded_motor_torque_Nm=None,actual_wire_slip=None,actual_required_stroke_mm=None,motor_selected=None,fabrication_ready=False,scope='Read actual saved concentric CSG cylinders;not newly manufactured or measured. Plain two-channel drum has NO modeled helical groove/anchor/horn coupling. Same shaft angle gives equal ideal takeup only if effective radii equal and no slip;NOT mechanical equalizer. Each scenario is independent assumed stroke/tension,not qualified B3 motor requirement. No layer buildup,wire compliance,bearing/cable friction,efficiency,holding torque,termination,fatigue,or motor thermal qualification. Three drums NOT six independent actuators.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],drums=len(records),geometry=records[0]['geometry']),indent=2))
if __name__=='__main__':main()
