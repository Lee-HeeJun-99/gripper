"""Scientific plots of actual stored Native motion and source-resolved loads.
No prescribed poses,generated conceptual image,or inferred pressure/contact area.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--assessments',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);fig,ax=plt.subplots(2,2,figsize=(11,8));records=[]
 for name in a.assessments:
  assessment=BASE/'results'/name/'summary.json';verdict=json.loads(assessment.read_text());src=BASE/'results'/verdict['case'];run=json.loads((src/'summary.json').read_text());assert run['duration_s']==2.;rows=read(src/'object.csv');t=np.array([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);assert len(t)==800;dt=float(ET.parse(src/'scene.scn').getroot().get('dt'));idx={x:i for i,x in enumerate(t)};skin=np.zeros((len(t),3));support=skin.copy()
  for r in read(src/'response_rows.csv'):
   paths=(r['model0'],r['model1'])
   if not any('/object/'in x for x in paths):continue
   imp=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3]/dt;k=idx[float(r['time_s'])]
   if any('/skinCollision/'in x for x in paths):skin[k]+=imp
   if any('/floor/'in x for x in paths):support[k]+=imp
  label=verdict['case'];ax[0,0].plot(t,(q[:,2]-q[0,2])*1000,label=label);ax[0,1].plot(t,np.linalg.norm(v[:,:3],axis=1)*1000,label=label);line=ax[1,0].plot(t,skin[:,2],label=label+' Skin')[0];ax[1,0].plot(t,support[:,2],'--',color=line.get_color(),label=label+' Support');ax[1,1].plot(q[:,0]*1000,q[:,1]*1000,label=label)
  records.append(dict(case=label,status=verdict['status'],slip_mm=verdict['slip_mm'],max_speed_mm_s=verdict['maximum_speed_mm_s'],force_partition=verdict['force_partition'],assessment_sha256=sha(assessment),object_sha256=sha(src/'object.csv'),response_sha256=sha(src/'response_rows.csv')))
 for axis in ax.flat:axis.grid(True,alpha=.3);axis.legend(fontsize=6)
 for axis in (ax[0,0],ax[0,1],ax[1,0]):axis.axvspan(1.6,2.,alpha=.08,color='green');axis.set_xlabel('Actual simulation time (s)')
 ax[0,0].set_ylabel('Object height relative first output (mm)');ax[0,1].set_ylabel('Object linear speed (mm/s)');ax[0,1].set_yscale('symlog',linthresh=5);ax[0,1].axhline(5,color='black',lw=.5);ax[1,0].set_ylabel('Actual vertical contact force (N)');ax[1,0].axhline(.981,color='black',lw=.5);ax[1,1].set_xlabel('Object x (mm)');ax[1,1].set_ylabel('Object y (mm)');ax[1,1].set_aspect('equal',adjustable='datalim');fig.suptitle('Actual Native 100g trials;NOT time/mesh/physical qualification');fig.tight_layout();fig.savefig(out/'native_motion_and_support.png',dpi=170);plt.close(fig);d=dict(status='ACTUAL_STORED_STATE_COMPARISON_ONLY',records=records,source_sha256=sha(Path(__file__)),scope='Goal thresholds unchanged;no reclassification,contact area/pressure,or extrapolated state');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
