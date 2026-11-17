"""Actual used pre-impact substates vs SAME partial midpoint force equation."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();source=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((source/'identity.json').read_text());summary=json.loads((source/'summary.json').read_text())
 if summary['status']!='PASS' or 'start_time' not in meta:raise ValueError('completed explicit initial-state case required')
 event=min((s for s in csv.DictReader((source/'coupled.event_states.csv').open()) if s['stage']=='pre'),key=lambda s:float(s['time']));start=meta['start_time'];tau=float(event['time'])-start
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for directory in ('film_coupled_contact','film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
  target=archive/'models'/directory;target.mkdir(parents=True)
  compiled=source/'sources/models'/directory
  if not compiled.is_dir():raise ValueError('actual archived model sources required:'+directory)
  for f in compiled.glob('*.h'):shutil.copy2(f,target/f.name)
 for name,digest in meta['sources'].items():
  if name.endswith('.h') and (archive/name).is_file() and sha(archive/name)!=digest:raise ValueError('actual compiled kernel header differs:'+name)
 cpp=archive/'diagnostics/film_coupled_reintegrated/EventResidual.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_coupled_reintegrated/EventResidual.cpp',cpp)
 scene=ET.parse(source/'scene.scn');field=scene.find('.//FilmRailTendon');dofs=scene.find("MechanicalObject[@name='dofs']");body=scene.find("Node[@name='free_object']/MechanicalObject");mass=scene.find('.//DiagonalMass').get('vertexMass').split();tri=scene.find('.//TriangleSetTopologyContainer').get('triangles').split();owner=scene.find('IsolatedReintegratedSphereODE')
 values=[field.get('nx'),field.get('guideIntervals','4'),field.get('guideOffset'),field.get('bondStiffness'),str(int(field.get('rootGuideSecondOrder','0') in ('true','1'))),repr(start),repr(tau),str(meta['rayleigh_mass']),str(meta['buffer_radius']),str(meta['body_mass']),str(meta['body_mass']*meta['inertia_per_mass']),' '.join(body.get('position').split()[:3]),' '.join(body.get('velocity').split()[:3]),' '.join(body.get('velocity').split()[3:]),owner.get('externalForce','0 0 0'),' '.join(field.get(k) for k in ('maximumTension','rampTime','releaseBegin','releaseEnd'))+' '+str(int(field.get('c2Control','0') in ('true','1'))),str(len(mass)),' '.join(mass),dofs.get('position'),dofs.get('velocity'),event['local_displacement'],event['local_velocity'],event['body_center'],event['body_velocity'],event['body_omega'],str(len(tri)//3),' '.join(tri)];(out/'input.txt').write_text('\n'.join(values)+'\n')
 binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.txt',out/'residual.csv'],out/'run',60) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='completed independent actual-substate residual measurement;NOT an equilibrium/time/energy gate',case=a.case,compile=compile,run=run,units=dict(momentum='N s',force_equivalent='N',position='mm'),time_reconstruction_note='tau is reconstructed from17digit absolute event clocks;kinematic errors are reported,not hidden',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},input_sha256=sha(out/'input.txt'),actual_hashes={f:sha(source/f) for f in ('identity.json','scene.scn','coupled.event_states.csv')})
 if binary.exists():result['binary_sha256']=sha(binary)
 if result['status']=='PASS':result['metrics']=next(csv.DictReader((out/'residual.csv').open()))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','metrics')}))
if __name__=='__main__':main()
