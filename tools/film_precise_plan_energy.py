"""Stage-consistent cumulative work and ALL common-time partial energy inventory."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_precise_startup_energy import CPP
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--plan-case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.plan_case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='COMPLETED_NOT_QUALIFIED':raise ValueError('complete independent candidate required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('immutable raw mismatch')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/StageEnergy.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(CPP.replace('film_precise_attachment/Force.h','film_precise_tendon/Force.h').replace('regrip_precise_attachment::parts','regrip_precise_tendon::parts'))
 r=dict(status='FAIL',scope='independent solver-plan ALL common public-clock partial energy/work inventory;NOT actual SOFA or whole physical energy certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},root_reaction_work=None,external_work=0,contact_work=0,impact_loss=0,relative_gate=.001,absolute_floor='NONE',trials={})
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120);journals={}
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'observer')
  for count in (40,80,160):
   folder=out/str(count);folder.mkdir();stages=list(csv.DictReader((src/str(count)/'state.csv.stages.csv').open()));states=list(csv.DictReader((src/str(count)/'state.csv').open()));samples=[(x['T'],x['q'],x['v']) for x in stages]+[('0',x['q'],x['v']) for x in states];(folder/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(' '.join(x) for x in samples)+'\n');run=guarded([out/'observer',src/'public_mass.txt',folder/'samples.txt'],folder/'process',180);trial=dict(process=run,status='FAIL');r['trials'][str(count)]=trial
   if run['exit_code']!=0:continue
   values=list(csv.DictReader((folder/'process/stdout.log').open()));force=max(float(np.max(abs(np.fromstring(x['reduced_force'],sep=' ')-np.fromstring(y['reduced_physical_force_N'],sep=' ')))) for x,y in zip(values,stages));work=np.longdouble(0);damping=np.longdouble(0);index=0;rows=[]
   for macro,state in enumerate(states,1):
    while index<len(stages) and int(stages[index]['macro'])==macro:
     weight=np.longdouble(stages[index]['weight_s']);work+=weight*np.longdouble(values[index]['tendon_power_Nmm_s']);damping+=weight*np.longdouble(values[index]['damping_power_Nmm_s']);index+=1
    e=values[len(stages)+macro-1];u=sum(np.longdouble(e[k]) for k in ('U_skin','U_rails','U_attachment'));kinetic=np.longdouble(e['K']);rows.append(dict(time=float(state['time']),W=float(work),D=float(damping),U_skin=float(e['U_skin']),U_rails=float(e['U_rails']),U_attachment=float(e['U_attachment']),K=float(kinetic),signed_partial_defect=float(work-damping-u-kinetic)))
   with (folder/'energy.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
   journals[count]=rows;trial.update(status='PASS' if force==0 and len(values)==len(samples) else 'FAIL',stage_force_max_abs_N=force,number_of_stages=len(stages),endpoint=rows[-1])
  if len(journals)==3 and all(x['status']=='PASS' for x in r['trials'].values()):
   errors=[]
   for lo,hi in ((40,80),(80,160),(40,160)):
    times=np.array([x['time'] for x in journals[hi]])
    for row in journals[lo]:
     t=row['time'];j=int(np.argmin(abs(times-t)));nearest=times[j];other=journals[hi][j]
     if nearest!=t:
      right=int(np.searchsorted(times,t));left=right-1
      if left<0 or right>=len(times):raise ValueError('energy interpolation extrapolation rejected')
      alpha=(t-times[left])/(times[right]-times[left]);other={k:(1-alpha)*journals[hi][left][k]+alpha*journals[hi][right][k] for k in row}
     for k in row:
      if k=='time':continue
      absolute=abs(row[k]-other[k]);scale=max(abs(row[k]),abs(other[k]));relative=absolute/scale if scale else None;errors.append(dict(pair=str(lo)+'_'+str(hi),time=t,quantity=k,absolute=absolute,relative=relative,nearest_clock_distance_s=abs(nearest-t),status='EXACT_ZERO' if not scale and not absolute else 'PASS' if relative is not None and relative<=.001 else 'FAIL'))
   with (out/'errors.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(errors[0]));w.writeheader();w.writerows(errors)
   r.update(status='FAIL' if any(x['status']=='FAIL' for x in errors) else 'PASS',force_observer='PASS',worst=max((x for x in errors if x['relative'] is not None),key=lambda x:x['relative']),number_of_compared_observables=len(errors),interpretation='Signed numerical defect is NOT physical heat;root work remains NULL;only partial inventory',clock_matching='fine scalar journal linear interpolation;raw clocks/states preserved;continuum interpolation error NOT bounded')
 r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in out.rglob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','trials','compile')}))
if __name__=='__main__':main()
