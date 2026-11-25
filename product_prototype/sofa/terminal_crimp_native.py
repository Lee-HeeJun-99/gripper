"""Guarded new finite terminal anchor trial, original support protocol retained."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from common_winch_assessment import assess

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--full',action='store_true');p.add_argument('--prefix');p.add_argument('--duration',type=float,default=.6);p.add_argument('--runtime-contract');a=p.parse_args();duration=2. if a.full else a.duration;assert .6<=duration<=2.;design=BASE/'results/terminal_crimp1896';mass=BASE/'results/crimp_tensor1897';assert json.loads((design/'summary.json').read_text())['status']=='PASS_TERMINAL_CRIMP_NECESSARY_GEOMETRY_ONLY';assert json.loads((mass/'summary.json').read_text())['status']=='PASS_ACTUAL_YOKE_INITIAL_TENSOR_ASSEMBLY_ONLY'
 if duration>.6:
  assert a.prefix;previous=json.loads((BASE/'results'/a.prefix/'summary.json').read_text());assert previous['status']=='VALID_UNBRACED_OBJECT_CONTACT_PREFIX_ONLY';prior_duration=json.loads((BASE/'results'/a.prefix/'preflight.json').read_text())['duration_s'];forecast=previous['process']['runtime_s']*duration/prior_duration*1.3
  if a.runtime_contract:
   assert a.full and a.prefix=='crimp_withdrawal1899';budget=json.loads((BASE/'results'/a.runtime_contract/'summary.json').read_text());assert budget['status']=='PASS_BOUNDED_RUNTIME_ESTIMATE_ONLY' and budget['long_case']==a.prefix;assert budget['input_sha256']['results/'+a.prefix+'/summary.json']==sha(BASE/'results'/a.prefix/'summary.json');forecast=budget['full2s_with_margin_s']
  assert forecast<420,'Existing measured resource forecast exceeds limit'
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 root=ET.parse(design/'scene.scn').getroot()
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(design),str(out)))
 for name in ('mesh.json','config.json','holding_protocol.json'):(out/name).write_bytes((BASE/'results/parallel_contact1894'/name).read_bytes())
 dt=float(root.get('dt'));steps=round(duration/dt);ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),assessment_source_sha256=sha(BASE/'sofa/common_winch_assessment.py'),design_scene_sha256=sha(design/'scene.scn'),design_summary_sha256=sha(design/'summary.json'),mass_contract_sha256=sha(mass/'summary.json'),scene_sha256=sha(out/'scene.scn'),holding_protocol_sha256=sha(out/'holding_protocol.json'),duration_s=duration,steps=steps,dt_s=dt,binary_sha256={e.get('pluginName'):sha(Path(e.get('pluginName'))) for e in root.iter('RequiredPlugin') if e.get('pluginName','').startswith('/')},scope='New blind terminal fitting material/COM/tensor only vs1894; same actual Skin/Rail/control/force cap/dt/Support protocol/free100gR30object. Actual finite fitting bridge/bore, allCollisionfeatures retained. Ideal terminated wire/crimp bond/rigid support and research density assumptions, not hardware/finitewire/time/mesh qualification. No q/v imposed on object or post-corrected.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',out/'scene.scn'],out/'process',420);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));metrics={};valid=False;unbraced=False
 if process['exit_code']==0 and '[ERROR]'not in logs:metrics,valid,unbraced=assess(root,out,steps)
 d=dict(status=('RUN_COMPLETED_NOT_QUALIFIED' if a.full else 'VALID_UNBRACED_OBJECT_CONTACT_PREFIX_ONLY') if valid and (a.full or unbraced) else 'FAIL_TERMINAL_CRIMP_NATIVE',process=process,metrics=metrics,dt_s=dt,gravity_m_s2=np.fromstring(root.get('gravity'),sep=' ').tolist(),holding_protocol_sha256=pre['holding_protocol_sha256'],source_sha256=sha(Path(__file__)),preflight_sha256=sha(out/'preflight.json'),scope=pre['scope']+' Prefix NOT Holding; completed2s still needs original Holding and zero-bracing force assessment.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
