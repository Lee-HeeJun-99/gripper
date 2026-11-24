"""Fail closed on unintended changes to original grasp/FEM/cable/contact inputs."""
import argparse,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def inventory(root):
 result={}
 def visit(node,path):
  result[path]=dict(node.attrib);counts={}
  for child in node:
   if child.tag=='Node':key=child.get('name')
   elif child.get('name'):key=child.tag+'['+child.get('name')+']'
   else:
    k=counts.get(child.tag,0);counts[child.tag]=k+1;key=child.tag+'#'+str(k)
   visit(child,path+'/'+key)
 visit(root,'');return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;old=BASE/'results/capillary_hold1700';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);left=inventory(ET.parse(old/'scene.scn').getroot());right=inventory(ET.parse(src/'scene.scn').getroot());changed=[];bad=[]
 normalize=lambda s:re.sub(re.escape(str(BASE/'results'))+r'/[^/ ]+',str(BASE/'results')+'/CASE',s)
 for path in sorted(set(left)|set(right)):
  x={k:normalize(v) for k,v in left.get(path,{}).items()};y={k:normalize(v) for k,v in right.get(path,{}).items()}
  if x==y:continue
  allowed=False;reason='UNEXPECTED'
  if re.fullmatch(r'/guides[012]/MechanicalObject\[frames\]',path):
   oldq=np.fromstring(x['position'],sep=' ').reshape(-1,7);q=np.fromstring(y['position'],sep=' ').reshape(-1,7);mask=np.arange(11)!=5
   allowed=q.shape==(11,7) and np.array_equal(q[mask],oldq[:11][mask]) and np.array_equal(q[5,3:],oldq[5,3:]) and {k:v for k,v in x.items() if k!='position'}=={k:v for k,v in y.items() if k!='position'};reason='Replace terminal5/11 by one COM frame; all others exact'
  elif re.fullmatch(r'/guides[012]/UniformMass#0',path):allowed=path not in right;reason='Replace original common mass by two indexed masses'
  elif re.fullmatch(r'/guides[012]/UniformMass\[(unmodifiedMass|yokeMass)\]',path):allowed=path not in left;reason='Native indexed mass contract independently tested'
  elif re.match(r'/guides[012]/dorsalYoke(?:/|$)',path):allowed=path not in left;reason='Explicit new finite rung and its collision/mapping components'
  elif re.match(r'/guides[012]/',path) and '/RigidMapping#'in path:
   expected=dict(x)
   if 'rigidIndexPerPoint'in x:expected['rigidIndexPerPoint']=' '.join('5' if k=='11' else k for k in x['rigidIndexPerPoint'].split())
   allowed=expected==y;reason='Only original owner11 becomes shared owner5'
  record=dict(path=path,changed_attributes=sorted(k for k in set(x)|set(y) if x.get(k)!=y.get(k)),allowed=bool(allowed),reason=reason);changed.append(record)
  if not allowed:bad.append(record)
 d=dict(status='PASS_DECLARED_YOKE_INPUT_CHANGES_ONLY' if not bad else 'FAIL_UNEXPECTED_GRASP_INPUT_CHANGE',case=a.case,changes=changed,unexpected=bad,source_sha256=sha(Path(__file__)),input_hashes={str(f):sha(f) for f in (old/'scene.scn',src/'scene.scn')},scope='Every scene component/attribute compared after normalizing ONLY result-output directories. Original FEM/rest, free object, six cable centre paths/commands/origins, material, gravity, friction, collision buffers, solver, support controller and plugins must be exactly unchanged. Only explicit same-finger shared frame, indexed masses and finite rung are whitelisted. Actual tensor dynamics and geometric/joint strength require separate tests.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='changes'},indent=2))
if __name__=='__main__':main()
