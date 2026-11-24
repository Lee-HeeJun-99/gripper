"""Capture actual small helper regressions; not new Native/product qualification."""
import argparse,io,json,subprocess,sys,time,unittest
from pathlib import Path
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);sys.path.insert(0,str(BASE/'tools'))
 names=['test_terminal_setback','test_capillary_bore','test_mechanism_sources','test_sector_route_contract','test_research_git_policy'];suite=unittest.defaultTestLoader.loadTestsFromNames(names);stream=io.StringIO();start=time.monotonic();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);runtime=time.monotonic()-start;(out/'unittest.log').write_text(stream.getvalue())
 files=[BASE/'sofa'/(n+'.py') for n in names[:-1]]+[BASE/'tools'/(names[-1]+'.py')]+[BASE/'sofa'/f for f in ('capillary_bored_support.py','capillary_guide_candidate.py','mechanism_contact_inventory.py','sector_route_feasibility.py')]+[BASE/'tools/research_git_guard.py']
 d=dict(status='PASS_SCOPED_HELPER_REGRESSIONS' if result.wasSuccessful() else 'FAIL_HELPER_REGRESSIONS',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),runtime_s=runtime,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),test_source_sha256={str(f.relative_to(BASE)):sha(f) for f in files},scope='Actual geometric/source-classification/staging-policy helper tests,not Native physical/time/mesh/material/hardware validation. Prior failed simulation verdicts unchanged.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2));raise SystemExit(not result.wasSuccessful())
if __name__=='__main__':main()
