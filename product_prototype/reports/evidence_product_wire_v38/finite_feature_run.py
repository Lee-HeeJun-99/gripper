"""Read-only Native feature identities and finite-edge point attribution."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_feature_rows
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_finite_mapped552';meta=json.loads((src/'summary.json').read_text());binary,source=compiled_feature_rows()
 records=[];checks=[];purity=0.
 for alarm in ('1','5'):
  d=out/alarm;d.mkdir();root=ET.parse(src/alarm/'scene.scn').getroot()
  for item in root.iter():
   if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
  ET.SubElement(root,'RequiredPlugin',pluginName=str(binary));ET.SubElement(root,'NativeFeatureRows',narrow='@'+root.find('BVHNarrowPhase').get('name'),filename=str(d/'features.csv'));ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(meta['steps']),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));r=dict(alarm_mm=int(alarm),process=process,status='FAIL_NATIVE_FEATURE_RUN',scene_sha256=sha(d/'scene.scn'))
  if process['exit_code']==0 and '[ERROR]' not in logs:
   frames={};states={}
   for i in (0,1):
    states[i]=read(d/f'guide{i}.csv');reference=read(src/alarm/f'guide{i}.csv');assert len(states[i])==len(reference)==meta['steps']
    for x,y in zip(states[i],reference):
     for key in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):purity=max(purity,float(np.max(abs(vec(x[key])-vec(y[key])))))
    for part in ('eyelet','support'):frames[i,part]=read(d/f'mapped{i}_{part}.csv')
   features=read(d/'features.csv');previous_time={float(s['time_s']):k for k,s in enumerate(states[0])}
   for feature in features:
    t=float(feature['time_s']);k=previous_time[t]
    for side in (0,1):
     vertex0=int(feature[f'line{side}_vertex0']);vertex1=int(feature[f'line{side}_vertex1'])
     if vertex0<0:continue
     path=feature[f'model{side}'];body=0 if '/guide0/' in path else 1;part='support' if '/supportCollision/' in path else 'eyelet';field='vertices_m' if part=='eyelet' else 'support_vertices_m';q=np.array(meta['models'][body][field]) if k==0 else vec(frames[body,part][k-1]['q']).reshape(-1,3);u=q[vertex0];v=q[vertex1];point=vec(feature[f'point{side}']);direction=v-u;length2=direction@direction
     if length2<=0:raise ValueError('degenerate actual Native edge')
     parameter=float((point-u)@direction/length2);perp=float(np.linalg.norm(point-u-parameter*direction));distance=float(np.linalg.norm(point-u-np.clip(parameter,0,1)*direction));checks.append(dict(alarm_mm=int(alarm),time_s=t,model=path,contact_id=int(feature['contact_id']),pair_index=int(feature['pair_index']),element=int(feature[f'element{side}']),vertex0=vertex0,vertex1=vertex1,finite_edge_parameter=parameter,perpendicular_distance_m=perp,finite_segment_distance_m=distance,detector_value=float(feature['value']),deltaT_raw=float(feature['deltaT'])))
   r.update(status='READ_ONLY_NATIVE_FEATURES_RECORDED',feature_rows=len(features))
  records.append(r)
 result=dict(status='NATIVE_FEATURE_DIAGNOSTIC_ONLY' if all(r['status']=='READ_ONLY_NATIVE_FEATURES_RECORDED' for r in records) else 'FAIL_NATIVE_FEATURE_RUN',scope='Same actual Native finite compound scene,read-only feature IDs and endpoint topology. deltaT is raw API data,NOT certified continuous birth time. Line parameters and distances are not corrected/clamped in physics.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),binary_sha256=sha(binary),compiled_source_sha256=sha(source),source_summary_sha256=sha(src/'summary.json'),strict_observer_state_error=purity,strict_observer_state_pass=purity<=1e-12,records=records,line_checks=checks,maximum_native_point_to_finite_segment_distance_m=max((r['finite_segment_distance_m'] for r in checks),default=None),maximum_native_point_perpendicular_edge_distance_m=max((r['perpendicular_distance_m'] for r in checks),default=None))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'Observer.cpp').write_bytes(source.read_bytes());(out/'CMakeLists.txt').write_bytes((BASE/'sofa/native_feature_rows/CMakeLists.txt').read_bytes());print(json.dumps({k:v for k,v in result.items() if k not in ('line_checks','records')},indent=2))
if __name__=='__main__':main()
