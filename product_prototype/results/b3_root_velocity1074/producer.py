"""Read actual Root velocities,distinguish ramp interior and hold-side endpoint."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/b3_root_terminal_hold1068';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 mesh=BASE/'results/b3_alarm_window485/mesh.json';ids=np.flatnonzero(np.array(json.loads(mesh.read_text())['local_positions_mm'])[:,0]<=5);records=[];hashes={str(mesh.relative_to(BASE)):sha(mesh)}
 for f in range(3):
  path=src/f'finger{f}.csv'
  for r in csv.DictReader(path.open()):
   t=float(r['time_s']);v=np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3)[ids];expected=np.array([0,0,.01 if t<.01 else 0])
   records.append(dict(finger=f,time_s=t,expected_velocity_m_s=expected.tolist(),maximum_error_m_s=float(abs(v-expected).max())))
  hashes[str(path.relative_to(BASE))]=sha(path)
 error=max(r['maximum_error_m_s'] for r in records)
 d=dict(status='PASS_ROOT_VELOCITY_API_SCOPE_ONLY' if error<=1e-12 and len(records)==12 else 'FAIL_ROOT_VELOCITY_API',records=records,maximum_error_m_s=error,endpoint_convention='ramp interior0.01m/s;endpoint0.01s is right-side terminal hold velocity0. No smooth acceleration/work claim across slope kink.',actual_pullpoint_API='NOT MEASURED',functional_lift='NOT RUN',input_hashes=hashes,producer_sha256=sha(Path(__file__)))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
