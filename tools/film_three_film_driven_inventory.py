"""Stored energy on completed independent C2 FEM states,not full work balance."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reuse');p.add_argument('--mass-case',default='20261118_three_film_actual_c2_887');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);s=json.loads((src/'summary.json').read_text());masssrc=ROOT/'results'/('autonomous_film_'+a.mass_case);m=json.loads((masssrc/'identity.json').read_text())
 if s['status']!='PASS' or s.get('adaptive_gap_control',False) or json.loads((masssrc/'summary.json').read_text())['status']!='PASS':raise ValueError('completed uniform independent C2 and qualified actual mass source required')
 for name in ('models/film_three_finger/FrameLayout.h','models/film_rail_tendon/Kernel.h','models/film_shell/Kernel.h'):
  if s['sources'][name]!=m['sources'][name]:raise ValueError('mass/material geometry kernel mismatch:'+name)
 rows=list(csv.DictReader((src/'states.csv').open()))
 if len(rows)!=s['steps']:raise ValueError('partial run')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/ActualEnergy.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/ActualEnergy.cpp',cpp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 scene=ET.parse(masssrc/'scene.scn');masses=[np.fromstring(scene.find('Node[@name="finger'+str(f)+'"]//DiagonalMass').get('vertexMass'),sep=' ') for f in range(3)];rigid=np.fromstring(scene.find('Node[@name="free_object"]//UniformMass').get('vertexMass'),sep=' ')
 with (out/'mass.txt').open('w') as stream:stream.write(str(len(masses[0]))+'\n'+'\n'.join(' '.join(format(x,'.17g') for x in mass) for mass in masses)+'\n'+format(rigid[0],'.17g')+' '+format(rigid[0]*rigid[2],'.17g')+'\n')
 with (out/'samples.txt').open('w') as stream:stream.write(str(len(rows))+'\n'+'\n'.join('end'+str(i)+' '+r['q']+' '+r['v'] for i,r in enumerate(rows))+'\n')
 binary=out/'reference'
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prior/'summary.json').read_text());binary=prior/'reference'
  if old['status']!='PASS' or sha(binary)!=old['binary_sha256'] or any(sources.get(k)!=v for k,v in old['sources'].items() if k.endswith('.h') or k.endswith('/ActualEnergy.cpp')):raise ValueError('compiled observer headers/ActualEnergy.cpp identity mismatch;unlinked model CPP excluded')
  compile=dict(exit_code=0,reused=a.reuse)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent FEM C2 accepted-state separated stored/kinetic energy;NOT actual SOFA/full work certificate',case=a.case,sources=sources,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),compile=compile,run=run,mass_source=a.mass_case,mass_scene_sha256=sha(masssrc/'scene.scn'),raw_sha256=sha(src/'states.csv'))
 if run and run['exit_code']==0:
  observed=list(csv.DictReader((out/'observed.csv').open()))
  if len(observed)!=len(rows):raise ValueError('incomplete observer')
  if not all(np.isfinite(float(v)) for row in observed for k,v in row.items() if k!='sample'):raise ValueError('nonfinite energy inventory')
  with (out/'inventory.csv').open('w') as stream:
   w=csv.DictWriter(stream,fieldnames=['time',*observed[0]]);w.writeheader();w.writerows(dict(time=r['time'],**value) for r,value in zip(rows,observed))
  result['binary_sha256']=sha(binary);result['inventory_sha256']=sha(out/'inventory.csv')
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','run')}))
if __name__=='__main__':main()
