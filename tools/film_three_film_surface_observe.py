"""Actual skin-width deformation profiles,not a contact-area/holding estimator."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_three_film_qualified import require_completed
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--qualification');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);approval=require_completed(src,a.qualification);meta=json.loads((src/'identity.json').read_text());scene=ET.parse(src/'scene.scn');rest=np.fromstring(scene.find('.//TriangleSetTopologyContainer').get('position'),sep=' ').reshape(-1,3);out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 observed=[];shapes=[];error=0.
 for f in range(3):
  fields=list(csv.DictReader((src/('film_'+str(f)+'.csv')).open()));displacements=list(csv.DictReader((src/('displacement_'+str(f)+'.csv')).open()));u=np.fromstring(displacements[-1]['u'],sep=' ').reshape(-1,3);actual=np.fromstring(fields[-1]['x'],sep=' ').reshape(-1,3);error=max(error,float(np.max(abs(rest+u-actual))));skin=u[:105].reshape(21,5,3);left=u[105:168].reshape(21,3,3);right=u[168:].reshape(21,3,3);shapes.append((skin,left,right));observed.append(dict(finger=f,time=float(fields[-1]['time']),skin_center_node_tip_z_mm=float(skin[-1,2,2]),skin_width_mean_tip_z_mm=float(skin[-1,:,2].mean()),left_width_mean_tip_z_mm=float(left[-1,:,2].mean()),right_width_mean_tip_z_mm=float(right[-1,:,2].mean()),skin_max_abs_displacement_mm=float(np.max(np.linalg.norm(skin,axis=2))),rail_max_abs_displacement_mm=float(max(np.max(np.linalg.norm(left,axis=2)),np.max(np.linalg.norm(right,axis=2))))))
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 skin,left,right=shapes[0];x=rest[:105].reshape(21,5,3)[:,2,0];y=rest[:105].reshape(21,5,3)[-1,:,1];fig,axes=plt.subplots(1,3,figsize=(14,4))
 for j in (0,2,4):axes[0].plot(x,skin[:,j,2],label='skin reference y='+str(y[j])+'mm')
 axes[0].plot(x,left[:,:,2].mean(axis=1),'--',label='left rail width mean');axes[0].plot(x,right[:,:,2].mean(axis=1),'--',label='right rail width mean');axes[0].set_xlabel('reference material x [mm]');axes[0].set_ylabel('ACTUAL local u_z [mm]');axes[0].legend(fontsize=7)
 for i in (5,10,15,20):axes[1].plot(y,skin[i,:,2],'.-',label='reference x='+str(x[i])+'mm')
 axes[1].set_xlabel('reference material y [mm]');axes[1].set_ylabel('ACTUAL local u_z [mm]');axes[1].legend(fontsize=7)
 image=axes[2].pcolormesh(x,y,skin[:,:,2].T,shading='nearest');fig.colorbar(image,ax=axes[2],label='actual nodal u_z [mm]');axes[2].set_xlabel('reference x [mm]');axes[2].set_ylabel('reference y [mm]')
 for ax in axes[:2]:ax.grid()
 fig.suptitle('Actual SOFA skin/rail deformation,not wrapping/grasp;displacements NOT magnified\n'+meta['source_commit'][:8]+' DLL '+meta['binary_sha256'][:12]+' t='+str(observed[0]['time'])+' dt='+str(meta['dt']));fig.tight_layout();fig.savefig(out/'actual_width_profiles.png',dpi=180);plt.close(fig)
 result=dict(status='PASS' if error<=1e-12 else 'FAIL',scope='actual nodal surface observation,NOT wrapping/contact area/holding performance',case=a.case,explicit_reassessment=approval,observed=observed,world_local_reconstruction_error_mm=error,displacement_magnification=1,contact_area_mm2=None,contact_area_status='NOT MEASURED;no vertex count or row angle proxy',interpretation='centre-node tip and width-mean tip are different observables;do not equate either with wrapping angle',raw={f:sha(src/f) for f in ('identity.json','scene.scn','film_0.csv','film_1.csv','film_2.csv','displacement_0.csv','displacement_1.csv','displacement_2.csv')});write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
