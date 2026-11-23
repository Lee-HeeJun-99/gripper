"""Actual accepted refined free/tied outputs;endpoint ratio is NOT static stiffness."""
import argparse,csv,json,os,subprocess,sys
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_coupon_assess import overlap
def states(case):
 src=BASE/'results'/case;m=json.loads((src/'mesh.json').read_text());q0=np.array(m['q0']);tet=np.array(m['tetrahedra']);rows=[]
 for i in (0,1):
  with (src/f'layer{i}.csv').open() as f:rows.append(list(csv.DictReader(f)))
 count=min(map(len,rows));q=np.array([[np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rr[:count]] for rr in rows]);v=np.array([[np.fromstring(r['v'],sep=' ').reshape(-1,3) for r in rr[:count]] for rr in rows]);init=np.array([q0,q0+[0,0,.000202]]);tip=np.array([np.mean(q[:,k,q0[:,0]==.04,2]-init[:,q0[:,0]==.04,2]) for k in range(count)]);time=np.array([float(r['time_s']) for r in rows[0][:count]]);lo=np.flatnonzero((q0[:,2]==.0002)&(q0[:,0]>0));gap=q[1,:,lo-1]-q[0,:,lo]-[0,0,.000002];D=(q[:,:,tet[:,1:]]-q[:,:,tet[:,0,None]]).transpose(0,1,2,4,3);D0=(q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1);w=sum(overlap(q[:,k],tet) for k in range(count));result=json.loads((src/'summary.json').read_text());complete=result['process']['exit_code']==0 and count==500
 return dict(case=case,complete_100ms=complete,accepted_outputs=count,last_time_s=float(time[-1]),final_tip_m=float(tip[-1]),last50_relative_tip_drift=float(abs(tip[-50:]-tip[-1]).max()/abs(tip[-1])),final_max_node_speed_m_s=float(np.linalg.norm(v[:,-1],axis=-1).max()),minimum_volume_ratio=float((np.linalg.det(D)/np.linalg.det(D0)).min()),maximum_interface_displacement_error_m=float(abs(gap).max()),strict_centroid_overlap_witnesses=w,equilibrium='NOT QUALIFIED',contact_force=None,root_reaction=None,whole_energy=None,input_hashes={str((src/f).relative_to(BASE)):sha(src/f) for f in ('scene.scn','preflight.json','summary.json','mesh.json','layer0.csv','layer1.csv')}),time,tip
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',120)));return
 records=[];traces=[]
 for case in ('layer_mesh_native1260','layer_refined_interface1266'):
  r,t,tip=states(case);records.append(r);traces.append((case,t,tip))
 ref=json.loads((BASE/'results/layer_interface_reference1264/summary.json').read_text());r33=next(r for r in ref['records'] if r['nx']==33);complete=all(r['complete_100ms'] for r in records);ratio=abs(records[0]['final_tip_m']/records[1]['final_tip_m']) if complete else None;d=dict(status='ACTUAL_REFINED_INTERFACE_ENDPOINT_ONLY' if complete else 'BLOCKED_INCOMPLETE_EXECUTION',records=records,accepted_endpoint_displacement_ratio_NOT_stiffness=ratio,independent_CST_ratio=r33['free_to_tied_ratio'],effective_stiffness_ratio=None,pressure_law=None,physical_validation='NOT QUALIFIED',scope='All actual Accepted State geometry,not prescribed poses. Contact forces not reconstructed from mixed bilateral/contact multipliers. No static stiffness,jamming,mesh/time/grasp qualification.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));os.environ['MPLCONFIGDIR']=str(out/'mpl_cache');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(8,4))
 for case,t,tip in traces:ax.plot(t*1000,tip*1e6,label='Actual Native '+case)
 ax.axhline(r33['free_tip_m']*1e6,color='C0',ls=':',label='Math CST free reference');ax.axhline(r33['tied_tip_m']*1e6,color='C1',ls=':',label='Math CST tied reference');ax.set(xlabel='Accepted physical time [ms]',ylabel='Width-mean tip displacement [um]',title='Refined ideal-interface diagnostic — NOT jamming qualification');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(out/'actual_native_interface.png',dpi=140);fig.savefig(out/'actual_native_interface.svg');plt.close(fig);print(json.dumps({k:v for k,v in d.items() if k!='records'}))
if __name__=='__main__':main()
