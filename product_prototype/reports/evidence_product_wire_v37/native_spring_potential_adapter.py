"""Opt-in potential-only adapter validation, preserving actual Native dynamics."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def read(path):
 with path.open() as f:return list(csv.DictReader(f))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 source=BASE/'sofa/native_unilateral_spring';build=BASE/'cad'/('build_'+a.tag)
 for name in ('Adapter.cpp','CMakeLists.txt'):(out/name).write_bytes((source/name).read_bytes())
 config=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',480)
 compiled=guarded(['cmake','--build',build,'--parallel','1'],out/'compile',480) if config['exit_code']==0 else None
 binary=build/'libReGripSpringPotential.so';records=[]
 original=BASE/'results/b3_native_spring_energy697';oldmeta=json.loads((original/'summary.json').read_text())
 observer=BASE.parent/oldmeta['build']/'libReGripSpringEnergy.so'
 if sha(observer)!=oldmeta['binary_sha256']:raise ValueError('energy observer identity mismatch')
 if compiled and compiled['exit_code']==0:
  for mode,origin,steps in [('taut_release',original/'taut_release',32),('initial_slack',original/'initial_slack',32),('slack_minus',BASE/'results/b3_native_spring_potential_fd698/minus',1),('slack_plus',BASE/'results/b3_native_spring_potential_fd698/plus',1)]:
   d=out/mode;d.mkdir();root=ET.parse(origin/'scene.scn').getroot();root.find('SpringForceField').tag='ReGripTensionSpringPotential';root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
   for node in root.iter():
    if node.get('filename'):node.set('filename',str(d/Path(node.get('filename')).name))
   ET.ElementTree(root).write(d/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',d/'scene.scn'],d/'process',480)
   logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));r=dict(mode=mode,process=proc,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_EXECUTION')
   if proc['exit_code']==0 and not r['sofa_errors']:
    before,after=read(origin/'probe.csv.point.csv'),read(d/'probe.csv.point.csv');energy=read(d/'energy.csv')
    if len(after)!=steps or len(energy)!=steps:raise ValueError('partial adapter trial')
    frames=[]
    for state,e in zip(after,energy):
     q=np.fromstring(state['q'],sep=' ').reshape(-1,3);extension=max(float(np.linalg.norm(q[1]-q[0]))-(.09 if mode=='taut_release' else .11),0.)
     frames.append(dict(time_s=float(e['time_s']),actual_potential_J=float(e['actual_native_potential_J']),independent_physical_potential_J=50*extension**2))
    error=max(abs(f['actual_potential_J']-f['independent_physical_potential_J']) for f in frames)
    r.update(status='PASS_POTENTIAL_ONLY_SCOPE' if before==after and error<=1e-12 else 'FAIL_POTENTIAL_OR_STATE',actual_q_v_force_slot_identity_exact=before==after,maximum_potential_reference_error_J=error,frames=frames)
   records.append(r)
   if r['status']=='FAIL_NATIVE_EXECUTION':break
 success=len(records)==4 and all(r['status']=='PASS_POTENTIAL_ONLY_SCOPE' for r in records)
 gradient=(records[-1]['frames'][0]['actual_potential_J']-records[-2]['frames'][0]['actual_potential_J'])/2e-6 if success else None
 result=dict(status='PASS_POTENTIAL_ONLY_NOT_TIME_OR_B3' if success and gradient==0 else 'FAIL_POTENTIAL_ADAPTER',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),build=str(build.relative_to(BASE.parent)),binary_sha256=sha(binary) if binary.exists() else None,source_hashes={n:sha(out/n) for n in ('Adapter.cpp','CMakeLists.txt')},observer_binary_sha256=sha(observer),configure=config,compile=compiled,slack_actual_potential_FD_gradient_N=gradient,records=records,scope='Potential API only Native subclass,unchanged inherited forces/tangents/Newmark. Sameq/v/force-slot as unmodified Native atALLsavedtimes. DoesNOTfix release discretization/timeGate,notB3/Holding/realwirevalidation.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({**result,'records':[{k:v for k,v in r.items() if k!='frames'} for r in records]},indent=2))
if __name__=='__main__':main()
