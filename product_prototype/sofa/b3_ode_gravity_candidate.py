"""Bounded joint candidate: global ODE damping, zero Cable, not a grasp claim."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--half',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/('b3_rail_back_zero_half1157' if a.half else 'b3_rail_back_zero1127');tree=ET.parse(src/'scene.scn');root=tree.getroot();ode=root.find('EulerImplicitSolver');ode.set('rayleighMass','1');ode.set('rayleighStiffness','0.0001');root.find("./Node[@name='finger0']/UniformMass").set('rayleighMass','0');root.find("./Node[@name='finger0']/TetrahedronFEMForceField").set('rayleighStiffness','0');assert next(root.iter('NativeCableSequence')).get('maximumForceN')=='0'
    for n in root.iter():
        for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
    tree.write(out/'scene.scn')
    for f in ('mesh.json','config.json'):shutil.copy2(src/f,out/f)
    dt=float(root.get('dt'));steps=round(.1/dt);cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')];pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),SDK='/home/ubuntu/SOFA/v26.06.00',command=cmd,dt_s=dt,expected_outputs=steps,estimated_runtime_s=2,child_limit_s=60,memory_GiB=4,change='Global ODE Rayleigh1/1e-4 instead of field1/1e-4. Guide mass ALSO globally damped:new damping law,not identical old physical model.',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')});(out/'preflight.json').write_text(json.dumps(pre,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());proc=guarded(cmd,out/'process',60);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else [];d=dict(status='NATIVE_CANDIDATE_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==steps else 'FAIL_EXECUTION',outputs=len(rows),process=proc,physical_validation='NOT QUALIFIED',holding='NOT RUN_ZERO_CABLE_NO_OBJECT');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
