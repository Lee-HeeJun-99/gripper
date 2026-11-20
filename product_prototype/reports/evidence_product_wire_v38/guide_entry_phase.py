"""Compare observed first-row phases;do not invent common continuous event times."""
import argparse,json,itertools
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from observer_identity import compiled_pair_rows
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);binary,source=compiled_pair_rows();path=BASE/'results/b3_row_dynamics520/summary.json';meta=json.loads(path.read_text());data=meta['records'];pairs=[]
 for mode in (False,True):
  for alarm in (1,5):
   rs=[r for r in data if r['velocity_first']==mode and r['alarm_mm']==alarm]
   for x,y in itertools.combinations(rs,2):
    u=x['first_nonzero_normal_row'];v=y['first_nonzero_normal_row'];normal=float(np.linalg.norm(np.array(u['normal'])-v['normal']));gap=abs(u['detector_buffered_gap_m']-v['detector_buffered_gap_m']);pre=abs(u['previous_row_velocity_m_s'][0]-v['previous_row_velocity_m_s'][0]);postu=u['accepted_row_velocity_m_s'][0];postv=v['accepted_row_velocity_m_s'][0];absolute=abs(postu-postv);den=max(abs(postu),abs(postv));relative=absolute/den if den else 0.
    pairs.append(dict(cases=[x['case'],y['case']],alarm_mm=alarm,velocity_first=mode,normal_difference=normal,buffered_gap_difference_m=gap,previous_normal_velocity_difference_m_s=pre,discrete_entry_output_times_s=[u['time_s'],v['time_s']],discrete_step_start_times_s=[u['step_start_s'],v['step_start_s']],entry_normal_velocity_relative_difference=relative,status='PASS_SELECTED_ENTRY_VALUE' if relative<=.001 else 'FAIL_ENTRY_VALUE_NOT_FULL_TIME_GATE',same_continuous_event_time='NOT ESTABLISHED',dt_weighted_post_velocity_difference_m=abs(x['dt_s']*postu-y['dt_s']*postv)))
 result=dict(status='FAIL_FIRST_ROW_TIME_SENSITIVITY',scope='First ACTIVE row comparisons label phase mismatch explicitly. Nearly equal normal/gap/prevelocity do not prove full same q/v or continuous event time. No interpolation and no relative-error floor.',time_gate=.001,source_sha256=sha(Path(__file__)),input_sha256=sha(path),frozen_binary_sha256=sha(binary),frozen_source_sha256=sha(source),pairs=pairs,strict_observer_states_all_pass=all(r['strict_state_pass'] for r in data),maximum_detector_previous_center_error_m=max(r['detector_previous_mapped_center_max_error_m'] for r in data))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
