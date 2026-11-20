"""Actual Native free-ring SE(3) objectivity; never transform saved output into evidence."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha,rotation
from native_bending_coupon import guarded,flat
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_inertia_matrix_api641');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text())
 if not meta['free_reference']:raise ValueError('free-ring diagnostic only;contact geometry not transformed by this runner')
 Q=Rotation.from_rotvec([.37,-.52,.21]);A=Q.as_matrix();shift=np.array([.013,-.021,.008]);records=[]
 for variant in (0,1):
  d=out/str(variant);d.mkdir();root=ET.parse(src/str(variant)/'scene.scn').getroot()
  for item in root.iter():
   if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
   if item.tag!='MechanicalObject':continue
   q=vec(item.get('position'));rigid=item.get('template','').startswith('Rigid')
   if rigid:
    q[:3]=A@q[:3]+shift;q[3:]=(Q*Rotation.from_quat(q[3:])).as_quat();item.set('position',flat([q]))
    if item.get('velocity'):
     v=vec(item.get('velocity'));item.set('velocity',flat([np.r_[A@v[:3],A@v[3:]]]))
   else:
    item.set('position',flat(q.reshape(-1,3)@A.T+shift))
    if item.get('velocity'):item.set('velocity',flat(vec(item.get('velocity')).reshape(-1,3)@A.T))
  ET.ElementTree(root).write(d/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(meta['steps']),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));errors={}
  if proc['exit_code']==0 and '[ERROR]' not in logs:
   for i in (0,1):
    for name in (f'mass{i}.csv',f'mapped{i}_eyelet.csv'):
     old=read(src/str(variant)/name);new=read(d/name)
     if len(old)!=meta['steps'] or len(new)!=len(old):raise ValueError('incomplete transformed actual trajectory')
     for key in ('q','v'):
      errors[f'{name}:{key}']=max(float(np.max(abs(vec(y[key]).reshape(-1,3)-(vec(x[key]).reshape(-1,3)@A.T+(shift if key=='q' else 0))))) for x,y in zip(old,new))
    old=read(src/str(variant)/f'guide{i}.csv');new=read(d/f'guide{i}.csv')
    errors[f'body{i}:angular_velocity']=max(float(np.max(abs(vec(y['rigid_v'])[3:]-A@vec(x['rigid_v'])[3:]))) for x,y in zip(old,new))
    errors[f'body{i}:rotation_matrix']=max(float(np.max(abs(rotation(vec(y['rigid_q'])[3:])-A@rotation(vec(x['rigid_q'])[3:])))) for x,y in zip(old,new))
  records.append(dict(variant=variant,process=proc,scene_sha256=sha(d/'scene.scn'),errors=errors))
 passed=all(r['errors'] and max(r['errors'].values())<=1e-12 for r in records)
 result=dict(status='PASS_ACTUAL_NATIVE_FREE_SE3_OBJECTIVITY' if passed else 'FAIL_NATIVE_OBJECTIVITY',scope='Actual independently executed Native initial world rotation+translation,not postprocessed replacement trajectory. Free finite rings only,no contact/B3 qualification.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),force_binary_sha256=meta['input_binary_sha256'],rotation_matrix=A.tolist(),translation_m=shift.tolist(),dt_s=meta['dt_s'],steps=meta['steps'],records=records,gate=1e-12)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
