"""One evidence-based Native termination normalization contrast;no tolerance fit."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=[10,100,500],default=10);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_refined_interface1266';tree=ET.parse(src/'scene.scn');root=tree.getroot();solver=root.find('BlockGaussSeidelConstraintSolver');assert solver.get('tolerance')=='1e-10' and solver.get('scaleTolerance') is None;solver.set('scaleTolerance','0')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'].copy();cmd[cmd.index('-n')+1]=str(a.steps);cmd[-1]=str(out/'scene.scn');pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),steps=a.steps,estimated_runtime_s=4,classification='NATIVE_TERMINATION_NORMALIZATION_CONTRAST_ONLY',hypothesis='519rows and currentError up to5.18e-8 match N*1e-10 scaled termination. Disable only scaleTolerance;numeric tolerance1e-10,maxIterations1000,allVerified default,physical inputs and dt unchanged. Not old root815 combined flag/LMD trial;not a convergence repair claim.')
 if a.steps>10:
  if not a.pilot:raise ValueError('actual pilot required')
  pilot=BASE/'results'/a.pilot;pm=json.loads((pilot/'preflight.json').read_text());pr=json.loads((pilot/'summary.json').read_text());forecast=pr['process']['runtime_s']*a.steps/pm['steps'];pre.update(estimated_runtime_s=forecast,pilot_summary_sha256=sha(pilot/'summary.json'))
  if forecast>120:
   (out/'preflight.json').write_text(json.dumps(pre,indent=2));d=dict(status='BLOCKED_COST_FORECAST_NOT_PHYSICS_FAIL',predicted_runtime_s=forecast,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d));return
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'constraints.csv').open())) if (out/'constraints.csv').exists() else [];d=dict(status='NATIVE_TERMINATION_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and 'Unused Attribute'not in logs and len(rows)==a.steps else 'FAIL_EXECUTION',process=proc,outputs=len(rows),max_solver_error=max(float(r['error']) for r in rows) if rows else None,max_iterations=max(int(r['iterations']) for r in rows) if rows else None,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
