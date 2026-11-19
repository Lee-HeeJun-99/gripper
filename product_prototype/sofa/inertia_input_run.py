"""Native existing ODE + analytically sampled inertia input;no q/v correction."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_pair_rows
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_finite_com_mapped_free572');p.add_argument('--dt',type=float,choices=(.0025,.00125,.000625),default=.0025);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;old=json.loads((src/'summary.json').read_text());buildcase=BASE/'results/b3_inertia_input_build592';build=json.loads((buildcase/'summary.json').read_text());binary=BASE.parent/build['build']/'libReGripInertiaInput.so';records=[];compiled_pair_rows();steps=round(.01/a.dt)
 if sha(binary)!='0e9d7336992942af5a0606e72323155335ced9f1eac3d9c540b8fe31cf3009b7' or sha(buildcase/'Observer.cpp')!='f590fac8ec3cdc755597382badf8759352ccd22effbf2d096a0eeb59b3f3318e':raise ValueError('unverified input source/binary')
 if not old.get('mapped_mass'):raise ValueError('requires mapped geometric mass;no frozen/old lumped mass allowed')
 if sha(BASE/'cad/build_default_control332/libReGripProductSequence.so')!=old['physical_binary_sha256']:raise ValueError('physical journal binary changed')
 for variant in (0,1):
  d=out/str(variant);d.mkdir();root=ET.parse(src/str(variant)/'scene.scn').getroot();root.set('dt',str(a.dt));root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad'))
  for item in root.iter():
   if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
  for i in (0,1):
   parent=root.find(f"./Node[@name='guide{i}']");ET.SubElement(parent,'ConstantForceField',name='inertiaInput',template='Rigid3d',indices='0',forces='0 0 0 0 0 0');ET.SubElement(parent,'NativeInertiaInput',body='@frames',points='@massQuadrature/points',force='@inertiaInput',mass=str(old['assumed_mass_kg']),filename=str(d/f'inertia_input{i}.csv'))
  ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));records.append(dict(variant=variant,process=process,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn')))
 metrics=[]
 if all(r['process']['exit_code']==0 and not r['sofa_errors'] for r in records):
  for i in (0,1):
   x=read(out/f'0/mapped{i}_eyelet.csv');y=read(out/f'1/mapped{i}_eyelet.csv');inputs=read(out/f'0/inertia_input{i}.csv')
   if len(x)!=steps or len(y)!=steps or len(inputs)!=steps:raise ValueError('incomplete Native state/input')
   error={key:max(float(np.max(abs(vec(u[key])-vec(v[key])))) for u,v in zip(x,y)) for key in ('q','v')};metrics.append(dict(body=i,basis_error=error,maximum_input_power_W=max(abs(float(r['power_W'])) for r in inputs),maximum_input_torque_Nm=max(float(np.linalg.norm(vec(r['applied_torque_Nm']))) for r in inputs)))
 result=dict(status='PASS_BASIS_API_ONLY' if len(metrics)==2 and max(v for r in metrics for v in r['basis_error'].values())<=1e-12 else 'FAIL_NATIVE_INPUT',scope='Sampled gyroscopic inertia torque=-omega cross Iworld*omega at AnimateBegin through Native ConstantForceField. Native EulerImplicit/mapped mass/contact unchanged;NO implicit gyro Jacobian,not a production physical qualification. No state reset,new ODE/contact solver or B3 adoption.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),input_binary_sha256=sha(binary),compiled_source_sha256=sha(buildcase/'Observer.cpp'),physical_binary_sha256=old['physical_binary_sha256'],source_summary_sha256=sha(src/'summary.json'),initial=old['initial'],assumed_mass_kg=old['assumed_mass_kg'],mapped_mass=True,free_reference=old['free_reference'],dt_s=a.dt,steps=steps,records=records,metrics=metrics,SDK='/home/ubuntu/SOFA/v26.06.00',physical_density=None)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='initial'},indent=2))
if __name__=='__main__':main()
