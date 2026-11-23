"""Launcher software fixtures,NOT new SOFA or physics evidence."""
import argparse,json,subprocess,sys
from pathlib import Path
from analyse import BASE,sha
from native_finite_guard import finite_guard

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];child=BASE/'sofa/finite_guard_fixture.py'
 for invalid in (False,True):
  folder=out/('NONFINITE_SOFTWARE_FIXTURE' if invalid else 'FINITE_SOFTWARE_FIXTURE');folder.mkdir();file=folder/'SOFTWARE_FIXTURE.csv';command=[sys.executable,str(child),'--output',str(file)]+(['--nonfinite'] if invalid else []);r=finite_guard(command,folder/'process',5,state_file=file);passed=(r['exit_code']!=0 and r['nonfinite_observation'].get('first_time_s')==.001 and r['runtime_s']<5) if invalid else r['exit_code']==0 and not r['nonfinite_observation'];records.append(dict(software_nonfinite_fixture=invalid,process=r,passed=passed))
 d=dict(status='PASS_LAUNCHER_SOFTWARE_FIXTURES_NOT_NATIVE' if all(r['passed'] for r in records) else 'FAIL_LAUNCHER_SOFTWARE_FIXTURES',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x):sha(x) for x in (Path(__file__),child,BASE/'sofa/native_finite_guard.py')},records=records,scope='DeliberatelygeneratedCSVfixtures testfiniteexit/nonfiniteabort ONLY. NOT SOFA states,physicsmeasurements ornewcontactresults.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
