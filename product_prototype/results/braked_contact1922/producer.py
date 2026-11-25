"""One independently scheduled passive actuator-loss assumption on100g scene."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from brake_schedule_common import attach
from common_winch_assessment import assess

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--full',action='store_true');p.add_argument('--prefix');a=p.parse_args();src=BASE/'results/crimp_hold1904';assert json.loads((BASE/'results/brake_schedule1920/summary.json').read_text())['status']=='PASS_PUBLIC_BRAKE_DATA_NATIVE_OPERATOR_ONLY';assert json.loads((BASE/'results/brake_switched_finger1921/summary.json').read_text())['status']=='PASS_LOCAL_BRAKE_SINGLE_CLOSING_ONLY';old=json.loads((src/'summary.json').read_text());duration=2. if a.full else .6;estimate=old['process']['runtime_s']*.6/2*1.3
 if a.full:
  assert a.prefix;prior=json.loads((BASE/'results'/a.prefix/'summary.json').read_text());assert prior['status']=='VALID_UNBRACED_BRAKED_CONTACT_PREFIX_ONLY';unbraked=json.loads((BASE/'results/crimp_contact1898/summary.json').read_text());estimate=(old['process']['runtime_s']+max(0,prior['process']['runtime_s']-unbraked['process']['runtime_s']))*1.3;assert estimate<420
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());root=ET.parse(src/'scene.scn').getroot()
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 c=json.loads((BASE/'results/winch_brake1916/preflight.json').read_text())['coefficient_Nms_per_rad'];schedule=attach(root,out,[f'drive_{i}_{j}' for i in range(3) for j in range(2)],c)
 for name in ['config.json','mesh.json','holding_protocol.json']:(out/name).write_bytes((src/name).read_bytes())
 dt=float(root.get('dt'));steps=round(duration/dt);ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),base_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),schedule=schedule,holding_protocol_sha256=sha(out/'holding_protocol.json'),duration_s=duration,steps=steps,dt_s=dt,forecast_s=estimate,forecast_basis='Actual unbraked full259.34s plus any measured newprefix overhead;1.3margin. Forecast not guarantee; child420s/4GiB hard limit.',changed_variable='Only nonnegative local stock rotor viscous loss scheduled0 before.5s,quintic to.6s,then fixed. All geometry,mass,FEM,contact,damping elsewhere,input1.5Ncap,original protocol unchanged. No q/v or solver edits.',binary_sha256={e.get('pluginName'):sha(Path(e.get('pluginName'))) for e in root.iter('RequiredPlugin') if e.get('pluginName','').startswith('/')});(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',out/'scene.scn'],out/'process',420);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ['stdout.log','stderr.log']);metrics={};valid=False;unbraced=False;brakes=[]
 if process['exit_code']==0 and '[ERROR]'not in logs:
  metrics,valid,unbraced=assess(root,out,steps)
  for i in range(3):
   for j in range(2):
    name=f'drive_{i}_{j}';drive=root.find(f"Node[@name='{name}']");frame=np.fromstring(drive.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)[2,:3];point=np.fromstring(drive.find("Node[@name='ports']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)[0];radius=np.linalg.norm((point-frame)[1:]);read=lambda f:list(csv.DictReader((out/f).open()));phases=[r for r in read(name+'_phases.csv') if r['phase']=='accepted_end'];coefs=read(name+'_brake_schedule.csv');assert len(phases)==len(coefs)==steps;torque=[]
    for r,cr in zip(phases,coefs):
     coeff=float(cr['coefficient']);speed=np.linalg.norm(np.fromstring(r['v'],sep=' ').reshape(-1,3)[0]);torque.append(coeff*speed/radius)
    brakes.append(dict(finger=i,tendon=j,maximum_reconstructed_passive_brake_torque_Nm=float(max(torque)),reference_torque_budget_Nm=.015))
  valid=valid and all(r['maximum_reconstructed_passive_brake_torque_Nm']<=.015+1e-12 for r in brakes)
 d=dict(status=('RUN_COMPLETED_NOT_QUALIFIED' if a.full else 'VALID_UNBRACED_BRAKED_CONTACT_PREFIX_ONLY') if valid and (a.full or unbraced) else 'FAIL_BRAKED_CRIMP_NATIVE_OR_TORQUE_BUDGET',process=process,metrics=metrics,brake_budget=brakes,dt_s=dt,gravity_m_s2=np.fromstring(root.get('gravity'),sep=' ').tolist(),holding_protocol_sha256=sha(out/'holding_protocol.json'),source_sha256=sha(Path(__file__)),preflight_sha256=sha(out/'preflight.json'),scope='Scheduled local actuator-loss assumption, NOT measured motor/brake/electrical data. Native stock implicit FF, ideal coaxial bearing, unchanged actual material/hardware assumptions. No damping scan or tension increase. Prefix is not Holding; completed fullrun requires original independent Holding/no-bracing/FEM/force/clearance assessment. No numerical/hardware certification.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='metrics'},indent=2))
if __name__=='__main__':main()
