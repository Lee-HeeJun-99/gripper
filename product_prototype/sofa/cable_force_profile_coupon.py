"""Independent calibrated native C2 force input/controller state regression."""
import argparse,json,csv,sys,hashlib,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent;sys.path.insert(0,str(ROOT/'tools'))
from film_guarded_process import guarded
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--controller-case',required=True);p.add_argument('--dt',type=float,choices=(.0025,.00125),default=.0025);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((BASE/'results'/a.controller_case/'summary.json').read_text());binary=ROOT/meta['build']/'libReGripProductSequence.so'
 if sha(binary)!=meta['binary_sha256'] or sha(BASE/'sofa/Controller.cpp')!=meta['source_hashes']['Controller.cpp']:raise ValueError('exact compiled input controller required')
 root=ET.parse(BASE/'results/native_force_units330/scene.scn').getroot();root.set('dt',str(a.dt))
 for e in root.iter():
  if 'filename' in e.attrib:e.set('filename',str(out/Path(e.get('filename')).name))
  if e.tag=='RequiredPlugin' and 'ReGripProductSequence' in e.get('pluginName',''):e.set('pluginName',str(binary))
 node=root.find("./Node[@name='coupon']");ET.SubElement(node,'NativeCableSequence',dict(body='@dofs',cable0='@cable0/actuator',cable1='@cable1/actuator',maximumForceN='1',filename=str(out/'control.csv')));ET.ElementTree(root).write(out/'scene.scn');steps=round(1/a.dt);r=dict(status='FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),scene_sha256=sha(out/'scene.scn'),scope='C2 native input N->Ns and linear discrete BE reference;NOT continuum convergence/contact/finger physics',dt_s=a.dt,maximum_force_N=1.,sdk='/home/ubuntu/SOFA/v26.06.00');(out/'producer.py').write_bytes(Path(__file__).read_bytes());r['process']=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);r['sofa_errors']=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'))
 if r['process']['exit_code']==0 and not r['sofa_errors']:
  controls=read(out/'control.csv');states=read(out/'states.csv');impulses=read(out/'constraints.csv');z=v=state_error=input_error=lambda_error=0.
  for c,s,l in zip(controls,states,impulses):
   t=float(c['time_s']);u=min(1.,max(0.,t/.5));T=u**3*(10+u*(-15+6*u));input_error=max(input_error,abs(float(c['command_N'])-T),abs(float(c['command_Ns'])-T*a.dt));lambda_error=max(lambda_error,float(abs(np.fromstring(l['impulses_Ns'],sep=' ')-T*a.dt).max()));v=(.001*v+a.dt*(T-1000*z))/(.001+a.dt*a.dt*1000);z+=a.dt*v;q=np.fromstring(s['q'],sep=' ').reshape(-1,3);speed=np.fromstring(s['v'],sep=' ').reshape(-1,3);state_error=max(state_error,float(abs(q[:,2]-z).max()),float(abs(speed[:,2]-v).max()))
  r.update(status='PASS_INPUT_CONTROLLER_ONLY' if len(states)==steps and max(state_error,input_error,lambda_error)<=1e-12 else 'FAIL',rows=len(states),command_error_N_Ns=input_error,BE_state_error=state_error,multiplier_error_Ns=lambda_error,gate=1e-12,raw_hashes={f.name:sha(f) for f in out.glob('*.csv')})
 (out/'summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
if __name__=='__main__':main()
