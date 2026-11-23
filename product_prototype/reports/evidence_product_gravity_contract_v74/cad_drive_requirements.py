"""Conditional actuator budget + read-only existing actual SOFA stroke audit.

Catalog stall torque/no-load speed are NOT continuous simultaneous performance.
No motor is approved by this calculation. No old physics is rerun or modified.
"""
import argparse,csv,itertools,json,math,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from manufacturing_assembly import load_design
from generate import world,width,guide_outboard,guide_normal

def requirement(tension,stroke_mm,radius_mm,time_s,efficiency,load_factor,wires=2):
 if min(tension,stroke_mm,radius_mm,time_s,efficiency,load_factor)<=0 or efficiency>1:raise ValueError('invalid conditional drive inputs')
 theta=stroke_mm/radius_mm
 return dict(tension_N_per_wire=tension,stroke_mm=stroke_mm,effective_radius_mm=radius_mm,closing_time_s=time_s,assumed_efficiency=efficiency,load_factor=load_factor,wires_per_channel=wires,
             channel_nominal_output_torque_Nm=wires*tension*radius_mm/1000,
             conditional_design_torque_Nm=load_factor*wires*tension*radius_mm/1000/efficiency,
             drum_angle_rad=theta,drum_turns=theta/(2*math.pi),drum_speed_rpm=theta/time_s*60/(2*math.pi),
             cable_work_constant_tension_J=wires*tension*stroke_mm/1000,
             conditional_input_work_J=wires*tension*stroke_mm/1000/efficiency,
             minimum_additional_gear_ratio=None)

