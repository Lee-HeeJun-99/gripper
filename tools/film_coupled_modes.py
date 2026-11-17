"""Reuse frozen film FEM spectrum for an ACTUAL coupled event;not full modes."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();source=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((source/'identity.json').read_text());summary=json.loads((source/'summary.json').read_text())
 if summary['status']!='PASS':raise ValueError('completed actual coupled state required')
 snapshots=list(csv.DictReader((source/'coupled.event_states.csv').open()));pre=min((s for s in snapshots if s['stage']=='pre'),key=lambda s:float(s['time']));post=next(s for s in snapshots if s['stage']=='post' and s['time']==pre['time']);jump=[float(y)-float(x) for x,y in zip(pre['local_velocity'].split(),post['local_velocity'].split())]
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for directory in ('film_impact','film_native_contact','film_rail_tendon','film_shell','film_sphere_contact'):
  target=archive/'models'/directory;target.mkdir(parents=True)
  for f in (ROOT/'models'/directory).glob('*.h'):shutil.copy2(f,target/f.name)
 cpp=archive/'diagnostics/film_impact/ImpactModes.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_impact/ImpactModes.cpp',cpp)
 scene=ET.parse(source/'scene.scn');field=scene.find('.//FilmRailTendon');mass=scene.find('.//DiagonalMass').get('vertexMass').split();h=meta['duration']/meta['steps'];control=['PROFILE']+[field.get(k) for k in ('maximumTension','rampTime','releaseBegin','releaseEnd')]+[str(int(field.get('c2Control','0') in ('true','1')))]
 values=[field.get('nx'),field.get('guideIntervals','4'),field.get('guideOffset'),field.get('bondStiffness'),str(int(field.get('rootGuideSecondOrder','0') in ('true','1'))),repr(h),pre['time'],'0',str(len(mass)),' '.join(mass),pre['local_displacement'],' '.join(map(repr,jump)),' '.join(control)];(out/'input.txt').write_text('\n'.join(values)+'\n')
 binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.txt',out/'modes.csv',out/'nodal_gram.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent FREE-film frozen FEM spectrum from actual coupled impact;NOT constrained coupled modes/nonlinear SOFA/time certificate',case=a.case,compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},source_hashes={name:sha(source/name) for name in ('identity.json','scene.scn','coupled.event_states.csv')},input_sha256=sha(out/'input.txt'),step=h,event_time=float(pre['time']),energy_note='film-only .5 deltaV^T M deltaV,NOT physical heat;no body inertia/contact constraint spectrum implied')
 if binary.exists():result['binary_sha256']=sha(binary)
 if result['status']=='PASS':
  rows=list(csv.DictReader((out/'modes.csv').open()));total=sum(float(r['jump_metric_energy']) for r in rows);result.update(negative_modes=sum(float(r['eigenvalue'])<0 for r in rows),maximum_omega=max(float(r['omega']) for r in rows if r['omega']!='null'),jump_metric=total,participation_fractions={str(limit):sum(float(r['jump_metric_energy']) for r in rows if r['omega_dt']!='null' and float(r['omega_dt'])>limit)/total for limit in (.1,1,3.141592653589793)})
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','maximum_omega','negative_modes','participation_fractions')}))
if __name__=='__main__':main()
