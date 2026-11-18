"""Read-only actual unloaded-state velocity;NOT a recovery qualification."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='20261118_three_film_unload_end1083');p.add_argument('--step',type=int,default=200);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code'] or meta['sofa_errors']:raise ValueError('complete actual Unload endpoint required')
 for name,digest in meta['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed')
 state=list(csv.DictReader((src/'three.states.csv').open()))[-1];q=np.fromstring(state['q'],sep=' ');v=np.fromstring(state['v'],sep=' ');n=len(q);nf=(n-6)//3;tokens=(src/f'three.checkpoint_{a.step}.txt').read_text().split()
 if float(tokens[1])!=float(state['time']) or not np.array_equal(q,np.array(tokens[5:5+n],dtype=float)) or not np.array_equal(v,np.array(tokens[5+n:5+2*n],dtype=float)):raise ValueError('accepted endpoint/checkpoint q/v differ')
 scene=ET.parse(src/'scene.scn');rest=np.fromstring(scene.find('.//TriangleSetTopologyContainer').get('position'),sep=' ').reshape(-1,3);nodes=len(rest);offset=5+2*n+4+3*nodes+36;metrics=[];error=0
 for f in range(3):
  mapping=np.array(tokens[offset+f*6*nodes:offset+(f+1)*6*nodes],dtype=float).reshape(3*nodes,2);indices=mapping[:,0].astype(int);weights=mapping[:,1]
  if np.any(mapping[:,0]!=indices) or np.any(indices>=nf) or np.any(indices< -1):raise ValueError('invalid exact root mapping')
  displacement=np.zeros(3*nodes);velocity=displacement.copy();active=indices>=0;displacement[active]=weights[active]*q[f*nf+indices[active]];velocity[active]=weights[active]*v[f*nf+indices[active]];displacement=displacement.reshape(nodes,3);velocity=velocity.reshape(nodes,3);field=list(csv.DictReader((src/f'film_{f}.csv').open()))[-1];x=np.fromstring(field['x'],sep=' ').reshape(nodes,3);error=max(error,float(np.max(abs(x-rest-displacement))))
  for name,start,ny in (('skin',0,5),('left_rail',105,3),('right_rail',168,3)):
   u=displacement[start:start+21*ny];vel=velocity[start:start+21*ny];metrics.append(dict(finger=f,part=name,tip_width_mean_displacement_mm=u[-ny:].mean(axis=0).tolist(),tip_width_mean_velocity_mm_s=vel[-ny:].mean(axis=0).tolist(),node_rms_displacement_mm=float(np.sqrt(np.mean(np.sum(u*u,axis=1)))),node_rms_displacement_squared_rate_mm2_s=float(2*np.mean(np.sum(u*vel,axis=1))),applied_tension_N=float(field['T_per_rail'])))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if error<1e-12 else 'FAIL',scope='actual saved q/v reconstruction and unloaded velocity observation;NOT recovery/holding/lift certificate',parent_summary_sha256=sha(src/'summary.json'),binary_sha256=meta['binary_sha256'],sdk=meta['sdk'],actual_time_s=float(state['time']),root_mapping_reconstruction_error_mm=error,body_position_mm=q[-6:-3].tolist(),body_velocity_mm_s=v[-6:-3].tolist(),metrics=metrics,recovery='NOT ESTABLISHED;report actual residual shape and velocity,not zero tension as recovery success',gravity_mm_s2=[0,0,0],external_body_force_N=[0,0,-.001]);write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='metrics'}))
if __name__=='__main__':main()
