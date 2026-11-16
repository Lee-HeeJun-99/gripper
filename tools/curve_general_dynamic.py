"""Short free-rigid sphere/Hermite dynamical smoke;not a gripper experiment."""
import argparse,csv,json,re
from pathlib import Path
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build',required=True);p.add_argument('--steps',type=int,default=20);p.add_argument('--dt',type=float,default=.0005);p.add_argument('--spacing',type=float,default=.02);p.add_argument('--speed',type=float,default=.02);a=p.parse_args()
 if not a.tag.replace('_','').isalnum()or not 1<=a.steps<=128 or not 0<a.dt<=.001 or not .001<=a.spacing<=1 or not 0<a.speed<=.2:raise ValueError('bounded fresh smoke')
 out=ROOT/'results'/('vector_history_moving_'+a.tag);out.mkdir(exist_ok=False)
 build=Path(a.build).resolve();plugin=build/'libReGripGeneralVectorContact.so';sdk=ROOT/'build/grasp_20261115/sofa_patched'
 libraries=logged(['ldd',plugin],out/'ldd',30)
 if libraries['exit_code']:raise ValueError('ldd failed')
 runtime={}
 for line in (out/'ldd/stdout.log').read_text().splitlines():
  if 'not found'in line:raise ValueError('unresolved library')
  m=re.search(r'(libSofa\S+)\s+=>\s+(\S+)',line)
  if m:
   q=Path(m[2]).resolve()
   if not q.is_relative_to(sdk.resolve()):raise ValueError('mixed SDK')
   runtime[m[1]]=dict(path=str(q),sha256=sha(q))
 if not runtime:raise ValueError('no SOFA dependency')
 write_json(out/'identity.json',dict(binary_sha256=sha(plugin),generated_sha256=sha(build/'GeneralGenerated.inc'),runtime=runtime,dt=a.dt,steps=a.steps,spacing=a.spacing,speed=a.speed,driver_sha256=sha(sdk/'bin/graph_probe'),scope='free sphere and free Hermite endpoints;not structural gripper'))
 scene=f'''<?xml version="1.0"?>
<Node name="GeneralHistoryMovingSphere" dt="{a.dt}" gravity="0 0 0">
 <RequiredPlugin pluginName="Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass Sofa.Component.ODESolver.Backward Sofa.Component.LinearSolver.Direct"/>
 <DefaultAnimationLoop/>
 <EulerImplicitSolver rayleighMass="0" rayleighStiffness="0"/>
 <EigenSparseLU/>
 <MechanicalObject template="Rigid3d" position="-.3 1.01 0 0 0 0 1 .3 1.01 0 0 0 0 1 0 0 0 0 0 0 1" velocity="0 -.01 {a.speed} 0 0 .01 0 -.01 {a.speed} 0 0 -.01 0 0 0 0 0 0"/>
 <UniformMass template="Rigid3d" totalMass=".03"/>
 <GeneralVectorCurvedContact segments="0 1" objectIndex="2" shape="0" radius="1" pointRadius=".02" lineStiffness=".001" tangentLineStiffness=".001" mu=".3" historySpacing="{a.spacing}" stride="1" filename="{out/'contact.csv'}"/>
</Node>'''
 # This generated experiment file is deliberately exclusive to this campaign.
 from xml.etree import ElementTree as ET
 ET.fromstring(scene)
 (out/'scene.scn').write_text(scene)
 cmd=[sdk/'bin/graph_probe',sdk,out/'scene.scn',str(a.steps),'0',plugin]
 process=logged(cmd,out/'process',480)
 text=(out/'process/stdout.log').read_text()+(out/'process/stderr.log').read_text()
 rows=list(csv.DictReader((out/'contact.csv').open()))if(out/'contact.csv').exists()else[]
 error=bool(re.search(r'\[ERROR\]|FAIL|Unused Attribute',text))
 status='PASS'if process['exit_code']==0 and not error and len(rows)==a.steps and any(float(r['normal_force'])>0 for r in rows)else'FAIL'
 write_json(out/'summary.json',dict(status=status,process=process,rows=len(rows),error_log=error,full_gripper='NOT RUN',energy='BLOCKED'))
 print(json.dumps(dict(out=str(out),status=status)))
if __name__=='__main__':main()
