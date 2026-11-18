"""Scale-one actual saved SOFA geometry and discrete centreline metrics.
No contact-area/pressure/holding estimator and no manufactured wrap pose.
"""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--accepted-prefix-step',type=int);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text())
 if a.accepted_prefix_step is None:
  if meta['status'] not in ('PASS','EXPERIMENTAL') or meta['process']['exit_code'] or meta['sofa_errors']:raise ValueError('complete actual continuation required')
 else:
  if meta['status']!='FAIL':raise ValueError('explicit accepted-prefix mode requires preserved failed horizon')
  checkpoint=src/f'three.checkpoint_{a.accepted_prefix_step}.txt'
  if sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('accepted checkpoint changed')
  tokens=checkpoint.read_text().split();state=list(csv.DictReader((src/'three.states.csv').open()))[-1];q=np.fromstring(state['q'],sep=' ');v=np.fromstring(state['v'],sep=' ');n=len(q)
  if tokens[0]!='REGRIP_EDGE_V2' or float(tokens[1])!=float(state['time']) or not np.array_equal(q,np.array(tokens[5:5+n],dtype=float)) or not np.array_equal(v,np.array(tokens[5+n:5+2*n],dtype=float)):raise ValueError('last actual accepted state differs from checkpoint')
 for n,h in meta['raw_hashes'].items():
  if sha(src/n)!=h:raise ValueError('actual raw changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');scene=ET.parse(src/'scene.scn');topology=scene.find('.//TriangleSetTopologyContainer');rest=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3);states=list(csv.DictReader((src/'three.states.csv').open()));state=states[-1];center=np.fromstring(state['q'],sep=' ')[-6:-3];world=[];initial=[];metrics=[];reconstruction_error=0.;profiles=[]
 depth=np.sqrt(75**2+30.01**2-50**2);angle=np.arctan2(50,depth)-np.arctan2(30.01,75)
 for f in range(3):
  field=list(csv.DictReader((src/f'film_{f}.csv').open()))[-1];u=np.fromstring(list(csv.DictReader((src/f'displacement_{f}.csv').open()))[-1]['u'],sep=' ').reshape(-1,3);x=np.fromstring(field['x'],sep=' ').reshape(-1,3);reconstruction_error=max(reconstruction_error,float(np.max(abs(x-rest-u))));phi=2*np.pi*f/3;radial=np.array([np.cos(phi),np.sin(phi),0]);tangent=np.array([-np.sin(phi),np.cos(phi),0]);z=np.array([0,0,1]);R=np.column_stack((-np.sin(angle)*radial-np.cos(angle)*z,tangent,np.cos(angle)*radial-np.sin(angle)*z));origin=50*radial-12*tangent;world.append(x@R.T+origin);initial.append(rest@R.T+origin)
  for name,offset,ny in (('skin',0,5),('left_rail',105,3),('right_rail',168,3)):
   line=x[offset:offset+21*ny].reshape(21,ny,3).mean(axis=1);reference=rest[offset:offset+21*ny].reshape(21,ny,3).mean(axis=1);delta=np.diff(line,axis=0);length=np.linalg.norm(delta,axis=1);unit=delta/length[:,None];turn=np.arctan2(np.cross(unit[:-1],unit[1:])[:,1],np.sum(unit[:-1]*unit[1:],axis=1));curvature=turn/((length[:-1]+length[1:])/2);tip_angle=np.arctan2(np.cross(unit[0],unit[-1])[1],np.dot(unit[0],unit[-1]));metrics.append(dict(finger=f,part=name,tip_width_mean_displacement_mm=(line[-1]-reference[-1]).tolist(),max_abs_discrete_curvature_per_mm=float(np.max(abs(curvature))),tip_root_tangent_angle_deg=float(np.degrees(tip_angle)),arclength_mm=float(length.sum())));profiles.append((f,name,line[:,0],line[:,2]-reference[:,2],line[1:-1,0],curvature))
 with (out/'actual_end.obj').open('w') as stream:
  stream.write('# ACTUAL SOFA saved geometry,scale1;NOT qualified wrapping/grasp\n')
  for f,x in enumerate(world):
   for point in x:stream.write('v '+' '.join(format(v,'.17g') for v in point)+'\n')
  for f in range(3):
   for t in tri:stream.write('f '+' '.join(str(int(i)+1+231*f) for i in t)+'\n')
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 fig=plt.figure(figsize=(14,5));ax=fig.add_subplot(131);P=np.array([[1/np.sqrt(2),-1/np.sqrt(2),0],[1/np.sqrt(6),1/np.sqrt(6),np.sqrt(2/3)]])
 for f in range(3):
  projected=world[f]@P.T;ax.add_collection(PolyCollection(projected[tri],facecolors=('tab:blue','tab:orange','tab:green')[f],edgecolors='none',alpha=.12));line=initial[f][:105].reshape(21,5,3).mean(axis=1)@P.T;ax.plot(*line.T,'--',color='gray',linewidth=.6)
 cc=center@P.T;az=np.linspace(0,2*np.pi,100);ax.plot(cc[0]+30*np.cos(az),cc[1]+30*np.sin(az),color='gray',linewidth=.8);ax.autoscale_view();ax.set_aspect('equal');ax.set_xlabel('orthographic u [mm]');ax.set_ylabel('orthographic v [mm]');ax.set_title('Actual geometry,scale1\northographic projection;dashed:reference')
 ax2=fig.add_subplot(132);ax3=fig.add_subplot(133)
 for f,name,x,z,cx,k in profiles:
  if f==0:ax2.plot(x,z,label=name);ax3.plot(cx,k,label=name)
 ax2.set_xlabel('local x [mm]');ax2.set_ylabel('width-mean z deformation [mm]');ax3.set_xlabel('local x [mm]');ax3.set_ylabel('discrete signed curvature [1/mm]');ax2.legend(fontsize=8);ax3.legend(fontsize=8);fig.suptitle('Actual SOFA3film/free sphere t='+state['time']+'s / dt='+str(meta.get('dt',.0002))+'s\nDLL '+meta['binary_sha256'][:12]+' / gravity0,Fz=-.001N,friction OFF;NOT wrap/lift/holding certificate');fig.tight_layout();fig.savefig(out/'actual_geometry_curvature.png',dpi=160);plt.close(fig)
 result=dict(status='PASS' if reconstruction_error<1e-12 else 'FAIL',scope='read-only actual geometry/discrete shape reconstruction,NOT physical wrapping/grasp qualification',case=a.case,parent_summary_sha256=sha(src/'summary.json'),binary_sha256=meta['binary_sha256'],actual_time_s=float(state['time']),displacement_scale=1,reconstruction_error_mm=reconstruction_error,body_center_mm=center.tolist(),body_quaternion='actual checkpoint stores separately;isotropic sphere rendering orientation invariant',metrics=metrics,contact_area=None,pressure=None,holding_load=None,wrapping_qualification='NOT ESTABLISHED;centreline bending is not continuous contact coverage',image_sha256=sha(out/'actual_geometry_curvature.png'),obj_sha256=sha(out/'actual_end.obj'));write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('metrics',)}))
if __name__=='__main__':main()
