"""Export an actually executed native scene with NEW exclusive journal paths."""
import argparse,json,hashlib,sys,xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE.parent/'tools'))
from film_guarded_process import guarded
SDK=Path('/home/ubuntu/SOFA/v26.06.00')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',required=True);p.add_argument('--run',action='store_true');a=p.parse_args();src=BASE/'results'/a.case;m=json.loads((src/'summary.json').read_text())
 if m['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('completed actual scene required,NOT grasp approval')
 if sha(src/'scene.scn')!=m['scene_sha256']:raise ValueError('immutable source scene changed')
 out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=False);(out/'records').mkdir();tree=ET.parse(src/'scene.scn');root=tree.getroot()
 names=set()
 for node in root.iter():
  if node.tag.startswith('Native') and 'filename' in node.attrib:
   name=Path(node.get('filename')).name
   if name in names:raise ValueError('journal collision would overwrite evidence:'+name)
   names.add(name);node.set('filename',str(out/'records'/name))
 tree.write(out/'scene.scn');r=dict(status='EXPORTED_FROM_ACTUAL_SCENE_NOT_GRASP_QUALIFIED',source_case=a.case,source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),source_binary_sha256=m['binary_sha256'],sdk=str(SDK),notes='ONLY journal destinations changed;full component/physical configuration retained;old Raw NEVER overwritten')
 if a.run:
  r['process']=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',m['steps'],'--hideProgressBar',out/'scene.scn'],out/'records/process',480)
  r['status']='SCENE_RUNNABLE' if r['process']['exit_code']==0 else 'FAIL'
  r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in (out/'records').rglob('*') if f.is_file()}
 (out/'identity.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
if __name__=='__main__':main()
