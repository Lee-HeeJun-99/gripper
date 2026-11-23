"""Bounded Native compliant sphere/plane with read-only actual penalty law probe.
Different physical model/input from661;NOT a correction of its impact failure.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--probe',action='store_true');p.add_argument('--reuse-build');p.add_argument('--trapezoidal',action='store_true');p.add_argument('--variational',action='store_true');p.add_argument('--default-loop',action='store_true');p.add_argument('--bdf-order',type=int,choices=(1,2));p.add_argument('--translation-only',action='store_true');p.add_argument('--newton-precise',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'sofa/native_penalty_probe';build=BASE/'cad'/('build_'+a.tag);steps=[];config=compiled=None
 if a.probe:
  if a.reuse_build:
   previous=json.loads((BASE/'results'/a.reuse_build/'summary.json').read_text());build=BASE.parent/previous['build'];binary=build/'libReGripPenaltyProbe.so'
   if sha(binary)!=previous['binary_sha256']:raise ValueError('probe binary changed')
  else:
   for n in ('Observer.cpp','CMakeLists.txt'):(out/n).write_bytes((source/n).read_bytes())
   config=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',480);compiled=guarded(['cmake','--build',build,'--parallel','1'],out/'compile',480) if config['exit_code']==0 else None
   if not compiled or compiled['exit_code']!=0:raise ValueError('penalty probe build failed;logs retained')
  binary=build/'libReGripPenaltyProbe.so'
 for dt in (.00025,.000125,.0000625):
  d=out/format(dt,'.7f');d.mkdir();root=ET.parse(BASE/'results/b3_native_plane_policy661/position_0.002500/scene.scn').getroot();root.set('dt',str(dt))
  for item in list(root):
   if item.tag in ('NativeResponseRows','NativePairRows'):root.remove(item)
  if a.default_loop:
   loop=root.find('FreeMotionAnimationLoop');loop.tag='DefaultAnimationLoop';loop.attrib.clear()
  solver=root.find('EulerImplicitSolver')
  if a.bdf_order:
   if a.trapezoidal or a.variational:raise ValueError('distinct integrators cannot be combined')
   root.insert(list(root).index(solver),ET.Element('NewtonRaphsonSolver',name='newton'));solver.tag='BDFOdeSolver';solver.set('order',str(a.bdf_order))
  elif a.variational:
   if a.trapezoidal:raise ValueError('distinct integrators cannot be combined')
   solver.tag='VariationalSymplecticSolver';solver.set('newtonError','1e-12');solver.set('steps','20');solver.set('useIncrementalPotentialEnergy','0');solver.set('computeHamiltonian','0');solver.set('saveEnergyInFile','0');solver.set('explicitIntegration','0')
  else:solver.set('trapezoidalScheme','1' if a.trapezoidal else '0')
  if a.newton_precise:
   newton=root.find('NewtonRaphsonSolver')
   if newton is None:raise ValueError('explicit Native Newton component required')
   for key,value in dict(maxNbIterationsNewton=50,relativeSuccessiveStoppingThreshold='1e-12',relativeInitialStoppingThreshold='1e-12',absoluteResidualStoppingThreshold='1e-14',maxNbIterationsLineSearch=20,updateStateWhenDiverged=0).items():newton.set(key,str(value))
  for item in root.iter():
   if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
  root.find('CollisionResponse').set('response','PenalityContactForceField');root.find('CollisionResponse').attrib.pop('responseParams',None);body=root.find("./Node[@name='sphere']/MechanicalObject");body.set('position','.001 .002 .001215 0 0 0 1');body.set('velocity','0 0 -.01 0 0 0');s=np.sqrt(100.*.0012)
  for item in root.iter():
   if item.tag in ('SphereCollisionModel','TriangleCollisionModel'):item.set('contactStiffness',format(s,'.17g'));item.set('contactFriction','0')
  if a.translation_only:
   sphere=root.find("./Node[@name='sphere']");body.set('template','Vec3d');body.set('position','.001 .002 .001215');body.set('velocity','0 0 -.01');mass=sphere.find('UniformMass');mass.attrib.clear();mass.set('template','Vec3d');mass.set('totalMass','.001');journal=sphere.find('NativeRigidJournal');journal.tag='NativePointJournal';journal.attrib.clear();journal.set('body','@frames');journal.set('filename',str(d/'state.csv'));col=sphere.find('Node');col.find('MechanicalObject').set('position','.001 .002 .001215');mapping=col.find('RigidMapping');mapping.tag='SubsetMapping';mapping.set('indices','0');root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Mapping.Linear'))
  if a.probe:root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(root,'NativePenaltyJournal',filename=str(d/'penalty.csv'))
  ET.ElementTree(root).write(d/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(round(.02/dt)),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));statefile=d/('state.csv' if a.translation_only else 'rigid.csv');rows=read(statefile) if statefile.exists() else []
  steps.append(dict(dt_s=dt,process=proc,sofa_errors=logs.count('[ERROR]'),actual_frames=len(rows),scene_sha256=sha(d/'scene.scn'),maximum_actual_buffered_penetration_m=max((.0012-float(np.fromstring(r['q' if a.translation_only else 'rigid_q'],sep=' ')[2]) for r in rows),default=None),actual_penalty_rows=len(read(d/'penalty.csv')) if a.probe and (d/'penalty.csv').exists() else None))
  if proc['exit_code']!=0 or '[ERROR]' in logs:break
 result=dict(status='RUN_COMPLETED_NOT_PHYSICALLY_QUALIFIED' if all(r['process']['exit_code']==0 and not r['sofa_errors'] and r['actual_frames']==round(.02/r['dt_s']) for r in steps) else 'FAIL_NATIVE_PENALTY',scope='Native PenalityContactForceField response,assumed100N/m,1g sphere,-.01m/s,15um initial buffer gap. No gravity,damping,friction or new solver. Not equivalent to hard impact661 or B3 product model. Stored contacts are rebuilt after force evaluation;not force callback samples.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),probe=a.probe,trapezoidal=a.trapezoidal,variational=a.variational,bdf_order=a.bdf_order,translation_only=a.translation_only,newton_precise=a.newton_precise,animation_loop='DefaultAnimationLoop' if a.default_loop else 'FreeMotionAnimationLoop',actual_response='PenalityContactForceField',build=str(build.relative_to(BASE.parent)) if a.probe else None,binary_sha256=sha(binary) if a.probe else None,configure=config,compile=compiled,records=steps,assumed_stiffness_N_per_m=100.,mass_kg=.001,initial_vz_m_s=-.01,initial_buffered_gap_m=.000015,SDK='/home/ubuntu/SOFA/v26.06.00')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
