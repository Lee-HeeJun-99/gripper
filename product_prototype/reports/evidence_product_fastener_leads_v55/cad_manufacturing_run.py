"""Bounded executable CAD candidate,not a simulation or fabrication approval."""
import argparse,json,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'sofa'))
from native_bending_coupon import guarded
from analyse import sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--config',type=Path,default=BASE/'config/manufacturing_b3_v12.json');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 source=BASE/'cad/manufacturing_assembly.py';proc=guarded([sys.executable,source,'--name',a.name,'--config',a.config],out/'process',480);checks=BASE/'meshes'/a.name/'checks.json';complete=proc['exit_code']==0 and checks.exists()
 result=dict(status='CAD_CANDIDATE_GENERATED_NOT_QUALIFIED' if complete else 'FAIL_CAD_BUILD_PARTIAL_PRESERVED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_sha256=sha(source),producer_sha256=sha(Path(__file__)),config_sha256=sha(a.config),process=proc,meshes=str((BASE/'meshes'/a.name).relative_to(BASE.parent)),drawings=str((BASE/'drawings'/a.name).relative_to(BASE.parent)),checks_sha256=sha(checks) if complete else None,RSS_bytes=None,summary=json.loads(checks.read_text()) if complete else None)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'generator.py').write_bytes(source.read_bytes());(out/'design_config.json').write_bytes(a.config.read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='summary'},indent=2))
if __name__=='__main__':main()
