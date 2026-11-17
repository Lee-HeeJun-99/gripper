"""Strict actual persistent transfer;immutable Campaign1002 is the continuous control.
Checkpoint legacy sampled-work is explicitly NOT restored. No physical work offset.
"""
import argparse,csv,json,shutil,subprocess,hashlib,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK

def mapping():
 index=np.full(693,-1,dtype=int);weight=np.ones(693);n=0
 for offset,ny in ((0,5),(105,3),(168,3)):
  for i in range(1,21):
   for j in range(ny):
    for d in range(3):
     if i!=1 or d!=2:index[3*(offset+i*ny+j)+d]=n;n+=int(i!=1 or d!=2)
 for offset,ny in ((0,5),(105,3),(168,3)):
  for j in range(ny):
   a=3*(offset+ny+j)+2;index[a]=index[a+3*ny];weight[a]=.25
 assert n==649
 return index,weight

def export_checkpoint(src,out,step,token):
 states=list(csv.DictReader((src/'three.states.csv').open()));state=states[step-1]
 q=np.fromstring(state['q'],sep=' ');v=np.fromstring(state['v'],sep=' ')
 # Campaign1002 has no spin or rotation increment at ANY preceding step.
 # Refuse unsupported historical reconstruction rather than invent quaternion.
 if any(np.any(np.fromstring(r[k],sep=' ')[-3:]!=0) for r in states[:step] for k in ('q','v')):raise ValueError('historical quaternion not independently recoverable')
 scene=ET.parse(src/'scene.scn');body=scene.find(".//Node[@name='free_object']/MechanicalObject");quat=np.fromstring(body.get('position'),sep=' ')[3:]
 mass=np.fromstring((src/'public_mass_reference.txt').read_text(),sep=' ');assert int(mass[0])==231 and len(mass)==696
 mb=np.diag([mass[-2]]*3+[mass[-1]]*3).ravel();index,weight=mapping()
 rows=[r for r in csv.DictReader((src/'three.rows.csv').open()) if float(r['time'])==float(state['time'])][-3:]
 if len(rows)!=3 or [int(r['owner_finger']) for r in rows]!=[0,1,2]:raise ValueError('missing accepted owned rows')
 text=['REGRIP_PERSISTENT_V1 '+state['time']+' .0002 '+str(step),token]
 text += [' '.join(format(x,'.17g') for x in z) for z in (q,v,quat,mass[1:-2],mb)]
 text += [' '.join(str(int(i))+' '+format(w,'.17g') for i,w in zip(index,weight))]*3
 text += [r['triangle']+' '+r['feature'] for r in rows]
 (out/'input.checkpoint').write_text('\n'.join(text)+'\n')
 return states,state

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--step',type=int,default=40);p.add_argument('--steps',type=int,default=4);a=p.parse_args()
 if not 1<=a.step<50 or not 1<=a.steps<=4 or a.step+a.steps>50:raise ValueError('initial regression only2–4 saved steps')
 src=ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002';sm=json.loads((src/'summary.json').read_text())
 for n,h in sm['raw_hashes'].items():
  if sha(src/n)!=h:raise ValueError('continuous raw changed:'+n)
 for n,h in sm['plugins'].items():
  if sha(n)!=h:raise ValueError('continuous binary changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 build=ROOT/'build'/('three_film_resume_'+a.tag);build.mkdir(exist_ok=False)
 configure=guarded(['cmake','-S',archive/'models/film_three_finger_resume','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
 compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 result=dict(status='FAIL',scope='actual persistent checkpoint transfer,NOT hold/release/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,sdk=str(SDK),configure=configure,compile=compile,legacy_sampled_work='NEW ORIGIN;private previousLength/T NOT restored;exclude from continuous-work claim',stage_work_origin='checkpoint physical time;prior evidence Campaign1011 and1007 retained separately',steps=a.steps,checkpoint_step=a.step)
 write_json(out/'summary.json',result)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmResume.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in s and '=> /' in s and str(SDK) not in s for s in deps.splitlines()):raise ValueError('resume SDK ABI mismatch')
  result['binary_sha256']=sha(binary);token=hashlib.sha256(json.dumps(dict(source=sources,binary=sha(binary),continuous=sha(src/'summary.json')),sort_keys=True).encode()).hexdigest();states,state=export_checkpoint(src,out,a.step,token)
  tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.set('time',state['time'])
  for node in scene.iter():
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmEvent.so'):node.set('pluginName',str(binary))
  owner=scene.find('ThreeFilmFirstPeakODE');owner.tag='ThreeFilmResumeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',token);owner.set('endTime','.01');owner.set('maxSteps','64');tree.write(out/'scene.scn')
  result.update(identity=token,checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'),continuous_summary_sha256=sha(src/'summary.json'),predicted_runtime_s=2*sm['process']['runtime_s']*a.steps/50+30)
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);result['process']=run;result['sofa_errors']=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'))
  if run['exit_code']==0 and not result['sofa_errors']:
   actual=list(csv.DictReader((out/'three.states.csv').open()));expected=states[a.step:a.step+a.steps]
   if len(actual)!=a.steps:raise ValueError('incomplete actual resume')
   errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};clock=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(actual,expected));rows=list(csv.DictReader((out/'three.rows.csv').open()));expected_rows=list(csv.DictReader((src/'three.rows.csv').open()))[(a.step-1)*9:(a.step+a.steps-1)*9]
   exact_rows=rows==expected_rows
   field_errors={}
   for f in range(3):
    aa=list(csv.DictReader((out/f'film_{f}.csv').open()));ee=list(csv.DictReader((src/f'film_{f}.csv').open()))[a.step:a.step+a.steps]
    field_errors[str(f)]={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(aa,ee)) for k in ee[0] if k!='tendon_work'}
   max_field=max(z for f in field_errors.values() for z in f.values());gap=min(float(r['minimum_gap']) for r in actual);momentum=max(float(r['momentum_residual']) for r in actual);vn=max(float(r['normal_velocity_residual']) for r in actual)
   result.update(status='PASS' if max(errors.values())<1e-12 and clock==0 and exact_rows and max_field<1e-12 and gap>=-1e-10 and momentum<=1e-17 and vn<=1e-10 else 'FAIL',reference_max_abs=errors,clock_max_abs_s=clock,stage_rows_byte_value_exact=exact_rows,field_errors=field_errors,minimum_gap_mm=gap,momentum_max_Ns=momentum,normal_velocity_max_mm_s=vn,absolute_api_gate=1e-12)
  result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')}
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','reference_max_abs','clock_max_abs_s','stage_rows_byte_value_exact','process','sofa_errors','compile') if k in result}))
if __name__=='__main__':main()
