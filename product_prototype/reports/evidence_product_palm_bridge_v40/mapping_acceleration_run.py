"""Actual Native public composite-acceleration API probe with trajectory purity check."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_pair_rows,compiled_mapping_acceleration
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);buildmeta=BASE/'results/b3_mapping_build589';build=json.loads((buildmeta/'summary.json').read_text());binary=BASE.parent/build['build']/'libReGripMappingAcceleration.so';src=BASE/'results/b3_finite_com_mapped_free572';records=[];compiled_pair_rows()
 if sha(binary)!=build['binary_sha256']:raise ValueError('compiled probe binary changed')
 verified,compiled=compiled_mapping_acceleration()
 if sha(binary)!=sha(verified) or sha(buildmeta/'Observer.cpp')!=sha(compiled):raise ValueError('compiled probe identity mismatch')
 if sha(BASE/'cad/build_default_control332/libReGripProductSequence.so')!='3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0':raise ValueError('physical binary changed')
 for variant in (0,1):
  d=out/str(variant);d.mkdir();root=ET.parse(src/str(variant)/'scene.scn').getroot()
  for item in root.iter():
   if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
  # XML creates child objects in order:register observer BEFORE children use it.
  root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
  for i in (0,1):
   parent=root.find(f"./Node[@name='guide{i}']");parent.find("Node[@name='massQuadrature']/RigidMapping").set('name','massMapping');ET.SubElement(parent,'NativeMappingAcceleration',mapping='@massQuadrature/massMapping',body='@frames',points='@massQuadrature/points',filename=str(d/f'api{i}.csv'))
  ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/name).read_text(errors='replace') for name in ('stdout.log','stderr.log'));record=dict(variant=variant,process=process,scene_sha256=sha(d/'scene.scn'),sofa_errors=logs.count('[ERROR]'),status='FAIL_PROBE',observer_state_error=None)
  if process['exit_code']==0 and not record['sofa_errors']:
   error=0.;api=[]
   for i in (0,1):
    for name,keys in ((f'guide{i}.csv',('rigid_q','rigid_v','object_impulse_Ns_Nms')),(f'mapped{i}_eyelet.csv',('q','v')),(f'mass{i}.csv',('q','v'))):
     old=read(src/str(variant)/name);new=read(d/name)
     if len(old)!=4 or len(new)!=4:raise ValueError('incomplete actual states')
     for x,y in zip(old,new):
      for key in keys:error=max(error,float(np.max(abs(vec(x[key])-vec(y[key])))))
    api.extend(read(d/f'api{i}.csv'))
   if len(api)!=48:raise ValueError('incomplete temporary acceleration API records')
   returned=max(float(np.linalg.norm(vec(r['api_acceleration_m_s2']))) for r in api);expected=max(float(np.linalg.norm(vec(r['expected_centripetal_m_s2']))) for r in api);defect=max(float(np.linalg.norm(vec(r['api_acceleration_m_s2'])-vec(r['expected_centripetal_m_s2']))) for r in api);record.update(status='PASS_OBSERVER_PURITY_API_DIAGNOSTIC' if error<=1e-12 else 'FAIL_OBSERVER_PURITY',observer_state_error=error,api_records=len(api),maximum_returned_acceleration_m_s2=returned,maximum_expected_centripetal_m_s2=expected,maximum_composite_acceleration_defect_m_s2=defect)
  records.append(record)
 result=dict(status='NATIVE_COMPOSITE_ACCELERATION_PROBED' if all(r['status']=='PASS_OBSERVER_PURITY_API_DIAGNOSTIC' for r in records) else 'FAIL_PROBE',scope='Actual public API evaluated with real q/v but ZERO parent acceleration and TEMPORARY child output only. No physical state/force writes,no solver correction. Missing composite term diagnostic,not global root-cause proof for all Native solvers.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),compiled_source_sha256=sha(buildmeta/'Observer.cpp'),source_summary_sha256=sha(src/'summary.json'),sdk='/home/ubuntu/SOFA/v26.06.00',records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'Observer.cpp').write_bytes((buildmeta/'Observer.cpp').read_bytes());(out/'CMakeLists.txt').write_bytes((buildmeta/'CMakeLists.txt').read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
