"""Read-only full finite-hardware wrench observation; no repeated design trial."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_pair_rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 src=BASE/'results/dispatch_finite_holding1586';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 binary,compiled=compiled_pair_rows();root=ET.parse(src/'scene.scn').getroot()
 root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
 for i in range(3):ET.SubElement(root,'NativePairRows',body=f'@guides{i}/frames',solver='@constraints',filename=str(out/f'direct{i}.csv'))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 for file in ('config.json','mesh.json','holding_protocol.json'):(out/file).write_bytes((src/file).read_bytes())
 ET.ElementTree(root).write(out/'scene.scn');(out/'Observer.cpp').write_bytes(compiled.read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),observer_binary=str(binary),observer_binary_sha256=sha(binary),compiled_source_sha256=sha(compiled),SDK='/home/ubuntu/SOFA/v26.06.00',child_limit_s=420,memory_GiB=4,forecast_s=180,scope='Frozen read-only observer ONLY; actual finite1586 baseline,not a new design or improved grasp. Require q/v/surface/impulse purity <=1e-12.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2))
 proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','800','--hideProgressBar',str(out/'scene.scn')],out/'process',420)
 errors={};counts={}
 for file,keys in [('object.csv',['rigid_q','rigid_v','object_impulse_Ns_Nms'])]+[(f'finger{i}.csv',['q_m','v_m_s']) for i in range(3)]+[(f'guide_frames{i}.csv',['rigid_q','rigid_v']) for i in range(3)]:
  old=list(csv.DictReader((src/file).open()));new=list(csv.DictReader((out/file).open())) if (out/file).exists() else [];counts[file]=len(new)
  err=0.
  if len(old)!=len(new):err=float('inf')
  else:
   for x,y in zip(old,new):
    assert float(x['time_s'])==float(y['time_s'])
    for k in keys:err=max(err,float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))))
  errors[file]=err
 logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'))
 d=dict(status='PASS_READONLY_FINITE_HOLD_OBSERVER' if proc['exit_code']==0 and '[ERROR]'not in logs and max(errors.values())<=1e-12 else 'FAIL_OBSERVER_EXECUTION_OR_PURITY',process=proc,counts=counts,maximum_errors=errors,scope=pre['scope'],files={f.name:dict(bytes=f.stat().st_size,sha256=sha(f)) for f in out.glob('*.csv')})
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='files'},indent=2))
if __name__=='__main__':main()
