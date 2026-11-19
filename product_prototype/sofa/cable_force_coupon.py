"""Stock CableConstraint force-input units vs analytic linear BE reference.
This is an independent input calibration,NOT new finger dynamics or a solver fix.
"""
import argparse,csv,json,hashlib,sys,xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent;sys.path.insert(0,str(ROOT/'tools'))
from film_guarded_process import guarded
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--dt',type=float,choices=(.0025,.00125),default=.0025);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/coupon_control323';tree=ET.parse(src/'scene.scn');root=tree.getroot();root.set('dt',str(a.dt));node=root.find("./Node[@name='coupon']");node.remove(node.find('NativeCableSequence'));mass=.001;stiffness=1000.;force=1.;steps=round(1/a.dt)
 for cable in node.findall('Node'):
  actuator=cable.find('CableConstraint');actuator.set('valueType','force');actuator.set('value',format(force*a.dt,'.17g'))
 ET.SubElement(node,'NativePointJournal',dict(body='@dofs',filename=str(out/'states.csv')));ET.SubElement(root,'NativeConstraintJournal',dict(solver='@constraints',filename=str(out/'constraints.csv')));tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());r=dict(status='FAIL',scope='native force-input impulse scaling on two independent spring-mass points;NOT FEM,time-continuum/contact/grasp certification',source_commit=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),source_coupon_sha256=sha(src/'summary.json'),scene_sha256=sha(out/'scene.scn'),physical_force_per_cable_N=force,native_value_Ns=force*a.dt,mass_per_point_kg=mass,stiffness_N_m=stiffness,dt_s=a.dt,steps=steps,sdk='/home/ubuntu/SOFA/v26.06.00')
 binary=json.loads((src/'summary.json').read_text())['binary_sha256'];r['binary_sha256']=binary;r['process']=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);r['sofa_errors']=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'))
 if r['process']['exit_code']==0 and not r['sofa_errors']:
  rows=list(csv.DictReader((out/'states.csv').open()));z=0.;v=0.;err=0.
  for row in rows:
   v=(mass*v+a.dt*(force-stiffness*z))/(mass+a.dt*a.dt*stiffness);z+=a.dt*v;q=np.fromstring(row['q'],sep=' ').reshape(-1,3);speed=np.fromstring(row['v'],sep=' ').reshape(-1,3);err=max(err,float(abs(q[:,2]-z).max()),float(abs(speed[:,2]-v).max()))
  impulses=list(csv.DictReader((out/'constraints.csv').open()));lambda_error=max(float(abs(np.fromstring(row['impulses_Ns'],sep=' ')-force*a.dt).max()) for row in impulses);r.update(status='PASS_DISCRETE_FORCE_CALIBRATION_ONLY' if len(rows)==steps and max(err,lambda_error)<=1e-12 else 'FAIL',rows=len(rows),maximum_BE_reference_state_error=err,maximum_multiplier_error_Ns=lambda_error,final_displacement_mm=float(z*1000),gate=1e-12,raw_hashes={f.name:sha(f) for f in out.glob('*.csv')})
 (out/'summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
if __name__=='__main__':main()
