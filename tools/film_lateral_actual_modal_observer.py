"""Project ACTUAL nonlinear q/v into a fixed REST mass-orthogonal basis.
Coordinates/kinetic shares are observations,not nonlinear mode identification.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,json,shutil,subprocess
import numpy as np
from scipy.linalg import eigh
from curve_common import ROOT,sha,write_json
from film_transmission_linear import mapping
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();modal=ROOT/'results/autonomous_film_20261118_lateral_modal_scale1419';mm=json.loads((modal/'summary.json').read_text())
 if mm['status']!='EXPERIMENTAL' or sha(modal/'rest.linear.txt')!=mm['raw_hashes']['rest.linear.txt']:raise ValueError('complete unchanged frozen basis source required')
 data=np.fromstring((modal/'rest.linear.txt').read_text(),sep=' ');n=int(data[0]);M=data[1:1+n];b=data[1+n:1+2*n];K=data[1+2*n:].reshape(n,n);inv=1/np.sqrt(M);w,V=eigh(inv[:,None]*K*inv[None,:]);P=mapping();primary=np.array([np.flatnonzero(P[:,j]==1)[0] for j in range(n)]);lift=inv[:,None]*V;tip=P[np.arange(100,105)*3+2].mean(axis=0)@lift;bands=[w<100,(w>=100)&(w<10000),(w>=10000)&(w<1000000),w>=1000000];records=[];proofs={};maxshape=maxK=0.
 for name in ('20261118_lateral_six_hold50_1363','20261118_lateral_slow_hold50_1404'):
  src=ROOT/'results'/('autonomous_film_'+name);m=json.loads((src/'summary.json').read_text())
  if m['status']!='PASS' or m['design']!='lateral' or m['amplitude_mm']!=6 or m['raw_hashes']['public_mass.txt']!=mm['actual_mass_sha256']:raise ValueError('same actual mass/geometry full trajectory required')
  for f,d in m['raw_hashes'].items():
   if sha(src/f)!=d:raise ValueError('actual source changed')
  states=list(csv.DictReader((src/'actual.csv').open()));fields=list(csv.DictReader((src/'film_0.csv').open()));proofs[name]=sha(src/'summary.json')
  for row,field in zip(states,fields):
   if row['time']!=field['time']:raise ValueError('exact physical epoch required')
   q=np.fromstring(row['q'],sep=' ');v=np.fromstring(row['v'],sep=' ');qf=q[primary];vf=v[primary]
   if not np.array_equal(P@qf,q) or not np.array_equal(P@vf,v):raise ValueError('fixed root mapping differs from actual state')
   y=V.T@(np.sqrt(M)*qf);yd=V.T@(np.sqrt(M)*vf);tip_parts=tip*y;kin=.5*yd**2;total=float(kin.sum());actual_tip=float(q.reshape(231,3)[100:105,2].mean());maxshape=max(maxshape,abs(float(tip_parts.sum())-actual_tip));maxK=max(maxK,abs(total-float(field['K'])));r=dict(case=name,time_s=float(row['time']),ramp_s=m.get('control_ramp_s',.01),actual_T_N=float(field['T_per_rail']),actual_skin_mean_tip_z_mm=actual_tip,rest_mode0_tip_contribution_mm=float(tip_parts[0]),actual_K_Nmm=total)
   for i,band in enumerate(bands):r['rest_band'+str(i)+'_tip_mm']=float(tip_parts[band].sum());r['rest_band'+str(i)+'_kinetic_fraction']=float(kin[band].sum()/total) if total else None
   records.append(r)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 with (out/'observed.csv').open('w') as f:writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(12,8))
 for name in proofs:
  selected=[r for r in records if r['case']==name];t=[r['time_s']*1000 for r in selected];label='C2 rise'+str(int(selected[0]['ramp_s']*1000))+'ms';axes[0,0].plot(t,[r['actual_T_N'] for r in selected],label=label);axes[0,1].plot(t,[r['actual_skin_mean_tip_z_mm'] for r in selected],label=label+' actual');axes[0,1].plot(t,[r['rest_mode0_tip_contribution_mm'] for r in selected],'--',label=label+' fixed-rest-mode0 component');axes[1,0].plot(t,[r['rest_band0_tip_mm'] for r in selected],label=label+' omega<10rad/s');axes[1,1].plot(t,[np.nan if r['rest_band0_kinetic_fraction'] is None else r['rest_band0_kinetic_fraction'] for r in selected],label=label)
 for ax,title,unit in zip(axes.flat,('Actual input','Actual tip and fixed-basis component','Low-frequency fixed-basis tip sum','Actual kinetic fraction in fixed omega<10rad/s band'),('T [N/rail]','local z [mm]','local z [mm]','fraction')):ax.set(xlabel='actual physical time [ms]',ylabel=unit,title=title);ax.grid();ax.legend(fontsize=7)
 fig.suptitle('Actual nonlinear SOFA q/v projected onto fixed REST mass-orthogonal basis\nNOT instantaneous nonlinear modes,predicted completion time,contact or wrapping certification');fig.tight_layout();fig.savefig(out/'actual_fixed_basis_response.png',dpi=150);plt.close(fig);r=dict(status='EXPERIMENTAL' if maxshape<1e-12 and maxK<1e-12 else 'FAIL',scope='actual accepted nonlinear coordinates/kinetic projection into frozen basis ONLY;NOT actual nonlinear modal identification or wrapping/time certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),basis_summary_sha256=sha(modal/'summary.json'),actual_summary_hashes=proofs,actual_tip_reconstruction_error_mm=maxshape,actual_Field_kinetic_parity_error_Nmm=maxK,rest_omega_band_bounds_rad_s=[0,10,100,1000,None],potential_energy='NOT decomposed as modal quadratic energy:actual model nonlinear',endpoint=[x for x in records if x['time_s']==.05],raw_hashes={n:sha(out/n) for n in ('observed.csv','actual_fixed_basis_response.png')});write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
