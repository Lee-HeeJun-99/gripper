"""Native Newmark external-force vs CableConstraint force channel calibration.
Identical spring/mass/straight force direction. No FEM/contact/custom solver.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--adapter-case');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/native_force_units330';physical=BASE/'cad/build_default_control332/libReGripProductSequence.so';probe=BASE/'cad/build_b3_native_plane_force682/libReGripPenaltyProbe.so'
 if sha(physical)!='3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0' or sha(probe)!='11d942a190d96ef3b80b47a31f279308b4a17a09ae8ca5d9b15e90d23028d1d9':raise ValueError('frozen public observers changed')
 adapter_meta=None
 if a.adapter_case:
  buildcase=BASE/'results'/a.adapter_case;adapter_meta=json.loads((buildcase/'summary.json').read_text());adapter=BASE.parent/adapter_meta['build']/'libReGripNewmarkFactors.so'
  if adapter_meta['status']!='BUILD_PASS' or sha(adapter)!=adapter_meta['binary_sha256'] or sha(buildcase/'Adapter.cpp')!=adapter_meta['source_hashes']['Adapter.cpp']:raise ValueError('unverified factor adapter')
 records=[];m=.001;k=1000.;F=1.
 for channel in ('cable','external_force'):
  for h in (.00025,.000125,.0000625):
   d=out/(channel+'_'+format(h,'.7f'));d.mkdir();root=ET.parse(src/'scene.scn').getroot();root.set('dt',str(h));node=root.find("./Node[@name='coupon']");ode=node.find('EulerImplicitSolver');ode.tag='NewmarkImplicitSolver';ode.attrib.update(gamma='.5',beta='.25',rayleighMass='0',rayleighStiffness='0',vdamping='0');root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad'));root.insert(0,ET.Element('RequiredPlugin',pluginName=str(probe)))
   if a.adapter_case:root.insert(0,ET.Element('RequiredPlugin',pluginName=str(adapter)));ode.tag='ReGripNewmarkFactors'
   for item in root.iter():
    if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
    if item.tag=='RequiredPlugin' and 'libReGripProductSequence.so' in item.get('pluginName',''):item.set('pluginName',str(physical))
    if item.tag=='CableConstraint':item.set('value',format(F*h if channel=='cable' else 0.,'.17g'))
   if channel=='external_force':ET.SubElement(node,'ConstantForceField',indices='0 1',forces='0 0 1 0 0 1')
   ET.SubElement(root,'NativePenaltyJournal',point='@coupon/dofs',filename=str(d/'probe.csv'));ET.ElementTree(root).write(d/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(round(.02/h)),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));r=dict(channel=channel,dt_s=h,process=proc,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn'),frames=[],complete=False)
   if proc['exit_code']==0 and not r['sofa_errors']:
    rows=read(d/'states.csv');impulses=read(d/'constraints.csv');z=0.;v=0.;acc=F/m
    if len(rows)!=round(.02/h) or len(impulses)!=len(rows):raise ValueError('partial actual Native channel trial')
    for s,l in zip(rows,impulses):
     anew=(F-k*(z+h*v+h*h/4*acc))/(m+h*h/4*k);znew=z+h*v+h*h/4*(acc+anew);vnew=v+h/2*(acc+anew);q=vec(s['q']).reshape(-1,3);vel=vec(s['v']).reshape(-1,3);lam=vec(l['impulses_Ns']);r['frames'].append(dict(time_s=float(s['time_s']),actual_z_m=q[:,2].tolist(),actual_vz_m_s=vel[:,2].tolist(),actual_native_multipliers_Ns=lam.tolist(),independent_Newmark_force_reference_z_m=znew,independent_Newmark_force_reference_vz_m_s=vnew,state_reference_error_m=float(np.max(abs(q[:,2]-znew))),velocity_reference_error_m_s=float(np.max(abs(vel[:,2]-vnew))),multiplier_reference_error_Ns=float(np.max(abs(lam-(F*h if channel=='cable' else 0.))))));z,v,acc=znew,vnew,anew
    r.update(complete=True,maximum_position_reference_error_m=max(x['state_reference_error_m'] for x in r['frames']),maximum_velocity_reference_error_m_s=max(x['velocity_reference_error_m_s'] for x in r['frames']),maximum_multiplier_error_Ns=max(x['multiplier_reference_error_Ns'] for x in r['frames']))
   records.append(r)
   if not r['complete']:break
 result=dict(status='NATIVE_NEWMARK_FORCE_CHANNEL_DIAGNOSTIC' if len(records)==6 and all(r['complete'] for r in records) else 'FAIL_NATIVE_FORCE_CHANNEL',scope='Actual straight CableConstraint impulse channel vs identical1N ConstantForceField on1g/1000N/m points. Independent discrete Newmark gamma=.5,beta=.25 reference with physical initial acceleration F/m. NOT FEM/contact/geometry/B3/Holding qualification. Correct multiplier units alone do not prove state integration.',adapter=adapter_meta,producer_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),physical_binary_sha256=sha(physical),observer_binary_sha256=sha(probe),SDK='/home/ubuntu/SOFA/v26.06.00',mass_per_point_kg=m,stiffness_N_per_m=k,force_per_point_N=F,records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**{k:v for k,v in result.items() if k!='records'},'runs':[{k:v for k,v in r.items() if k!='frames'} for r in records]},indent=2))
if __name__=='__main__':main()
