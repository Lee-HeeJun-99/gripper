"""Record observed outer-timeout/nonfinite failure WITHOUT inventing runtime or states."""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in ('product_root_native_strict815','product_root_native_strict816'):
  folder=BASE/'results'/case
  if (folder/'summary.json').exists():raise ValueError('do not overwrite raw result')
  rows=list(csv.DictReader((folder/'wheel.csv').open()));bad=[float(r['time_s']) for r in rows if not np.isfinite(np.fromstring(r['rigid_q']+' '+r['rigid_v'],sep=' ')).all()]
  if not bad:raise ValueError('no observed nonfinite state')
  d=dict(status='FAIL_NONFINITE_OUTER_TIMEOUT_PARTIAL_RAW',source_commit='2a81fb044200531e52ba51ac2f9fca946b6c7888',executed_producer_sha256=sha(folder/'producer.py'),scene_sha256=sha(folder/'scene.scn'),observed_outer_exit_code=124,outer_timeout_seconds=480,actual_runtime_s=None,state_rows=len(rows),first_nonfinite_state_time_s=min(bad),internal_process_result_exists=(folder/'process/result.json').exists(),input_hashes={f.name:sha(f) for f in folder.iterdir() if f.is_file()},scope='Originalcommandusedoutertimeout480andinnerguard480;outerterminatedbeforeinnerfinalization. RuntimeNULL,notinvented. Partial43statesincludeNaNat10.75ms;NOT80completedstates. HostprocesschecklaterfoundbothtrialPIDsgone;requestedkillreturnedNoSuchProcess. No source/state/force/SDKrepair. FuturefiniteguardmuststopownchildonNaNandfinishbeforeouterdeadline.',fabrication_ready=False)
  (folder/'summary.json').write_text(json.dumps(d,indent=2));records.append(dict(case=case,summary_sha256=sha(folder/'summary.json'),first_nonfinite_state_time_s=min(bad)))
 result=dict(status='FAILED_RUN_METADATA_FINALIZED_NOT_SIMULATION_PASS',records=records,producer_sha256=sha(Path(__file__)),scope='Retrospectivefailuremetadataonly,originalscenes/journals/producerpreserved.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
