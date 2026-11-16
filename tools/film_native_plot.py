"""Scientific plots/OBJ from actual native-contact accepted states, no pose editing."""
import argparse,csv,os,json,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--times',type=float,nargs=3,default=[.1,.25,.5]);a=p.parse_args();out=ROOT/'designs/visualizations'/('film_native_'+a.tag);out.mkdir(exist_ok=False);os.environ['MPLCONFIGDIR']=str(out/'matplotlib_cache')
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Circle,Polygon
 source=ROOT/'results'/('autonomous_film_'+a.case)/'1';r=list(csv.DictReader((source/'contact.csv').open()));j=list(csv.DictReader((source/'journal.csv').open()));times=np.array([float(s['time']) for s in r]);tree=ET.parse(source/'scene.scn');tri=np.fromstring(tree.find("Node[@name='assembly']/Node[@name='actual']/TriangleSetTopologyContainer").get('triangles'),sep=' ',dtype=int).reshape(-1,3)
 execution=json.loads((source.parent/'summary.json').read_text());complete=execution.get('status')=='PASS'
 center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ');sphere_model=tree.find("Node[@name='fixed']/SphereCollisionModel");radius=float(sphere_model.get('radius')) if sphere_model is not None else float(tree.find("FilmNativeObserver").get("radius"));object_shape=tree.find("FilmNativeObserver").get("objectShape","sphere")
 owner=tree.find('FilmNativeCoupledCorrection');jacobian_stage='accepted current sphere' if owner is not None and owner.get('currentSphereNormal','0')=='1' else 'begin native'
 fig,axes=plt.subplots(1,3,figsize=(15,4),layout='constrained')
 for ax,t in zip(axes,a.times):
  index=int(np.argmin(abs(times-t)));q=np.fromstring(r[index]['positions'],sep=' ').reshape(-1,3);sphere_patch=Circle((center[0],center[2]),radius,color='lightgray',label=f'fixed sphere y={center[1]:g} section')
  if object_shape=='cylinderY':
   points=np.fromstring(tree.find("Node[@name='fixed']/Node[@name='collision_mesh']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);n=(len(points)-2)//2;sphere_patch=Polygon(points[:n][:,[0,2]],closed=True,color='lightgray',label=f'actual {n}-facet cylinder side section')
  ax.add_patch(sphere_patch)
  for indices,label in ((np.arange(2,105,5),'skin centerline'),(np.arange(106,168,3),'left rail centerline'),(np.arange(169,231,3),'right rail centerline')):ax.plot(q[indices,0],q[indices,2],label=label)
  ax.set(xlabel='x [mm]',ylabel='z [mm]',title=f'Actual accepted state t={times[index]:.5g}s');ax.set_aspect('equal');ax.set_xlim(0,105);ax.set_ylim(min(-17,float(min(q[:,2]))-1),max(3,float(max(q[:,2]))+1))
  with (out/f'actual_t{t:g}.obj').open('x') as stream:
   stream.write('# Actual SOFA accepted coordinates, displacement scale1,not qualified grasp\n')
   for v in q:stream.write('v '+' '.join(map(str,v))+'\n')
   for face in tri:stream.write('f '+' '.join(str(i+1) for i in face)+'\n')
 axes[0].legend(fontsize=6);fig.suptitle(('Completed execution / ' if complete else 'PARTIAL FAILED run / ')+'Actual SOFA Film–Rails–Tendon / fixed collision object; experimental, NOT qualified grasp; scale1');fig.savefig(out/'actual_contact_states.png',dpi=160);plt.close(fig)
 f=np.array([np.fromstring(s['body_force'],sep=' ') for s in r]);dt=np.array([float(s['dt']) for s in r]);fig,axes=plt.subplots(2,1,sharex=True,layout='constrained');axes[0].plot(times,np.linalg.norm(f,axis=1));axes[0].set_ylabel('|Jᵀλ/dt| [F]');axes[1].plot(times,np.cumsum(f[:,2]*dt));axes[1].set(xlabel='time [s]',ylabel='vertical impulse [F s]');fig.suptitle('Actual contact; '+jacobian_stage+' Jacobian; fixed reaction unavailable');fig.savefig(out/'actual_contact_force.png',dpi=160);plt.close(fig)
 write_json(out/'source.json',dict(inputs={str((source/file).relative_to(ROOT)):sha(source/file) for file in ('contact.csv','journal.csv','scene.scn')},force_jacobian_stage=jacobian_stage,displacement_scale=1,input_execution_status=execution.get('status'),trajectory_complete=complete,scope='Actual accepted SOFA surface;frictionless fixed sphere,not free-object grasp',pressure=None,contact_area=None,relative_xy_plot_note='Side projection,not volumetric rail thickness rendering'))
if __name__=='__main__':main()
