"""Conditional energy/actuation scale from actual50ms;NOT a lifting test."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--hypothetical-height-mm',type=float,default=1.);a=p.parse_args()
 if not 0<a.hypothetical_height_mm<=100:raise ValueError('positive hypothetical height required')
 src=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';m=json.loads((src/'summary.json').read_text());cp=src/'three.checkpoint_250.txt'
 if m['status']!='PASS' or sha(cp)!=m['raw_hashes'][cp.name] or sha(src/'scene.scn')!=m['scene_sha256']:raise ValueError('qualified actual endpoint required')
 fields=[]
 for f in range(3):
  path=src/f'film_{f}.csv'
  if sha(path)!=m['raw_hashes'][path.name]:raise ValueError('actual energy changed')
  fields.append(list(csv.DictReader(path.open()))[-1])
 scene=ET.parse(src/'scene.scn').getroot();ff=list(scene.iter('FilmLateralTendon'))
 if len(ff)!=3 or scene.get('gravity')!='0 0 0' or any(float(f['T_per_rail'])!=0 for f in fields):raise ValueError('actual zero-tension/zero-gravity endpoint required')
 tokens=cp.read_text().split();v=np.array(tokens[5+1953:5+2*1953],float);offset=5+2*1953+4+693;bodyM=np.array(tokens[offset:offset+36],float).reshape(6,6)
 if np.any(bodyM-np.diag(np.diag(bodyM))) or not all(bodyM[i,i]==bodyM[0,0] for i in range(3)):raise ValueError('actual isotropic translational public mass required')
 filmE=math.fsum(float(f[k]) for f in fields for k in ('U_shell','U_attachment','K'));bodyE=float(.5*v[-6:]@bodyM@v[-6:]);weight=float(bodyM[0,0]*9810.);required=weight*a.hypothetical_height_mm;maximums=[float(f.get('maximumTension')) for f in ff];sumT=2*math.fsum(maximums)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='EXPERIMENTAL',scope='conditional necessary energy/actuation scale ONLY;NOT SOFA gravity/holding/lifting/capacity certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),checkpoint_sha256=sha(cp),actual_time_s=float(tokens[1]),actual_gravity='0 0 0',hypothetical_gravity_mm_s2=9810.,hypothetical_height_mm=a.hypothetical_height_mm,public_translational_mass_Ns2_per_mm=float(bodyM[0,0]),mass_kg=float(bodyM[0,0]*1000),hypothetical_weight_N=weight,measured_film_stored_plus_K_Nmm=filmE,measured_rigid_K_Nmm=bodyE,conditional_snapshot_energy_Nmm=filmE+bodyE,necessary_potential_energy_Nmm=required,conditional_height_if_all_snapshot_energy_convertible_mm=(filmE+bodyE)/weight,necessary_mean_positive_shortening_per_rail_mm=required/sumT,maximum_prescribed_tension_per_rail_N=maximums,rails=6,assumptions=['Hypothetical gravity is NOT applied to the actual experiment','Snapshot inventory must be complete;root work/whole energy gate still unqualified','Perfect mechanical conversion,no losses,no additional energy input for conditional height','Stroke lower bound assumes tension never exceeds recorded research maximum;not actual actuator specifications'],root_work=None,holding_load=None,lift_result='NOT RUN',actuator_stroke='UNKNOWN;do not infer actual mechanism feasibility from this conditional bound');write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