def actual_stroke():
 src=BASE/'results/precurve40_force_three344';cfg=json.loads((src/'config.json').read_text());root=ET.parse(src/'scene.scn').getroot();motion=json.loads((src/'motion_commands.json').read_text())
 if any(c['node']!='floor' for c in motion['commands']):raise ValueError('cannot assume stationary pullpoint with moving root')
 records=[];hashes={str((src/name).relative_to(BASE.parent)):sha(src/name) for name in ('config.json','scene.scn','summary.json','motion_commands.json')}
 for finger,angle in enumerate(cfg['palm']['angles_deg']):
  path=src/f'finger{finger}.csv';hashes[str(path.relative_to(BASE.parent))]=sha(path)
  with path.open() as stream:rows=list(csv.DictReader(stream))
  for cable,side in enumerate((-1,1)):
   actuator=list(root.find(f"Node[@name='guides{finger}']").iter('CableConstraint'))[cable];pull=np.fromstring(actuator.get('pullPoint'),sep=' ')
   initial=np.asarray([world(cfg,[x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)],angle) for x in cfg['tendon']['guide_stations']])*.001
   length0=float(np.linalg.norm(np.diff(np.vstack([pull,initial]),axis=0),axis=1).sum());values=[];last_time=0.;previous_shortening=0.;previous_force=0.;work=0.
   for row in rows:
    time=float(row['time_s']);h=time-last_time;points=np.fromstring(row[f'guide{cable}_q_m'],sep=' ').reshape(-1,3);length=float(np.linalg.norm(np.diff(np.vstack([pull,points]),axis=0),axis=1).sum());shortening=length0-length;force=float(row[f'cable{cable}_force_raw'])/h
    work+=(force+previous_force)/2*(shortening-previous_shortening)
    values.append(dict(time_s=time,geometric_length_m=length,geometric_shortening_mm=shortening*1000,Native_internal_displacement_mm=float(row[f'cable{cable}_displacement_m'])*1000,equivalent_cable_force_N=force))
    last_time,previous_shortening,previous_force=time,shortening,force
   records.append(dict(finger=finger,cable=cable,initial_geometric_length_mm=length0*1000,maximum_geometric_shortening_mm=max(x['geometric_shortening_mm'] for x in values),minimum_geometric_shortening_mm=min(x['geometric_shortening_mm'] for x in values),maximum_actual_equivalent_force_N=max(x['equivalent_cable_force_N'] for x in values),maximum_internal_vs_geometric_difference_mm=max(abs(x['Native_internal_displacement_mm']-x['geometric_shortening_mm']) for x in values),sampled_trapezoidal_cable_work_J_NOT_stage_work=work,frames=values))
 return records,hashes

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 design=load_design(BASE/'config/manufacturing_b3_v14_mount.json');drive=design['drive'];catalog_path=BASE/'config/procurement_candidates_v12.json';catalog=json.loads(catalog_path.read_text());records=[]
 for t,s,d,e in itertools.product(drive['tension_scenarios_N_per_wire'],drive['stroke_scenarios_mm'],drive['closing_time_scenarios_s'],drive['assumed_transmission_efficiencies']):records.append(requirement(t,s,drive['drum_effective_wire_radius_mm'],d,e,drive['design_load_factor']))
 observed,source_hashes=actual_stroke();source_hashes[str(catalog_path.relative_to(BASE.parent))]=sha(catalog_path)
 for row in records:
  row['motor_screening']=[dict(candidate=m['candidate'],conditional_torque_divided_by_CATALOG_STALL=row['conditional_design_torque_Nm']/m['stall_torque_Nm'],required_speed_divided_by_CATALOG_NO_LOAD=row['drum_speed_rpm']/m['no_load_speed_rpm'],continuous_operation_verdict='BLOCKED_NOT_MEASURED',stall_torque_is_not_continuous_rating=True) for m in catalog['motors']]
 with (out/'drive_scenarios.csv').open('w') as f:
  fields=[k for k in records[0] if k!='motor_screening'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows([{k:v for k,v in r.items() if k!='motor_screening'} for r in records])
 with (out/'procurement_BOM.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['assembly_item','quantity','candidate','catalog_source','measured_specimen_property','unit_cost_KRW','selection_status'])
  for m in catalog['materials']:w.writerow([m['part'],'TBD',m['candidate'],m['supplier_url'],'NOT MEASURED','NULL','COUPON_OR_QUOTE_REQUIRED'])
  for m in catalog['motors']:w.writerow(['alternative motor',3,m['candidate'],m['manual_url'],'continuous torque/speed NOT MEASURED','NULL','ALTERNATIVES_NOT_BOTH_PURCHASED'])
  for w0 in catalog['wires']:w.writerow(['alternative wire',6,w0['candidate'],w0['supplier_url'],'bend fatigue/stiffness/termination NOT MEASURED','NULL','DIAMETER_DIFFERS_FROM_B3_0.5mm'])
 curve_angle=math.radians(40);bend_R=30/curve_angle
 result=dict(status='CONDITIONAL_DRIVE_DESIGN_NOT_MOTOR_OR_GRASP_APPROVAL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),source_hashes=source_hashes,scenarios=records,actual_old_SOFA_stroke=observed,
             actual_source_scope='Existing344 functional run;time/mesh Gate FAIL,no physical hardware measurement. Geometric cable lengths recomputed from accepted mappedguide coordinates and stationary XMLpullpoint. Equivalentforce=Nativeimpulse/actualdt. Notstagework or motorstroke includingextra routing/friction.',
             geometry=dict(manufactured_distal_radius_mm=bend_R,geometric_flattening_strain_skin_outer_fibre=.1/(2*bend_R),geometric_flattening_strain_rail_outer_fibre=.5/(2*bend_R),scope='section-geometry strain only,no material stress/fatigue or residual-forming validation'),
             three_motor_CATALOG_stall_current_sum_A=sum(m['stall_current_A'] for m in [catalog['motors'][0]]*3),
             current_sum_scope='catalog screening only,NOT selected supply rating,fuse,thermal load or simultaneous continuous operating point',
             motor_selected=None,wire_selected=None,wire_measured_axial_stiffness_N_m=None,measured_required_stroke_mm=None,measured_continuous_torque_Nm=None)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'catalog.json').write_bytes(catalog_path.read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],scenarios=len(records),observed_simulated_stroke_range_mm=[min(r['maximum_geometric_shortening_mm'] for r in observed),max(r['maximum_geometric_shortening_mm'] for r in observed)],internal_vs_geometric_max_mm=max(r['maximum_internal_vs_geometric_difference_mm'] for r in observed)),indent=2))
if __name__=='__main__':main()
