"""Check potential-only correction in actual Native Newton/line-search graph.

Unlike699's Newmark graph, Newton may consult potential during acceptance;do not
assume that an API-only change is dynamically pure without this separate test.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def read(path):
 with path.open() as f:return list(csv.DictReader(f))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 meta=json.loads((BASE/'results/b3_native_spring_potential_adapter699/summary.json').read_text());build=BASE.parent/meta['build'];binary=build/'libReGripSpringPotential.so'
 observer_meta=json.loads((BASE/'results/b3_native_spring_energy697/summary.json').read_text());observer=BASE.parent/observer_meta['build']/'libReGripSpringEnergy.so'
 if sha(binary)!=meta['binary_sha256'] or sha(observer)!=observer_meta['binary_sha256']:raise ValueError('frozen compiled Native adapter/observer mismatch')
 records=[]
 for mode in ('taut_release','initial_slack'):
  origin=BASE/'results/b3_native_elastic_newton695'/(mode+'_0.0002500');d=out/mode;d.mkdir();root=ET.parse(origin/'scene.scn').getroot();root.find('SpringForceField').tag='ReGripTensionSpringPotential'
  for lib in (binary,observer):root.insert(0,ET.Element('RequiredPlugin',pluginName=str(lib)))
  for node in root.iter():
   if node.get('filename'):node.set('filename',str(d/Path(node.get('filename')).name))
  ET.SubElement(root,'NativeSpringEnergyJournal',filename=str(d/'energy.csv'));ET.ElementTree(root).write(d/'scene.scn')
  proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','32','--hideProgressBar',d/'scene.scn'],d/'process',480)
  logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));r=dict(mode=mode,process=proc,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_EXECUTION')
  if proc['exit_code']==0 and not r['sofa_errors']:
   before,after=read(origin/'probe.csv.point.csv'),read(d/'probe.csv.point.csv');energy=read(d/'energy.csv')
   if len(after)!=32 or len(energy)!=32:raise ValueError('partial actual Newton input')
   error=0.
   for row,e in zip(after,energy):
    q=np.fromstring(row['q'],sep=' ').reshape(-1,3);extension=max(float(np.linalg.norm(q[1]-q[0]))-(.09 if mode=='taut_release' else .11),0.)
    error=max(error,abs(float(e['actual_native_potential_J'])-50*extension**2))
   r.update(actual_state_force_slot_Newton_status_residualGraph_identity_exact=before==after,maximum_potential_reference_error_J=error,status='PASS_NEWTON_POTENTIAL_ONLY_SCOPE' if before==after and error<=1e-12 else 'FAIL_NEWTON_PURITY')
  records.append(r)
 result=dict(status='PASS_NEWTON_API_PURITY_NOT_TIME_OR_B3' if len(records)==2 and all(r['status']=='PASS_NEWTON_POTENTIAL_ONLY_SCOPE' for r in records) else 'FAIL_NEWTON_ADAPTER_VALIDITY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),build=str(build.relative_to(BASE.parent)),binary_sha256=sha(binary),observer_binary_sha256=sha(observer),records=records,scope='Actual NativeBDF1/Newton potential-only adapter. Allstate/force-slot/Newtonjournals compareEXACT. DoesNOTfix first-order dissipation/timeGate or certify general Newton graphs/realwire/B3.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
