"""Pre-snapshot bounded CAD runner;partial/failing candidates remain evidence."""
import argparse,json,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from native_bending_coupon import guarded
from analyse import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--topology',choices=['direct','tower'],required=True);a=p.parse_args()
 if any(Path(s).name!=s for s in (a.tag,a.name)):raise ValueError('unique local output names required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'cad/palm_bridge_candidate.py';worker=out/'executed_worker.py';worker.write_bytes(source.read_bytes());deps=[source,BASE/'cad/manufacturing_assembly.py',BASE/'cad/deformed_wire_screen.py'];before={str(p):sha(p) for p in deps}
 code="import sys,runpy;sys.path.insert(0,sys.argv[1]);sys.argv=sys.argv[2:];runpy.run_path(sys.argv[0],run_name='__main__')"
 proc=guarded([sys.executable,'-c',code,str(BASE/'cad'),str(worker),'--tag',a.tag+'_analysis','--name',a.name,'--topology',a.topology],out/'process',480);detail=BASE/'results'/(a.tag+'_analysis')/'summary.json';after={str(p):sha(p) for p in deps};analysis=json.loads(detail.read_text()) if detail.exists() else None;identity=before==after;complete=proc['exit_code']==0 and analysis is not None and identity
 status='FAIL_CAD_PARTIAL_OR_IDENTITY'
 if complete:status='REFERENCE_GEOMETRY_INTERSECTIONS_REMAIN' if analysis['nonempty_solid_intersections'] or analysis['wire_intersections'] else 'REFERENCE_MESH_SCREEN_CLEAR_NOT_PRODUCT_GATE'
 result=dict(status=status,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),executed_worker_sha256=sha(worker),dependency_hashes_before=before,dependency_hashes_after=after,dependencies_unchanged=identity,process=proc,analysis=analysis,analysis_summary=str(detail.relative_to(BASE.parent)),partial_CAD_output=None if complete else str((BASE/'meshes'/a.name).relative_to(BASE.parent)))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k not in ('analysis','dependency_hashes_before','dependency_hashes_after')},indent=2))
if __name__=='__main__':main()
