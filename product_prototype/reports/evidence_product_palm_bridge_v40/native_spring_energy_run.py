"""Actual Native potential API on unilateral spring, with exact observer purity."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'sofa/native_spring_energy';build=BASE/'cad'/('build_'+a.tag)
 for name in ('CMakeLists.txt','Observer.cpp'):(out/name).write_bytes((src/name).read_bytes())
 config=guarded(['cmake','-S',src,'-B',build,'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',480)
 compiled=guarded(['cmake','--build',build,'--parallel','1'],out/'compile',480) if config['exit_code']==0 else None
 binary=build/'libReGripSpringEnergy.so';records=[]
 if compiled and compiled['exit_code']==0:
  for mode in ('taut_release','initial_slack'):
   original=BASE/'results/b3_native_elastic_tendon693'/(mode+'_0.0002500');d=out/mode;d.mkdir();root=ET.parse(original/'scene.scn').getroot()
   for node in root.iter():
    if node.get('filename'):node.set('filename',str(d/Path(node.get('filename')).name))
   root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(root,'NativeSpringEnergyJournal',filename=str(d/'energy.csv'));ET.ElementTree(root).write(d/'scene.scn')
   proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','32','--hideProgressBar',d/'scene.scn'],d/'process',480)
   logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'))
   r=dict(mode=mode,process=proc,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_EXECUTION')
   if proc['exit_code']==0 and not r['sofa_errors']:
    def read(path):
     with path.open() as f:return list(csv.DictReader(f))
    old,new=read(original/'probe.csv.point.csv'),read(d/'probe.csv.point.csv');energy=read(d/'energy.csv')
    if len(new)!=32 or len(energy)!=32:raise ValueError('partial Native energy journal')
    original_summary=json.loads((original.parent/'summary.json').read_text());reference=next(r for r in original_summary['records'] if r['mode']==mode and r['dt_s']==.00025)
    frames=[dict(time_s=float(e['time_s']),actual_native_potential_J=float(e['actual_native_potential_J']),independent_unilateral_potential_J=.5*100*max(f['geometric_length_m']-(.09 if mode=='taut_release' else .11),0.)**2) for e,f in zip(energy,reference['frames'])]
    r.update(status='ACTUAL_API_DIAGNOSTIC',observer_state_purity_exact=old==new,frames=frames,maximum_potential_disagreement_J=max(abs(f['actual_native_potential_J']-f['independent_unilateral_potential_J']) for f in frames))
   records.append(r)
 result=dict(status='SPRING_ENERGY_API_DIAGNOSTIC_NOT_GLOBAL_ENERGY_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),build=str(build.relative_to(BASE.parent)),binary_sha256=sha(binary) if binary.exists() else None,source_hashes={n:sha(out/n) for n in ('Observer.cpp','CMakeLists.txt')},configure=config,compile=compiled,records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**result,'records':[{k:v for k,v in r.items() if k!='frames'} for r in records]},indent=2))
if __name__=='__main__':main()
