"""Read-only scene change and Lift/variable-stiffness scope audit."""
import argparse,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha

def normalized(path,folder):
 root=ET.parse(path).getroot()
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(folder),'CASE'))
 return root

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
 src=BASE/'results'/a.case;old=BASE/'results/b3_alarm_window485';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 before=normalized(old/'scene.scn',old);after=normalized(src/'scene.scn',src)
 bmass=before.find("./Node[@name='object']/UniformMass");amass=after.find("./Node[@name='object']/UniformMass")
 oldmass=bmass.get('vertexMass');newmass=amass.get('vertexMass');amass.set('vertexMass',oldmass)
 identical=ET.tostring(before)==ET.tostring(after)
 if not identical:raise ValueError('unexpected physical scene change beyond mass')
 initial=json.loads((old/'initial_geometry.json').read_text())
 free=[dict(name=n.get('name'),fixed_root=n.find('FixedProjectiveConstraint') is not None,movement_constraint=n.find('LinearMovementProjectiveConstraint') is not None) for n in after.findall('Node') if n.get('name','').startswith('free')]
 controls=[dict(node=n.get('name'),body=n.find('NativeCableSequence').get('body'),liftHeight=n.find('NativeCableSequence').get('liftHeight','0')) for n in after.findall('Node') if n.find('NativeCableSequence') is not None]
 result=dict(status='PASS_MASS_ONLY_SCENE_CONTRACT_NOT_PHYSICS',scene_equivalent_except_mass=identical,old_vertexMass=oldmass,new_vertexMass=newmass,initial_geometry_status=initial['status'],initial_geometry_scope=initial['scope'],fixed_root_subsets=free,controllers=controls,lift='BLOCKED_UNQUALIFIED_ROOT_PULLPOINT_COUPLING',lift_next_test='Separate no-object fixture coupon: drive only original free-subset Root indices with Native movement constraint; journal mapped Root and all PullPoints at every accepted time. Verify no unexpected direct full-film/object state write, then loaded exploratory lift with predeclared relative-slip criteria.',variable_stiffness='NOT IMPLEMENTED_IN_THIS_SCENE',variable_stiffness_basis='Single bonded Skin/Rail FEM; no vacuum/pressure/layer sliding or layer-friction state. Young modulus sensitivity would not validate jamming.',physical_validation='NOT QUALIFIED',input_hashes={str(f.relative_to(BASE)):sha(f) for f in [old/'scene.scn',src/'scene.scn',old/'initial_geometry.json',BASE/'sofa/Controller.cpp',Path(__file__)]},source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
