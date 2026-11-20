"""Stock Native Euler/SparseLU with scoped analytic inertial force/tangent."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha,rotation
from native_bending_coupon import guarded,flat
from observer_identity import compiled_pair_rows
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build-case',default='b3_inertia_force_build623');p.add_argument('--case',default='b3_finite_com_mapped_free572');p.add_argument('--dt',type=float,choices=(.0025,.00125,.000625),default=.0025);p.add_argument('--duration',type=float,choices=(.01,.1),default=.1);p.add_argument('--trapezoidal',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;old=json.loads((src/'summary.json').read_text());buildcase=BASE/'results'/a.build_case;build=json.loads((buildcase/'summary.json').read_text());binary=BASE.parent/build['build']/'libReGripInertiaForce.so';compiled_pair_rows();steps=round(a.duration/a.dt);records=[]
 if build['status']!='BUILD_PASS' or sha(binary)!=build['binary_sha256'] or sha(buildcase/'Force.cpp')!=build['source_hashes']['Force.cpp']:raise ValueError('unverified scoped force source/binary')
 if not old.get('mapped_mass'):raise ValueError('mapped COM mass required')
 if sha(BASE/'cad/build_default_control332/libReGripProductSequence.so')!=old['physical_binary_sha256']:raise ValueError('frozen journal binary changed')
 for variant in (0,1):
  d=out/str(variant);d.mkdir();root=ET.parse(src/str(variant)/'scene.scn').getroot();root.set('dt',str(a.dt));root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));solver=root.find('SparseLDLSolver');solver.tag='EigenSparseLU';solver.attrib.pop('template',None);root.find('EulerImplicitSolver').set('trapezoidalScheme','1' if a.trapezoidal else '0')
  for item in root.iter():
   if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
  for i in (0,1):
   parent=root.find(f"./Node[@name='guide{i}']");q=vec(parent.find('MechanicalObject').get('position'));R=rotation(q[3:]);I=R.T@np.array(old['initial'][i]['world_inertia_kg_m2'])@R
   if np.min(np.linalg.eigvalsh(I))<=0:raise ValueError('invalid geometric inertia')
   ET.SubElement(parent,'NativeInertiaForce',localInertia=flat(I),filename=str(d/f'gyro{i}.csv'))
  ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));records.append(dict(variant=variant,process=process,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn')))
 metrics=[]
 if all(r['process']['exit_code']==0 and not r['sofa_errors'] for r in records):
  for i in (0,1):
   x=read(out/f'0/mapped{i}_eyelet.csv');y=read(out/f'1/mapped{i}_eyelet.csv');journal=read(out/f'0/gyro{i}.csv')
   if len(x)!=steps or len(y)!=steps:raise ValueError('partial actual states')
   fd=next(r for r in journal if r['kind']=='FD');metrics.append(dict(body=i,basis_error={n:max(float(np.max(abs(vec(u[n])-vec(v[n])))) for u,v in zip(x,y)) for n in ('q','v')},rotation_FD_relative_error=float(fd['value0']),velocity_FD_relative_error=float(fd['value1']),force_calls=sum(r['kind']=='FORCE' for r in journal),K_assembly_calls=sum(r['kind']=='K' for r in journal),B_assembly_calls=sum(r['kind']=='B' for r in journal)))
 passed=len(metrics)==2 and all(max(r['basis_error'].values())<=1e-12 and r['rotation_FD_relative_error']<=1e-7 and r['velocity_FD_relative_error']<=1e-7 and r['K_assembly_calls']>0 and r['B_assembly_calls']>0 for r in metrics)
 result=dict(status='PASS_FORCE_FD_BASIS_AND_LEGACY_ASSEMBLY_ONLY' if passed else 'FAIL_FORCE_CANDIDATE',scope='Gyroscopic force and nonsymmetric world rotation/velocity Jacobians;stock Native EulerImplicit + SparseLU,mapped mass/contact retained. Not a new ODE/contact solver or B3/global physical qualification. Assembly presence separately verified,not assumed.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),input_binary_sha256=sha(binary),compiled_source_sha256=sha(buildcase/'Force.cpp'),physical_binary_sha256=old['physical_binary_sha256'],source_summary_sha256=sha(src/'summary.json'),initial=old['initial'],assumed_mass_kg=old['assumed_mass_kg'],mapped_mass=True,free_reference=old['free_reference'],dt_s=a.dt,duration_s=a.duration,steps=steps,trapezoidal=a.trapezoidal,records=records,metrics=metrics,SDK='/home/ubuntu/SOFA/v26.06.00',physical_density=None)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='initial'},indent=2))
if __name__=='__main__':main()
