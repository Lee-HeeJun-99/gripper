"""Frozen B3 scene plus public stock detection-data schedule;no physics solver."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/force_release_clear_support375';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text());binary=BASE/'cad/build_alarm_window484/libReGripAlarmWindow.so';native=BASE.parent/meta['build']/'libReGripProductSequence.so'
 if sha(native)!=meta['binary_sha256']:raise ValueError('frozen physical/controller binary mismatch')
 (out/'source').mkdir()
 for name in ('Controller.cpp','CMakeLists.txt'):shutil.copy2(src/'source'/name,out/'source'/name)
 for name in ('Controller.cpp','CMakeLists.txt'):shutil.copy2(BASE/'sofa/native_alarm_window'/name,out/('Alarm'+name))
 shutil.copy2(binary.parent/'CMakeCache.txt',out/'AlarmCMakeCache.txt');(out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
 for name in ('config.json','mesh.json','holding_protocol.json','motion_commands.json','initial_geometry.json','geometry_generator.py'):shutil.copy2(src/name,out/name)
 tree=ET.parse(src/'scene.scn');root=tree.getroot()
 for node in root.iter():
  for key,value in list(node.attrib.items()):
   if str(src) in value:node.set(key,value.replace(str(src),str(out)))
 root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));root.find('MinProximityIntersection').set('name','proximity')
 ET.SubElement(root,'NativeAlarmWindow',target='@proximity',begin='2.386',end='2.396',narrow='.001',wide='.005',filename=str(out/'alarm_applied.csv'));tree.write(out/'scene.scn')
 schedule=dict(begin_end_clock_s=2.386,end_end_clock_s=2.396,narrow_mm=1,wide_mm=5,scope='Diagnostic detection range schedule only;contactDistance0.2mm unchanged;not general event-aware CCD or adaptive integration')
 (out/'alarm_schedule.json').write_text(json.dumps(schedule,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1200','--hideProgressBar',out/'scene.scn'],out/'process',480)
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));meta.update(status='FAIL_ALARM_WINDOW',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),process=process,scene_sha256=sha(out/'scene.scn'),alarm_schedule=schedule,alarm_binary_sha256=sha(binary),alarm_compiled_source_sha256=sha(out/'AlarmController.cpp'),producer_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),sofa_errors=logs.count('[ERROR]'))
 meta.pop('raw_hashes',None);meta.pop('metrics',None);meta.pop('source_hashes',None)
 if process['exit_code']==0 and not meta['sofa_errors'] and 'Unused Attribute' not in logs:
  counts=[len(list(csv.DictReader((out/f'finger{i}.csv').open()))) for i in range(3)]
  if counts==[1200]*3:meta['status']='RUN_COMPLETED_NOT_QUALIFIED'
 meta['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};(out/'summary.json').write_text(json.dumps(meta,indent=2));print(json.dumps({k:meta[k] for k in ('status','process','alarm_binary_sha256','alarm_compiled_source_sha256')}))

if __name__=='__main__':main()
