"""Installed Native VTKExporter reads actual initialized mapped positions.

No-contact one-step diagnostic;exportAtBegin reads initial state. Never sets q/v.
"""
import argparse,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from b3_contact_layer_native import add

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_contact_layer_pilot1337';tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.IO.Mesh'));root.remove(root.find('CollisionPipeline'))
 for i in range(3):
  n=root.find(f"Node[@name='contactLayer{i}']");add(n,'VTKExporter',name='initialReadOnlyExport',filename=out/f'layer{i}',position='@dofs.position',fileFormat=0,exportAtBegin=1,exportAtEnd=0,exportEveryNumberOfSteps=0,writeTetras=1,overwrite=1)
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',str(out/'scene.scn')]
 pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),SDK='/home/ubuntu/SOFA/v26.06.00',component='installed Native VTKExporter at exportAtBegin;one no-contact step,not zero-step batch which can animate',steps=1,child_limit_s=30,memory_GiB=4);(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',30);g=json.loads((BASE/'results/b3_contact_layer_geometry1336/mesh.json').read_text());records=[]
 for i in range(3):
  paths=list(out.glob(f'layer{i}*.vtk'))
  if not paths:continue
  tokens=paths[0].read_text().split();k=tokens.index('POINTS');n=int(tokens[k+1]);q=np.array([float(x) for x in tokens[k+3:k+3+3*n]]).reshape(-1,3);expected=np.array(g['world_reference_m'][i]);records.append(dict(finger=i,points=n,maximum_position_error_m=float(abs(q-expected).max()),actual_bbox=[q.min(axis=0).tolist(),q.max(axis=0).tolist()],file_sha256=sha(paths[0])))
 d=dict(status='PASS_INITIAL_POSITIONS_ONLY' if proc['exit_code']==0 and len(records)==3 and max(r['maximum_position_error_m'] for r in records)<=1e-12 else 'FAIL_INITIAL_EXPORT',process=proc,records=records,physical_validation='NOT QUALIFIED',scope='Native exportAtBegin coordinates;one no-contact step,not force/contact validation. Export text precision can limit identity assessment.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
