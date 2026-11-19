"""Expected-rejection regressions;these are NOT physical PASS results."""
import argparse,json,sys,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE.parent/'tools'))
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cases=[('mapped_lift',['--lift','--gravity','--object','free','--rigid-guides','--mapped-guide-joints','--global-native-ode'],'mapped-root lift'),('blocked_bridge',['--guide-bridges','--rigid-guides','--mapped-guide-joints','--global-native-ode','--steps','20'],'DiagonalMass'),('clock_without_motion',['--end-clock-motion'],'moving native fixture'),('double_damping',['--component-film-damping'],'double counting')];results=[]
 for name,flags,message in cases:
  tag=a.tag+'_'+name;process=guarded([sys.executable,BASE/'sofa/run_native.py','--tag',tag,*flags],out/name,30);error=(out/name/'stderr.log').read_text();passed=process['exit_code']!=0 and message in error and not(BASE/'results'/tag).exists();results.append(dict(test=name,status='PASS_EXPECTED_REJECTION' if passed else 'FAIL',process=process))
 (out/'summary.json').write_text(json.dumps(dict(status='PASS' if all(x['status']=='PASS_EXPECTED_REJECTION' for x in results) else 'FAIL',scope='input guards only,NO SOFA physical trial',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),tests=results),indent=2));print(json.dumps(results))
if __name__=='__main__':main()
