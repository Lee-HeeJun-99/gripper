"""Read-only coupled inventory using ACTUAL labeled micro-stage dt and state."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_lateral_stage_labels1496';m=json.loads((src/'summary.json').read_text());purity=ROOT/'results/autonomous_film_20261118_lateral_stage_purity1497';pm=json.loads((purity/'summary.json').read_text())
 if m['status']!='PASS' or pm['status']!='PASS' or sha(src/'summary.json') not in pm['summaries']:raise ValueError('actual passive-label purity qualification required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual journal changed')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('actual model archive changed')
 rows=list(csv.DictReader((src/'three.rows.csv').open()));states=list(csv.DictReader((src/'three.states.csv').open()));fields=[list(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)];P=mapping();n=3*P.shape[1]+6;tokens=(src/'input.checkpoint').read_text().split();q0=np.array(tokens[5:5+n],float);v0=np.array(tokens[5+n:5+2*n],float);start=float(tokens[1]);offset=5+2*n+4;mass=np.array(tokens[offset:offset+693],float).reshape(3,231);Mb=np.array(tokens[offset+693:offset+729],float).reshape(6,6)
 if not np.array_equal(mass[0],mass[1]) or not np.array_equal(mass[0],mass[2]) or np.any(Mb-np.diag(np.diag(Mb))):raise ValueError('this observer requires identical actual film masses/isotropic diagonal body')
 if any(len(f)!=len(states) for f in fields) or len(rows)%3:raise ValueError('complete actual records required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);cpp=diag/'LateralStagePower.cpp';text=(ROOT/'diagnostics/film_three_finger/LateralStagePower.cpp').read_text();old='auto control=holdControl();'
 if text.count(old)!=1:raise ValueError('source-bound control adapter differs')
 text=text.replace(old,'auto control=regrip_transmission::control();')
 if text.count('in>>macro>>t>>w>>T;')!=1:raise ValueError('stage input adapter differs')
 cpp.write_text(text.replace('in>>macro>>t>>w>>T;','in>>macro>>t>>w;T=control.sample(t).tension;'))
 energy=diag/'ActualEnergy.cpp';shutil.copy2(ROOT/'diagnostics/film_three_finger/ActualEnergy.cpp',energy);samples=[];stages=[]
 for index in range(0,len(rows),3):
  group=rows[index:index+3];r=group[0]
  if [int(x['owner_finger']) for x in group]!=[0,1,2] or any(any(x[k]!=r[k] for k in ('time','local_macro','micro','stage','used_h_s','force_kind','stage_q','stage_v')) for x in group):raise ValueError('shared actual micro-stage identity differs')
  stage=int(r['stage']);h=float(r['used_h_s']);weight=h*(2/3 if stage==1 else 1/6);q=np.fromstring(r['stage_q'],sep=' ');v=np.fromstring(r['stage_v'],sep=' ')
  if h<=0 or stage not in (0,1,2) or r['force_kind']!=('acceleration_constraint' if stage==0 else 'collocation_stage'):raise ValueError('actual stage type/duration invalid')
  stages.append(dict(macro=int(r['local_macro']),micro=int(r['micro']),stage=stage,time=float(r['time']),h=h,weight=weight,v=v,normal_power=math.fsum(float(x['force'])*float(x['normal_velocity']) for x in group)))
  for f in range(3):samples.append((index//3,f,float(r['time']),weight,P@q[649*f:649*(f+1)],P@v[649*f:649*(f+1)]))
 scene=ET.parse(src/'scene.scn');actual_fields=list(scene.iter('FilmLateralTendon'))
 if len(actual_fields)!=3 or any(any(float(field.get(k))!=v for k,v in dict(maximumTension=.0001,rampTime=.01,releaseBegin=.02,releaseEnd=.03,lateralOffset=6).items()) or field.get('c2Control')!='1' for field in actual_fields):raise ValueError('actual common C2/lateral parameters differ')
 if not np.array_equal(np.diag(Mb),[Mb[0,0]]*3+[Mb[3,3]]*3):raise ValueError('isotropic actual body required')
 massfile=out/'public_mass.txt';massfile.write_text('231\n'+'\n'.join(' '.join(format(x,'.17g') for x in values) for values in mass)+f'\n{Mb[0,0]:.17g} {Mb[3,3]:.17g}\n')
 stagefile=out/'stages.txt';stagefile.write_text(str(len(samples))+'\n'+'\n'.join(f'{i} {t:.17g} {w:.17g} '+' '.join(format(x,'.17g') for x in q)+' '+' '.join(format(x,'.17g') for x in v) for i,f,t,w,q,v in samples)+'\n')
 endpoints=[('initial',q0,v0)]+[('end'+str(i),np.fromstring(x['q'],sep=' '),np.fromstring(x['v'],sep=' ')) for i,x in enumerate(states)];energyfile=out/'energy_samples.txt';energyfile.write_text(str(len(endpoints))+'\n'+'\n'.join(name+' '+' '.join(format(x,'.17g') for x in q)+' '+' '.join(format(x,'.17g') for x in v) for name,q,v in endpoints)+'\n')
 r=dict(status='FAIL',scope='actual labeled-micro-stage partial work/energy inventory;NOT whole energy/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),purity_sha256=sha(purity/'summary.json'),root_work=None,whole_energy='BLOCKED',heat='NOT assigned')
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'power'],out/'power_compile',120);ec=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',energy,'-o',out/'energy'],out/'energy_compile',120);run=guarded([out/'power',massfile,stagefile,out/'power.csv','.01'],out/'power_process',480) if compile['exit_code']==0 else None;er=guarded([out/'energy',massfile,energyfile,out/'energy.csv'],out/'energy_process',480) if ec['exit_code']==0 else None;r.update(power_compile=compile,energy_compile=ec,power_process=run,energy_process=er,source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if run and er and run['exit_code']==er['exit_code']==0:
  powers=list(csv.DictReader((out/'power.csv').open()));energies=list(csv.DictReader((out/'energy.csv').open()))
  if len(powers)!=len(samples) or len(energies)!=len(endpoints):raise ValueError('incomplete diagnostics')
  D=np.zeros(n);pos=offset+729
  for f in range(3):
   pairs=np.array(tokens[pos:pos+1386],float).reshape(693,2);pos+=1386
   for a,(index,weight) in enumerate(pairs):
    if index>=0:D[f*649+int(index)]+=mass[f,a//3]*weight*weight
  D[-6:]=np.diag(Mb);D=D.astype(np.longdouble);W=We=Wd=Wn=np.longdouble(0);inventory=[];previous=v0.astype(np.longdouble);dK=np.longdouble(0);U0=math.fsum(float(energies[0][k]) for k in ('U_skin','U_rails','U_attachment'));physicalError=Terror=0.;endT={}
  for i,stage in enumerate(stages):
   pp=powers[3*i:3*i+3];w=np.longdouble(stage['weight']);vv=stage['v'].astype(np.longdouble);W+=w*sum(np.longdouble(x['tendon_power_Nmm_s']) for x in pp);Wd+=w*(sum(np.longdouble(x['damping_power_Nmm_s']) for x in pp)+2*sum(D[-6:]*vv[-6:]*vv[-6:]));We+=w*(-np.longdouble(.001)*vv[-4]);Wn+=w*np.longdouble(stage['normal_power']);endT[stage['time']]=float(pp[0]['T_N'])
   if any(float(x['T_N'])!=float(pp[0]['T_N']) for x in pp):raise ValueError('shared C2 differs across fingers')
  for i,(state,e) in enumerate(zip(states,energies[1:])):
   U=math.fsum(float(e[k]) for k in ('U_skin','U_rails','U_attachment'));physicalError=max(physicalError,abs(U-sum(float(f[i]['U_shell'])+float(f[i]['U_attachment']) for f in fields)),abs(float(e['K_film'])-sum(float(f[i]['K']) for f in fields)));Terror=max(Terror,max(abs(float(f[i]['T_per_rail'])-endT[float(state['time'])]) for f in fields));vv=np.fromstring(state['v'],sep=' ').astype(np.longdouble);dK+=sum(D*(vv-previous)*(vv+previous))/2;previous=vv
  Efinal=math.fsum(float(energies[-1][k]) for k in ('U_skin','U_rails','U_attachment'));defect=np.longdouble(Efinal)-np.longdouble(U0)+dK-W-We+Wd-Wn
  r.update(status='PASS' if physicalError<=1e-12 and Terror==0 else 'FAIL',actual_energy_field_max_abs_Nmm=physicalError,actual_control_max_abs_N=Terror,start_time_s=start,end_time_s=float(states[-1]['time']),stages=len(stages),actual_used_h_sum_s=math.fsum(x['h'] for x in stages if x['stage']==0),accumulated_clock_duration_s=float(states[-1]['time'])-start,delta_stored_Nmm=Efinal-U0,delta_K_stable_Nmm=float(dK),tendon_work_Nmm=float(W),external_work_Nmm=float(We),Rayleigh_work_Nmm=float(Wd),normal_constraint_work_Nmm=float(Wn),signed_partial_defect_Nmm=float(defect),impact_loss='0 in this declared persistent-only model interval;NOT a swept absence-of-impact certificate',work_origin='actual25.2ms IVP;prior cumulative work NOT spliced',weights='ACTUAL used_h_s and stage IDs;Lobatto1/6,2/3,1/6',tension='same source-bound C++ ControlProfile evaluated at actual stage times;NOT an independently sensed tension',power_binary_sha256=sha(out/'power'),energy_binary_sha256=sha(out/'energy'))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','power_compile','energy_compile','power_process','energy_process','raw_hashes')}))
if __name__=='__main__':main()
