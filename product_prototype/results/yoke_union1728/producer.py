"""Remove original support/weld material double counting; no fitted inertia.
All geometry, feet, stiffness and commands identical to1723; only physically
new material contributes added mass, COM and parallel-axis inertia.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from finite_hardware_grasp_pilot import flat

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/dorsal_yoke1723';audit=BASE/'results/yoke_bond1725';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 d=json.loads((src/'summary.json').read_text());check=json.loads((audit/'summary.json').read_text());assert check['status']=='PASS_NEW_YOKE_MATERIAL_FEM_SEPARATION_ONLY';root=ET.parse(src/'scene.scn').getroot();old=ET.parse(BASE/'results/capillary_hold1700/scene.scn').getroot();changes=[]
 for record in check['records']:
  i=record['finger'];parent=root.find(f"Node[@name='guides{i}']");oldq=np.fromstring(old.find(f"Node[@name='guides{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7);q=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
  mb=record['added_mass_kg'];m0=1e-5;mass=2*m0+mb;cb=np.array(record['added_COM_m']);com=(m0*oldq[5,:3]+m0*oldq[11,:3]+mb*cb)/mass;inertia=np.array(record['added_inertia_COM_kg_m2'])
  for m,c,I in [(m0,oldq[5,:3],np.eye(3)*1e-11),(m0,oldq[11,:3],np.eye(3)*1e-11),(mb,cb,np.zeros((3,3)))]:
   x=c-com;inertia+=I+m*((x@x)*np.eye(3)-np.outer(x,x))
  assert np.linalg.eigvalsh(inertia).min()>0;q[5,:3]=com;parent.find('MechanicalObject').set('position',flat(q));parent.find("UniformMass[@name='yokeMass']").set('vertexMass',flat([mass,2e-8+record['added_material_volume_mm3']*1e-9,*((inertia/mass).ravel())]))
  part=d['added_parts'][i];part.update(added_mass_kg=mb,added_material_volume_mm3=record['added_material_volume_mm3'],total_yoke_and_two_guides_mass_kg=mass,COM_m=com.tolist(),inertia_kg_m2=inertia.tolist())
  for actual in d['all_parts']:
   if actual.get('part')=='dorsalYoke' and actual['finger']==i:actual.update(part)
  changes.append(dict(finger=i,mass_kg=mass,COM_m=com.tolist(),inertia_kg_m2=inertia.tolist()))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn')
 for f in ('config.json','mesh.json','holding_protocol.json'):(out/f).write_bytes((src/f).read_bytes())
 for f in src.glob('*.stl'):(out/f.name).write_bytes(f.read_bytes())
 d.update(source_sha256=sha(Path(__file__)),parent_geometry_sha256=sha(src/'summary.json'),bond_audit_sha256=sha(audit/'summary.json'),scene_sha256=sha(out/'scene.scn'),changes=changes,scope=d['scope']+' MASS UNION CORRECTION: only rung material outside original supports adds density-derived mass/inertia; initial world geometry/feet/FEM/wire path unchanged. Not a material calibration.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(status=d['status'],changes=changes),indent=2))
if __name__=='__main__':main()
