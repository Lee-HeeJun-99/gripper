"""Actual C2 all-pair time gates,including BOTH old sampled/new stage tendon work."""
import argparse,csv,itertools,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_time import metric
from film_three_film_qualified import require_completed
def canonical(path):
 root=ET.parse(path/'scene.scn').getroot();root.attrib.pop('dt',None)
 for node in root.iter():
  for k in ('filename','displacementFilename','ownerCostFilename','costProfileFilename','publicMassFilename'):node.attrib.pop(k,None)
  if node.tag.startswith('ThreeFilmDriven'):node.attrib.pop('maxSteps',None)
 return ET.tostring(root)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);p.add_argument('--energies',nargs=3,required=True);p.add_argument('--qualifications',nargs=3,default=['-']*3);a=p.parse_args();runs=[]
 for case,energy,qualified in zip(a.cases,a.energies,a.qualifications):
  src=ROOT/'results'/('autonomous_film_'+case);ep=ROOT/'results'/('autonomous_film_'+energy);m=json.loads((src/'identity.json').read_text());e=json.loads((ep/'summary.json').read_text());approval=require_completed(src,None if qualified=='-' else qualified)
  if e['status']!='PASS' or e['case']!=case or not m['actual_solver'].startswith('ThreeFilmDriven'):raise ValueError('completed actual driven state and matched observer required')
  for name,digest in e['raw_hashes'].items():
   if sha(src/name)!=digest:raise ValueError('observed Raw changed')
  if runs and (m['binary_sha256']!=runs[0][2]['binary_sha256'] or canonical(src)!=canonical(runs[0][1])):raise ValueError('same-DLL physical XML must match except dt/count/output paths')
  states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));inventory=list(csv.DictReader((ep/'inventory.csv').open()))
  if len(states)!=m['steps'] or len(rows)!=9*m['steps'] or len(inventory)!=m['steps']:raise ValueError('incomplete actual trajectory')
  runs.append((case,src,m,states,rows,inventory,approval,ep))
 runs.sort(key=lambda r:r[2]['steps']);pairs={}
 def forces(run):
  _,_,m,_,rows,*_=run;n=m['steps'];f=np.array([float(r['force']) for r in rows]).reshape(n,3,3);normals=np.array([[float(r[k]) for k in ('nx','ny','nz')] for r in rows]).reshape(n,3,3,3);world=f[:,:,:,None]*normals
  impulse=m['dt']*np.einsum('s,nsfd->nfd',np.array([1/6,2/3,1/6]),world)
  return f[:,-1,:],world[:,-1,:,:],impulse
 for left,right in itertools.combinations(runs,2):
  name,_,lm,lr,_,le,*_=left;other,_,rm,rr,_,re,*_=right;ratio=rm['steps']//lm['steps']
  if ratio*lm['steps']!=rm['steps']:raise ValueError('nested time grids required')
  aligned=rr[ratio-1::ratio];ae=re[ratio-1::ratio]
  if max(abs(float(x['time'])-float(y['time'])) for x,y in zip(lr,aligned))>1e-12:raise ValueError('physical sampling clock mismatch')
  energy_keys=('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation','external_work','damping_work','tendon_work','field_sampled_tendon_work')
  errors={k:metric(np.array([float(r[k]) for r in le]),np.array([float(r[k]) for r in ae])) for k in energy_keys}
  for key in ('q','v'):
   x=np.array([np.fromstring(r[key],sep=' ') for r in lr]);y=np.array([np.fromstring(r[key],sep=' ') for r in aligned]);errors['film_'+key]=metric(x[:,:-6],y[:,:-6]);center=[0,0,-63.44761697652639] if key=='q' else 0;errors['body_'+key]=metric(x[:,-6:-3]-center,y[:,-6:-3]-center)
  ln,lw,li=forces(left);rn,rw,ri=forces(right);errors['endpoint_normal_force']=metric(ln,rn[ratio-1::ratio]);errors['endpoint_world_force']=metric(lw.reshape(len(lr),-1),rw[ratio-1::ratio].reshape(len(lr),-1));errors['common_window_world_contact_force']=metric((li/lm['dt']).reshape(len(lr),-1),(ri.reshape(len(lr),ratio,3,3).sum(axis=1)/lm['dt']).reshape(len(lr),-1))
  diagnostics={k:metric(np.array([float(r[k]) for r in le]),np.array([float(r[k]) for r in ae])) for k in ('contact_work','signed_energy_residual')}
  pairs[name+'__'+other]=dict(status='PASS' if all(v['status']=='PASS' for v in errors.values()) else 'FAIL',errors=errors,defect_observations=diagnostics)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(p['status']=='PASS' for p in pairs.values()) else 'FAIL',scope='actual10ms C2 already-touching time gates for listed observables;NOT full cycle/full energy/grasp',relative_gate=.001,pairs=pairs,qualifications={r[0]:r[6] for r in runs},raw={r[0]:{f:sha(r[1]/f) for f in ('identity.json','scene.scn','summary.json','three.states.csv','three.rows.csv')} for r in runs},missing=['separated closing/impact/release','full pressure/friction/root work','mesh/self-contact/full thickness','lift/hold/grasp/12wrench'])
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],pairs={k:{n:v['relative_error'] for n,v in p['errors'].items()} for k,p in pairs.items()})))
if __name__=='__main__':main()
