"""Read-only ALL-join actual-state/mass/root audit and FREE energy inventory."""
import argparse,csv,json,math,os,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def rows(path):return list(csv.DictReader(path.open()))
def checkpoint(path,n=1953):
 t=path.read_text().split();q=np.array(t[5:5+n],float);v=np.array(t[5+n:5+2*n],float);i=5+2*n;quaternion=np.array(t[i:i+4],float);i+=4;mass=np.array(t[i:i+693],float).reshape(3,231);i+=693;body=np.array(t[i:i+36],float).reshape(6,6);i+=36;maps=np.array(t[i:i+4158],float).reshape(3,693,2);diagonal=np.zeros(n)
 if t[0]!='REGRIP_ROUTED_FREE_V3' or not np.array_equal(body,np.diag(body.diagonal())) or t[-2]!='ACCUMULATED_TIME' or float(t[-1])!=float(t[1]):raise ValueError('explicit FREE diagonal projected mass/clock required')
 for f in range(3):
  for a,(index,weight) in enumerate(maps[f]):
   if index>=0:diagonal[f*649+int(index)]+=mass[f,a//3]*weight**2
 diagonal[-6:]=body.diagonal()
 if diagonal.min()<=0 or not np.isfinite(diagonal).all():raise ValueError('positive actual mass required')
 return t,q,v,quaternion,diagonal,maps
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();chain=ROOT/'results/autonomous_film_20261118_routed_free_to50_chain1396';cm=json.loads((chain/'summary.json').read_text())
 if cm['status']!='PASS':raise ValueError('complete actual chain required')
 source=ROOT/'results/autonomous_film_20261118_routed_recovery_window1393';sm=json.loads((source/'summary.json').read_text());origin=source/'three.checkpoint_158.txt';tokens,q0,v0,quat,D,maps=checkpoint(origin);tail=tokens[5+2*len(q0):-1];time=float(tokens[1]);step=int(tokens[3]);proofs={};records=[];Wt=We=Wd=0.;E0=None;maxkin=maxinput=maxrest=0.;joins=True
 def energy(fields,v):return math.fsum(float(x[k]) for x in fields for k in ('U_shell','U_attachment','K'))+.5*float(np.dot(D[-6:]*v[-6:],v[-6:]))
 initial_fields=[rows(source/f'film_{f}.csv')[-1] for f in range(3)];E0=energy(initial_fields,v0)
 for segment in cm['segments']:
  src=ROOT/'results'/('autonomous_film_'+segment['case']);m=json.loads((src/'summary.json').read_text())
  if m['status']!='PASS' or sha(src/'summary.json')!=segment['summary_sha256']:raise ValueError('changed/incomplete actual segment')
  for name,d in m['raw_hashes'].items():
   if sha(src/name)!=d:raise ValueError('actual raw changed')
  loaded,qi,vi,rotation,diagonal,root=checkpoint(src/'input.checkpoint');stages=rows(src/'three.free.stages.csv');accepted=rows(src/'three.states.csv');fields=[rows(src/f'film_{f}.csv') for f in range(3)];displacement=[rows(src/f'displacement_{f}.csv') for f in range(3)];actual=rows(src/'three.primitive.actual.csv');rest=np.fromstring(ET.parse(src/'scene.scn').find('.//TriangleSetTopologyContainer').get('position'),sep=' ').reshape(231,3)
  if len(stages)!=3*len(accepted):raise ValueError('complete FREE stage records required')
  joins=joins and float(loaded[1])==time and int(loaded[3])==step and np.array_equal(qi,q0) and np.array_equal(vi,v0) and loaded[5+2*len(q0):-1]==tail and np.array_equal(diagonal,D) and np.array_equal(root,maps) and np.array_equal(rotation,quat)
  proofs[segment['case']]=sha(src/'summary.json')
  for j,row in enumerate(accepted):
   q=np.fromstring(row['q'],sep=' ');v=np.fromstring(row['v'],sep=' ');dt=float(loaded[2]);start,mid,end=stages[3*j:3*j+3]
   if not np.array_equal(np.fromstring(start['q'],sep=' '),q0) or not np.array_equal(np.fromstring(start['v'],sep=' '),v0) or float(start['time'])!=time or float(mid['weight_s'])!=dt:raise ValueError('actual stage IVP/weight differs')
   vm=(v0+v)/2
   if not np.array_equal(np.fromstring(mid['v'],sep=' '),vm):raise ValueError('actual midpoint velocity differs')
   time+=dt;step+=1
   if float(row['time'])!=time:raise ValueError('accumulated time differs')
   saved,x,y,rotation,diagonal,root=checkpoint(src/f'three.checkpoint_{step}.txt')
   if not np.array_equal(x,q) or not np.array_equal(y,v) or saved[5+2*len(q):-1]!=tail or float(saved[1])!=time or int(saved[3])!=step:raise ValueError('actual complete checkpoint payload differs')
   if not np.array_equal(np.fromstring(actual[j]['quaternion'],sep=' '),quat) or float(actual[j]['endpoint_tension'])!=0:raise ValueError('actual rigid/control state differs')
   fvalues=[fields[f][j] for f in range(3)];tips=[];speed=[]
   for f,field in enumerate(fvalues):
    if float(field['time'])!=time or float(field['T_per_rail'])!=0:raise ValueError('actual ForceField epoch/input differs')
    u=np.fromstring(displacement[f][j]['u'],sep=' ');expanded=np.zeros(693);velocity=np.zeros(693)
    for k,(index,weight) in enumerate(maps[f]):
     if index>=0:expanded[k]=q[f*649+int(index)]*weight;velocity[k]=v[f*649+int(index)]*weight
    maxinput=max(maxinput,float(np.max(abs(u-expanded))));maxrest=max(maxrest,float(np.max(abs(np.fromstring(field['x'],sep=' ').reshape(231,3)-rest-u.reshape(231,3)))));tips.append(u.reshape(231,3)[100:105,2].mean());speed.append(float(field['max_speed']))
   Kfilm=.5*float(np.dot(D[:-6]*v[:-6],v[:-6]));maxkin=max(maxkin,abs(Kfilm-math.fsum(float(x['K']) for x in fvalues)));We+=dt*(-.001)*vm[-4];Wd+=dt*2*float(np.dot(D*vm,vm));E=energy(fvalues,v);records.append(dict(time_s=time,skin_mean_tip0_z_mm=float(tips[0]),maximum_field_speed_mm_s=max(speed),body_z_mm=float(q[-4]),body_vz_mm_s=float(v[-4]),minimum_gap_mm=float(row['minimum_gap']),stored_plus_kinetic_Nmm=E,external_work_Nmm=We,damping_work_Nmm=Wd,signed_inventory_defect_Nmm=E-E0-We+Wd));q0=q;v0=v
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 with (out/'inventory.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(3,1,figsize=(10,8));t=[x['time_s']*1000 for x in records]
 for ax,key in zip(axes,('skin_mean_tip0_z_mm','maximum_field_speed_mm_s','signed_inventory_defect_Nmm')):ax.plot(t,[x[key] for x in records]);ax.set(xlabel='actual accumulated time [ms]',ylabel=key);ax.grid()
 fig.suptitle('Actual SOFA quadratic-route FREE recovery,scale1\nZero measured tendon input;NOT completed recovery/whole energy/grasp');fig.tight_layout();fig.savefig(out/'actual_recovery_inventory.png',dpi=150);plt.close(fig)
 r=dict(status='PASS' if joins and max(maxinput,maxrest,maxkin)<1e-12 and len(records)==92 else 'FAIL',scope='read-only ALL-join/API/mass/root and signed FREE inventory;NOT whole energy/time/recovery success',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),chain_summary_sha256=sha(chain/'summary.json'),actual_summary_hashes=proofs,origin_checkpoint_sha256=sha(origin),all_join_state_time_mass_root_quaternion_identity=joins,field_input_max_abs_mm=maxinput,field_rest_reconstruction_max_abs_mm=maxrest,actual_film_kinetic_energy_error_Nmm=maxkin,endpoint=records[-1],origin_energy_Nmm=E0,tendon_work_Nmm=0.,tendon_zero_basis='all actual endpoint ForceField and primitive-owner inputs measured zero;unchanged C2 after30ms',root_reaction_work=None,contact_work='absent in explicit FREE interval;all numerical paths certified clear by actual owner',whole_energy='BLOCKED',recovery='NOT COMPLETED:residual deformation and nonzero velocity',defect_note='signed integration/measurement/roundoff/unmeasured-root defect;NOT heat',raw_hashes={n:sha(out/n) for n in ('inventory.csv','actual_recovery_inventory.png')});write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='actual_summary_hashes'}))
if __name__=='__main__':main()
