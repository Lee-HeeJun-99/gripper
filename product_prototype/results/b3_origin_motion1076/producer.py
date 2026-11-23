"""Bounded public-data observer/controller experiment,not a new physics solver."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reuse');p.add_argument('--drive',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_root_terminal_hold1068';source=out/'source';source.mkdir()
 for name,dest in [('CableOrigin.cpp','CableOrigin.cpp'),('CableOriginCMakeLists.txt','CMakeLists.txt')]:shutil.copy2(BASE/'sofa'/name,source/dest)
 if a.reuse:
  prior=BASE/'results'/a.reuse;meta=json.loads((prior/'summary.json').read_text());binary=Path(meta['binary']);build=binary.parent
  if sha(binary)!=meta['binary_sha256'] or sha(source/'CableOrigin.cpp')!=meta['compiled_source_sha256']:raise ValueError('compiled origin identity mismatch')
 else:
  build=BASE/'cad'/('build_'+a.tag);build.mkdir(exist_ok=False)
  for name,cmd in [('configure',['cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00']),('compile',['cmake','--build',build,'-j2'])]:
   proc=guarded(cmd,out/name,120)
   if proc['exit_code']!=0:(out/'summary.json').write_text(json.dumps(dict(status='FAIL_ORIGIN_BUILD',stage=name,process=proc)));return
  binary=build/'libReGripCableOrigin.so'
 tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
 for n in root.iter():
  for k,v in list(n.attrib.items()):
   if str(src) in v:n.set(k,v.replace(str(src),str(out)))
 for f in range(3):
  node=root.find(f"./Node[@name='finger{f}']")
  for c in range(2):ET.SubElement(node,'NativeCableOrigin',target=f'@../guides{f}/cable{c}/actuator',filename=str(out/f'origin_f{f}_c{c}.csv'),drive=str(int(a.drive)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',out/'scene.scn'],out/'process',60)
 errors=[];records=[];state_error=0.
 for f in range(3):
  if not(out/f'finger{f}.csv').exists():continue
  actual=list(csv.DictReader((out/f'finger{f}.csv').open()));old=list(csv.DictReader((src/f'finger{f}.csv').open()))
  for x,y in zip(actual,old):
   for key in ('q_m','v_m_s','guide0_q_m','guide1_q_m'):state_error=max(state_error,float(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')).max()))
  for c in range(2):
   path=out/f'origin_f{f}_c{c}.csv'
   if not path.exists():continue
   for row in csv.DictReader(path.open()):
    t=float(row['accepted_time_s']);q=np.fromstring(row['actual_pullPoint_m'],sep=' ');initial=np.fromstring(row['initial_pullPoint_m'],sep=' ');expected=np.array([0,0,.0001*min(1,t/.01)])
    records.append(dict(finger=f,cable=c,time_s=t,actual_translation_m=(q-initial).tolist(),vs_moving_root_error_m=float(abs(q-initial-expected).max())))
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));complete=proc['exit_code']==0 and '[ERROR]' not in logs and len(records)==24
 result=dict(status='ORIGIN_FIXTURE_MEASURED_ONLY' if complete else 'FAIL_ORIGIN_EXECUTION',drive=a.drive,process=proc,binary=str(binary),binary_sha256=sha(binary),compiled_source_sha256=sha(source/'CableOrigin.cpp'),scene_sha256=sha(out/'scene.scn'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',records=records,maximum_origin_vs_root_error_m=max((r['vs_moving_root_error_m'] for r in records),default=None),maximum_observer_vs_baseline_state_error=state_error,observer_purity_1e12_pass=bool(complete and not a.drive and state_error<=1e-12),functional_lift='NOT RUN_NO_OBJECT',scope='Actual public CableConstraint.pullPoint API. Optional controller writes ONLY pullPoint,not Film/object/root state or force/impulse. Driving is a NEW boundary condition;not purity comparison.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in [src/'scene.scn',Path(__file__),source/'CMakeLists.txt']})
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['status','maximum_origin_vs_root_error_m','observer_purity_1e12_pass']}))
if __name__=='__main__':main()
