"""Independent mass-scaled linearized response to ACTUAL midpoint control.

Same implicit-midpoint discretization,not a continuous-time or nonlinear reference.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,json,shutil
import numpy as np
from scipy.linalg import eigh
from curve_common import ROOT,sha,write_json
def mapping():
 index=np.full(693,-1,dtype=int);weight=np.ones(693);n=0
 for offset,ny in ((0,5),(105,3),(168,3)):
  for i in range(1,21):
   for j in range(ny):
    for d in range(3):
     if i!=1 or d!=2:index[3*(offset+i*ny+j)+d]=n;n+=1
  for j in range(ny):a=3*(offset+ny+j)+2;index[a]=index[a+3*ny];weight[a]=.25
 P=np.zeros((693,n));ids=np.flatnonzero(index>=0);P[ids,index[ids]]=weight[ids]
 return P
def shape(u):
 x=u.reshape(231,3);values={}
 for part,offset,ny,width in (('skin',0,5,24.),('left',105,3,1.322329862910148),('right',168,3,1.322329862910148)):
  p=x[offset:offset+21*ny].reshape(21,ny,3);line=p.mean(axis=1);line[:,0]+=np.linspace(0,100,21);delta=np.diff(line,axis=0);length=np.linalg.norm(delta,axis=1);unit=delta/length[:,None];turn=np.arctan2(np.cross(unit[:-1],unit[1:])[:,1],np.sum(unit[:-1]*unit[1:],axis=1));k=turn/((length[:-1]+length[1:])/2)
  values.update({part+'_tip_z':float(p[-1,:,2].mean()),part+'_mid_z':float(p[10,:,2].mean()),part+'_max_curvature_per_mm':float(np.max(abs(k))),part+'_mid_curvature_per_mm':float(k[9]),part+'_root_tip_angle_rad':float(np.arctan2(np.cross(unit[0],unit[-1])[1],np.dot(unit[0],unit[-1])))})
  cross=np.cross(unit[:-1],unit[1:]);total=np.arctan2(np.linalg.norm(cross,axis=1),np.sum(unit[:-1]*unit[1:],axis=1))/((length[:-1]+length[1:])/2)
  values.update({part+'_max_total_curvature_per_mm':float(np.max(total)),part+'_mid_total_curvature_per_mm':float(total[9]),part+'_root_tip_total_angle_rad':float(np.arctan2(np.linalg.norm(np.cross(unit[0],unit[-1])),np.dot(unit[0],unit[-1])))})
  if part=='skin':values.update(skin_centre_tip_z=float(p[-1,2,2]),skin_centre_mid_z=float(p[10,2,2]),skin_tip_width_warp_z_mm=float(np.max(p[-1,:,2])-np.min(p[-1,:,2])))
 return values
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);proof=json.loads((src/'summary.json').read_text())
 if proof['status']!='PASS' or proof['process']['exit_code']:raise ValueError('complete strict actual single-film response required')
 if proof.get('scheme','midpoint')!='midpoint':raise ValueError('this independent linear tool implements midpoint only;do not silently replace Gauss stage inputs')
 for f,digest in proof['raw_hashes'].items():
  if sha(src/f)!=digest:raise ValueError('actual/reference source changed')
 data=np.fromstring((src/'reference.linear.txt').read_text(),sep=' ');n=int(data[0]);M=data[1:1+n];force=data[1+n:1+2*n];K=data[1+2*n:].reshape(n,n);P=mapping()
 if P.shape!=(693,n) or np.min(M)<=0 or np.max(abs(K-K.T))>1e-12:raise ValueError('linear mass/stiffness/root dimensions invalid')
 inv=1/np.sqrt(M);w,V=eigh(inv[:,None]*K*inv[None,:]);
 if np.min(w)<=0:raise ValueError('linear static response requires positive tangent;no regularization')
 b=V.T@(inv*force);lift=inv[:,None]*V;y=np.zeros(n);v=np.zeros(n);rows=list(csv.DictReader((src/'actual.csv').open()));records=[];endpoint=None
 for row in rows:
  h=float(row['dt']);T=float(row['T_mid']);vm=(v-h/2*w*y+h/2*b*T)/(1+h+h*h*w/4);y+=h*vm;v=2*vm-v;q=P@(lift@y);lv=P@(lift@v);actual=np.fromstring(row['q'],sep=' ');av=np.fromstring(row['v'],sep=' ');metrics=dict(time=float(row['time']),T_mid_N=T,q_linear_actual_max_abs_mm=float(np.max(abs(q-actual))),v_linear_actual_max_abs_mm_s=float(np.max(abs(lv-av))))
  metrics.update({'actual_'+k:x for k,x in shape(actual).items()});metrics.update({'linear_'+k:x for k,x in shape(q).items()});records.append(metrics);endpoint=dict(q_relative_L2_percent=float(100*np.linalg.norm(q-actual)/np.linalg.norm(actual)) if np.linalg.norm(actual)>0 else None,v_relative_L2_percent=float(100*np.linalg.norm(lv-av)/np.linalg.norm(av)) if np.linalg.norm(av)>0 else None,**metrics)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 with (out/'response.csv').open('w') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
 static=P@(lift@(b*.0001/w));compliance=b*b/w;result=dict(status='PASS',scope='independent linearized FEM vs actual nonlinear single-film coupon;NOT time convergence or wrapping/grasp',actual_case=a.case,parent_summary_sha256=sha(src/'summary.json'),actual_binary_sha256=proof['binary_sha256'],linear_source_sha256=sha(src/'reference.linear.txt'),mass_kg=proof['mass_kg'],bond_stiffness_N_mm=proof['bond_stiffness_N_mm'],guide_offset_mm=proof['guide_offset_mm'],mode_count=n,minimum_omega_rad_s=float(np.sqrt(w[0])),maximum_omega_rad_s=float(np.sqrt(w[-1])),endpoint=endpoint,linear_static_prediction=shape(static),linear_static_scope='linearized small-strain equilibrium only;NOT nonlinear static solution/dynamic recovery time',root_reaction_work=None,actual_contact='NOT PRESENT',contact_area=None,pressure=None)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(11,8));t=np.array([r['time'] for r in records])*1000
 for ax,key in zip(axes.flat,('skin_tip_z','left_tip_z','skin_max_curvature_per_mm','left_max_curvature_per_mm')):
  ax.plot(t,[r['actual_'+key] for r in records],label='actual SOFA nonlinear');ax.plot(t,[r['linear_'+key] for r in records],'--',label='independent linearized midpoint');ax.set_xlabel('time [ms]');ax.set_ylabel(key+(' [mm]' if 'tip' in key else ' [1/mm]'));ax.legend(fontsize=7)
 fig.suptitle('Single-film transmission;NO object/contact / T_max=0.0001N per rail\n'+a.case+' / actual DLL '+proof['binary_sha256'][:12]);fig.tight_layout();fig.savefig(out/'actual_vs_linear.png',dpi=150);plt.close(fig);result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.png')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('endpoint','linear_static_prediction','raw_hashes')}));print(json.dumps(endpoint))
if __name__=='__main__':main()
