"""Native linear FEM first-mode load diagnostic; no Guide/Cable/contact.
Altered spatial force is declared, not a successful grasp or old time repair.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import eigh
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--half',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_linear_gravity_ode1166';tree=ET.parse(src/'scene.scn');root=tree.getroot();node=root.find('Node');q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ');N=len(q0);free=np.ones(N,bool)
    for i in np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int):free[3*i:3*i+3]=False
    K0=np.zeros((N,N))
    for r in csv.DictReader((src/'rest.matrix.csv').open()):K0[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    m=float(node.find('UniformMass').get('totalMass'))/(N//3);K=K0[np.ix_(free,free)];e,V=eigh((K+K.T)/2,m*np.eye(len(K)),subset_by_index=[0,0]);lam=float(e[0]);mode=V[:,0];fg=np.tile(m*np.fromstring(root.get('gravity'),sep=' '),N//3)[free];modal_force=float(mode@fg);force=np.zeros(N);force[free]=m*mode*modal_force;root.set('gravity','0 0 0');dt=.00125 if a.half else .0025;root.set('dt',str(dt))
    node.remove(node.find('NativeElasticMatrixObserver'));ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad');ET.SubElement(node,'ConstantForceField',indices=' '.join(map(str,range(N//3))),forces=' '.join(format(x,'.17g') for x in force))
    for n in root.iter():
        for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
    tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'force_pattern.json').write_text(json.dumps(dict(force_N=force.tolist(),free_mode=mode.tolist(),eigenvalue_s_minus2=lam,modal_force=modal_force,scope='Mathematical spatial load projection,not realizable actuator assumption')));steps=round(.1/dt);cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')];pre=dict(command=cmd,SDK='/home/ubuntu/SOFA/v26.06.00',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_K_sha256=sha(src/'rest.matrix.csv'),source_scene_sha256=sha(src/'scene.scn'),estimated_runtime_s=2,memory_GiB=4,child_limit_s=60,changed='Only gravity spatial force→first-mode-projected ConstantForceField;no Guide/Cable and SAME FEM/mass/root/ODE. New diagnostic load,NOT gripper.',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')});(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else [];logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));trace=[];x=v=0.;c=1+1e-4*lam;s=np.sqrt(complex(c*c/4-lam));r1=-c/2+s;r2=-c/2-s
    for r in rows:
        v=(v+dt*(modal_force-lam*x))/(1+dt*c+dt*dt*lam);x+=dt*v;t=float(r['time_s']);actual=(np.fromstring(r['q'],sep=' ')-q0)[free];eta=float(m*mode@actual);exact=float((modal_force/lam*(1+(r2*np.exp(r1*t)-r1*np.exp(r2*t))/(r1-r2))).real);den=max(abs(eta),abs(x));trace.append(dict(time_s=t,actual_modal_displacement=eta,BE_modal_displacement=x,continuous_modal_displacement=exact,native_BE_relative=abs(eta-x)/den if den else None,native_continuous_relative=abs(eta-exact)/max(abs(eta),abs(exact)),off_mode_mass_norm=float(np.sqrt(m)*np.linalg.norm(actual-mode*eta))))
    d=dict(status='PASS_ISOLATED_MODE_DISCRETE_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==steps and max(r['native_BE_relative'] for r in trace)<=.001 else 'FAIL_MODAL_COUPON',process=proc,outputs=len(rows),mode_Hz=float(np.sqrt(lam)/(2*np.pi)),maximum_native_BE_relative=max(r['native_BE_relative'] for r in trace) if trace else None,maximum_native_continuous_relative=max(r['native_continuous_relative'] for r in trace) if trace else None,first=trace[0] if trace else None,physical_validation='NOT QUALIFIED',B3_time_convergence='FAIL_PRESERVED',scope='Actual Native FEM forced by one mode;discrete agreement only,not modal-filtered production model or mechanical improvement.');(out/'trace.json').write_text(json.dumps(trace,indent=2));(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
