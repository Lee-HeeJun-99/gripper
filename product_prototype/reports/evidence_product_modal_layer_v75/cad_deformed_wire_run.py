"""Bounded frozen-source analysis worker;identity failure is not geometry PASS."""
import argparse,json,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from native_bending_coupon import guarded
from analyse import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);p.add_argument('--radius-mm',type=float,default=2.);p.add_argument('--include-film',action='store_true');p.add_argument('--object-only-all-frames',action='store_true');p.add_argument('--all-event-worst',action='store_true');p.add_argument('--hardware-pairs',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);worker=out/'executed_worker.py';source=BASE/'cad/deformed_wire_screen.py';worker.write_bytes(source.read_bytes());deps=[source,BASE/'cad/rounded_wire_path.py',BASE/'cad/manufacturing_assembly.py',BASE/'cad/generate.py',BASE/'cad/finite_guide_product.py',BASE/'sofa/analyse.py'];before={str(p):sha(p) for p in deps}
 for n,p in enumerate(deps):(out/f'dependency_{n}_{p.name}').write_bytes(p.read_bytes())
 argv=[str(worker),'--tag',a.tag+'_analysis','--candidate',a.candidate,'--radius-mm',str(a.radius_mm)]
 if a.include_film:argv.append('--include-film')
 if a.object_only_all_frames:argv.append('--object-only-all-frames')
 if a.all_event_worst:argv.append('--all-event-worst')
 if a.hardware_pairs:argv.append('--hardware-pairs')
 code="import sys,runpy;sys.path.insert(0,sys.argv[1]);sys.argv=sys.argv[2:];runpy.run_path(sys.argv[0],run_name='__main__')"
 proc=guarded([sys.executable,'-c',code,str(BASE/'cad'),*argv],out/'process',480);after={str(p):sha(p) for p in deps};identity=before==after;detail=BASE/'results'/(a.tag+'_analysis')/'summary.json';complete=proc['exit_code']==0 and detail.exists()
 result=dict(status='BOUNDED_FROZEN_ANALYSIS_COMPLETE_NOT_PRODUCT_GATE' if complete and identity else 'FAIL_EXECUTION_OR_SOURCE_IDENTITY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),executed_worker_sha256=sha(worker),dependency_hashes_before=before,dependency_hashes_after=after,dependencies_unchanged=identity,process=proc,analysis_summary=str(detail.relative_to(BASE.parent)),analysis_sha256=sha(detail) if detail.exists() else None,analysis=json.loads(detail.read_text()) if detail.exists() else None)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('analysis','dependency_hashes_before','dependency_hashes_after')},indent=2))
if __name__=='__main__':main()
