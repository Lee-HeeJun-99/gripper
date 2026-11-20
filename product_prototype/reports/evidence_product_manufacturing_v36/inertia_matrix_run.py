"""Build/read actual Native matrix,compare observer trajectory with immutable627."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_inertia_force,compiled_pair_rows
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_inertia_force_trap627');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'sofa/native_system_matrix';build=BASE/'cad'/('build_'+a.tag);identity={n:sha(source/n) for n in ('Observer.cpp','CMakeLists.txt')}
 for n in identity:(out/n).write_bytes((source/n).read_bytes())
 config=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',480);compiled=guarded(['cmake','--build',build,'--parallel','1'],out/'compile',480) if config['exit_code']==0 else None;binary=build/'libReGripSystemMatrix.so';records=[]
 compiled_inertia_force();compiled_pair_rows()
 if compiled and compiled['exit_code']==0:
  src=BASE/'results'/a.case;steps=json.loads((src/'summary.json').read_text())['steps']
  for variant in (0,1):
   d=out/str(variant);d.mkdir();root=ET.parse(src/str(variant)/'scene.scn').getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
   for item in root.iter():
    if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
   ET.SubElement(root,'NativeSystemMatrix',solver='@globalLinear',filename=str(d/'matrix.csv'));ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));r=dict(variant=variant,process=process,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn'),observer_state_error=None)
   if process['exit_code']==0 and not r['sofa_errors']:
    error=0.
    for i in (0,1):
     for name,keys in ((f'guide{i}.csv',('rigid_q','rigid_v','object_impulse_Ns_Nms')),(f'mass{i}.csv',('q','v'))):
      old=read(src/str(variant)/name);new=read(d/name)
      if len(old)!=steps or len(new)!=steps:raise ValueError('incomplete observed trajectory')
      for x,y in zip(old,new):
       for key in keys:error=max(error,float(np.max(abs(vec(x[key])-vec(y[key])))))
    r['observer_state_error']=error;r['matrix_rows']=len(read(d/'matrix.csv'))
   records.append(r)
 result=dict(status='PASS_MATRIX_OBSERVER_PURITY_ONLY' if len(records)==2 and all(r['observer_state_error'] is not None and r['observer_state_error']<=1e-12 for r in records) else 'FAIL_BUILD_OR_NATIVE_PROBE',scope='Read-only actual global Native system matrix,NO solver/state writes or assumption about assembly coefficients',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),source_hashes=identity,build=str(build.relative_to(BASE.parent)),binary_sha256=sha(binary) if binary.exists() else None,configure=config,compile=compiled,records=records,SDK='/home/ubuntu/SOFA/v26.06.00');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
