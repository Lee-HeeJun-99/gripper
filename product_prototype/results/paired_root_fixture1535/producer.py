"""Independent current-mesh Root/cable-origin fixture coupon;NO object/Liftclaim."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/centreline_paired1527';root=ET.parse(src/'scene.scn').getroot();meta=json.loads((BASE/'results/b3_origin_observer1075/summary.json').read_text());binary=Path(meta['binary']);assert sha(binary)==meta['binary_sha256'];root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));free=root.find("Node[@name='free0']");fixed=free.find('FixedProjectiveConstraint');ids=fixed.get('indices');free.remove(fixed);ET.SubElement(free,'LinearMovementProjectiveConstraint',indices=ids,keyTimes='-.0025 .0075 .9975',movements='0 0 0 0 0 .0001 0 0 .0001');f=root.find("Node[@name='finger0']")
 for j in range(2):ET.SubElement(f,'NativeCableOrigin',target=f'@../guides0/cable{j}/actuator',filename=str(out/f'origin{j}.csv'),drive='1',begin='0',end='.01',height='.0001')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());(out/'config.json').write_bytes((src/'config.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),origin_binary_sha256=sha(binary),origin_compiled_source_sha256=meta['compiled_source_sha256'],SDK='/home/ubuntu/SOFA/v26.06.00',memory_GiB=4,child_limit_s=60,scope='ActualNativeprojectiveRootsubset andonlypublicCableorigin;noobject,not100gLift or fixtureenergyqualification. Existing1075binary verified,not unverifiednewRigidMapping. Positionsandinterior-segmentvelocities measuredseparately.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',str(out/'scene.scn')];process=guarded(command,out/'process',60);rows=list(csv.DictReader((out/'finger0.csv').open()));logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);mask=local[:,0]<=5;q0=np.fromstring(f.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);poserror=0.;verror=0.;originerror=0.;records=[]
 for r in rows:
  t=float(r['time_s']);q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);v=np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3);want=np.array([0,0,.0001*min(1,t/.01)]);poserror=max(poserror,float(abs(q[mask]-q0[mask]-want).max()))
  if t<.01-1e-12:verror=max(verror,float(abs(v[mask]-[0,0,.01]).max()))
  records.append(dict(time_s=t,root_mean_translation_m=(q[mask]-q0[mask]).mean(0).tolist(),root_mean_velocity_m_s=v[mask].mean(0).tolist()))
 for j in range(2):
  origins=list(csv.DictReader((out/f'origin{j}.csv').open()));assert [float(r['accepted_time_s']) for r in origins]==[float(r['time_s']) for r in rows]
  for r in origins:
   t=float(r['accepted_time_s']);d=np.fromstring(r['actual_pullPoint_m'],sep=' ')-np.fromstring(r['initial_pullPoint_m'],sep=' ');originerror=max(originerror,float(abs(d-[0,0,.0001*min(1,t/.01)]).max()))
 d=dict(status='PASS_ROOT_ORIGIN_POSITION_AND_INTERIOR_VELOCITY_API_ONLY' if process['exit_code']==0 and '[ERROR]'not in logs and len(rows)==4 and max(poserror,verror,originerror)<=1e-12 else 'FAIL_ROOT_FIXTURE_API',process=process,outputs=len(rows),maximum_root_position_error_m=poserror,maximum_interior_segment_root_velocity_error_m_s=verror,maximum_actual_origin_error_m=originerror,records=records,object_Lift='NOT TESTED',physical_validation='NOT QUALIFIED',scope=pre['scope']);(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
