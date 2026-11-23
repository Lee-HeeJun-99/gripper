"""Correct installed API link,then isolated termination-normalization contrast."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--unscaled',action='store_true');p.add_argument('--steps',type=int,choices=[10,100],default=10);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_refined_interface1266';tree=ET.parse(src/'scene.scn');root=tree.getroot();cc=root.find('GenericConstraintCorrection');assert cc.get('solverName')=='globalLinear';cc.attrib.pop('solverName');cc.set('linearSolver','@globalLinear')
 if a.unscaled:root.find('BlockGaussSeidelConstraintSolver').set('scaleTolerance','0')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'].copy();cmd[cmd.index('-n')+1]=str(a.steps);cmd[-1]=str(out/'scene.scn');pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),steps=a.steps,estimated_runtime_s=4,classification='EXPLICIT_NATIVE_CORRECTION_LINK_AND_SCOPED_CONTRAST',unscaled=a.unscaled,hypothesis='Installed GenericConstraintCorrection uses linearSolver SingleLink;old solverName is unused. First verify unchanged q/v/impulses for explicit vs auto link. Separate unscaled variant then changes ONLY normalization,not numeric tolerance.')
 if a.steps>10:
  if not a.pilot:raise ValueError('measured clean pilot required')
  pilot=BASE/'results'/a.pilot;pm=json.loads((pilot/'preflight.json').read_text());pr=json.loads((pilot/'summary.json').read_text());assert pr['status']=='CLEAN_UNSCALED_NATIVE_STATES_ONLY' and pm['unscaled']==a.unscaled;forecast=pr['process']['runtime_s']*a.steps/pm['steps'];pre.update(estimated_runtime_s=forecast,pilot_summary_sha256=sha(pilot/'summary.json'))
  if forecast>120:raise ValueError('forecast exceeds budget')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[];errors={}
 for i in (0,1):
  path=out/f'layer{i}.csv';rows=list(csv.DictReader(path.open())) if path.exists() else [];counts.append(len(rows));base=list(csv.DictReader((src/f'layer{i}.csv').open()))[:a.steps]
  for key in ('q','v'):errors[f'layer{i}_{key}']=max(float(abs(np.fromstring(r[key],sep=' ')-np.fromstring(b[key],sep=' ')).max()) for r,b in zip(rows,base)) if rows else None
 cr=list(csv.DictReader((out/'constraints.csv').open())) if (out/'constraints.csv').exists() else [];br=list(csv.DictReader((src/'constraints.csv').open()))[:a.steps];errors['constraint_impulses_Ns']=max(float(abs(np.fromstring(r['impulses_Ns'],sep=' ')-np.fromstring(b['impulses_Ns'],sep=' ')).max()) for r,b in zip(cr,br)) if cr else None;clean=proc['exit_code']==0 and '[ERROR]'not in logs and 'Unused Attribute'not in logs and counts==[a.steps]*2;status='CLEAN_UNSCALED_NATIVE_STATES_ONLY' if clean and a.unscaled else 'PASS_EXPLICIT_LINK_PURITY_ONLY' if clean and max(errors.values())<=1e-12 else 'FAIL_LINK_OR_EXECUTION';d=dict(status=status,process=proc,outputs=counts,errors_vs_old_auto_link_scaled=errors,max_solver_error=max(float(r['error']) for r in cr) if cr else None,max_iterations=max(int(r['iterations']) for r in cr) if cr else None,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
