"""Read-only exact actual50→56.4ms chain and partial stage energy inventory."""
import argparse,csv,json,math,os,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();base=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';proof=ROOT/'results/autonomous_film_20261119_stationary_gauss_resume1637';pm=json.loads((proof/'summary.json').read_text());cases=[(proof/'whole',pm['trials']['whole']['raw_hashes'],sha(proof/'summary.json'))]
 for name in ('20261119_stationary_gauss_to518_1639','20261119_stationary_gauss_to534_1641','20261119_stationary_gauss_to550_1643','20261119_stationary_gauss_to564_1644'):
  folder=ROOT/'results'/('autonomous_film_'+name);m=json.loads((folder/'summary.json').read_text())
  if m['status']!='PASS' or m['binary_sha256']!=pm['binary_sha256'] or m['reference_max_abs']!={'q':0.,'v':0.} or not m['ALL_Gauss_stages_EXACT']:raise ValueError('same-binary exact actual segments required')
  cases.append((folder,m['raw_hashes'],sha(folder/'summary.json')))
 bm=json.loads((base/'summary.json').read_text());cp=base/'three.checkpoint_250.txt';tokens=cp.read_text().split();n=1953;v=np.array(tokens[5+n:5+2*n],float);time=float(tokens[1]);pos=5+2*n+4;mass=np.array(tokens[pos:pos+693],float).reshape(3,231);pos+=693;bodyM=np.array(tokens[pos:pos+36],float).reshape(6,6);pos+=36;M=[]
 for f in range(3):
  pairs=np.array(tokens[pos:pos+1386],float).reshape(693,2);pos+=1386;diag=np.zeros(649)
  for row,(index,weight) in enumerate(pairs):
   if index>=0:diag[int(index)]+=mass[f,row//3]*weight*weight
  M.append(diag)
 def fields(folder):return [list(csv.DictReader((folder/f'film_{f}.csv').open())) for f in range(3)]
 ff=fields(base);initialU=math.fsum(float(x[-1][k]) for x in ff for k in ('U_shell','U_attachment'));initialK=math.fsum(float(x[-1]['K']) for x in ff)+float(.5*v[-6:]@bodyM@v[-6:]);records=[];loss=0.;links=[];previous_cp=cp;previous_step=250;original_time=time
 if pm['status']!='PASS' or bm['status']!='PASS':raise ValueError('qualified origin and resume proof required')
 for name,digest in bm['raw_hashes'].items():
  if sha(base/name)!=digest:raise ValueError('actual initial energy/state raw changed')
 for ci,(folder,raw,summary_hash) in enumerate(cases):
  for name,digest in raw.items():
   if sha(folder/name)!=digest:raise ValueError('actual immutable raw changed')
  inp=folder/'input.checkpoint';z=inp.read_text().split();old=previous_cp.read_text().split()
  # First transition changes identity only;ALL physical/time/dt/step tokens stay.
  if ci==0:
   if z[:4]+z[5:]!=old[:4]+old[5:]:raise ValueError('initial restore physical tokens changed')
  elif sha(inp)!=sha(previous_cp):raise ValueError('typed link is not byte exact')
  links.append(dict(folder=str(folder.relative_to(ROOT)),summary_sha256=summary_hash,source_checkpoint_sha256=sha(previous_cp),input_checkpoint_sha256=sha(inp)))
  rows=list(csv.DictReader((folder/'three.states.csv').open()));stages=list(csv.DictReader((folder/'three.gauss.stages.csv').open()));ff=fields(folder)
  if len(stages)!=6*len(rows):raise ValueError('actual Gauss stage count differs')
  for i,row in enumerate(rows):
   finish=float(row['time']);h=.00005;step=previous_step+1;endv=np.fromstring(row['v'],sep=' ');q=np.fromstring(row['q'],sep=' ')
   if finish!=time+h:raise ValueError('actual accumulated clock differs')
   contribution=[]
   for f in range(3):
    if float(ff[f][i]['time'])!=finish or float(ff[f][i]['T_per_rail'])!=0:raise ValueError('actual Field clock/control differs')
    for j in range(2):
     s=stages[6*i+2*f+j];clock=time+h*(.5+(1 if j else -1)*math.sqrt(3)/6)
     if int(s['step'])!=step or int(s['finger'])!=f or int(s['stage'])!=j or float(s['time'])!=clock or float(s['weight_s'])!=h/2:raise ValueError('actual stage ownership/clock/weight differs')
     velocity=np.fromstring(s['local_v'],sep=' ');contribution.append(2*float(s['weight_s'])*float(np.dot(M[f]*velocity,velocity)))
   middle=(v[-6:]+endv[-6:])/2;contribution.append(2*h*float(middle@bodyM@middle));loss=math.fsum((loss,*contribution));U=math.fsum(float(x[i][k]) for x in ff for k in ('U_shell','U_attachment'));K=math.fsum(float(x[i]['K']) for x in ff)+float(.5*endv[-6:]@bodyM@endv[-6:]);snapshot=folder/f'three.checkpoint_{step}.txt';z=snapshot.read_text().split()
   if z[0]!='REGRIP_STATIONARY_GAUSS_FREE_V1' or float(z[1])!=finish or float(z[2])!=h or int(z[3])!=step or z[z.index('FREE_ACTIVE_COUNT')+1]!='0' or not np.array_equal(np.array(z[5:5+n],float),q) or not np.array_equal(np.array(z[5+n:5+2*n],float),endv):raise ValueError('actual accepted checkpoint identity differs')
   records.append(dict(time_s=finish,shell_attachment_stored_Nmm=U,total_K_Nmm=K,Rayleigh_loss_from50_Nmm=loss,signed_partial_defect_from50_Nmm=U-initialU+K-initialK+loss));time=finish;v=endv;previous_step=step;previous_cp=snapshot
 if len(records)!=128 or previous_step!=378:raise ValueError('complete128-step chain required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 with (out/'actual_energy.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 reference=ROOT/'results/autonomous_film_20261119_gauss_parallel_full1634';reference_meta=json.loads((reference/'summary.json').read_text())
 if sha(reference/'states.csv')!=reference_meta['raw_hashes']['states.csv']:raise ValueError('independent cumulative reference raw changed')
 ref=next(x for x in csv.DictReader((reference/'states.csv').open()) if x['substeps']=='16' and x['macro']=='8');nominal={}
 for key in ('q','v'):
  x=np.array(previous_cp.read_text().split()[5+(n if key=='v' else 0):5+(2*n if key=='v' else n)],float)[:1947];y=np.fromstring(ref[key],sep=' ')[:1947];nominal[key]=dict(max_abs=float(np.max(abs(x-y))),relative=float(np.linalg.norm(x-y)/max(np.linalg.norm(x),np.linalg.norm(y))))
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(2,1,figsize=(10,7));t=[1000*x['time_s'] for x in records]
 for key in ('shell_attachment_stored_Nmm','total_K_Nmm','Rayleigh_loss_from50_Nmm'):ax[0].plot(t,[x[key] for x in records],label=key)
 ax[1].plot(t,[x['signed_partial_defect_from50_Nmm'] for x in records],label='signed partial defect,NOT heat');ax[0].legend(fontsize=7);ax[1].legend(fontsize=7)
 for x in ax:x.set_xlabel('actual accumulated time [ms]');x.set_ylabel('[N mm]');x.grid()
 fig.suptitle('ACTUAL SOFA stationary separated Gauss50us;zero tension/load/gravity\nStage damping inventory;root work NULL;NOT whole Energy PASS');fig.tight_layout();fig.savefig(out/'actual_energy.png',dpi=160);plt.close(fig)
 r=dict(status='PASS' if max(x['relative'] for x in nominal.values())<=.001 else 'FAIL',scope='actual chain identity and partial stage inventory ONLY;NOT whole energy/time/recovery/grasp',links=links,binary_sha256=pm['binary_sha256'],start_time_s=original_time,end_time_s=time,accepted_steps=len(records),end_checkpoint=str(previous_cp.relative_to(ROOT)),initial_stored_Nmm=initialU,initial_total_K_Nmm=initialK,final_inventory=records[-1],root_work=None,contact_work_Nmm=0,tendon_work_Nmm=0,external_work_Nmm=0,zero_work_basis='all declared stages separated,zero control/force/gravity;NOT missing-data fill',heat='NOT assigned',nominal_dt_vs_aligned_reference=nominal,reference_clock_difference_s=time-float(ref['time']),clock_note='actual nominal50us accumulated clock vs independent800us aligned epochs;NOT strict bit identity between different h evaluation orders',reference_summary_sha256=sha(reference/'summary.json'),raw_hashes={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.png')});write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='links'}))
if __name__=='__main__':main()
