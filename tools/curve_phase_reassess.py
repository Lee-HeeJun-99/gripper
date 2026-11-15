"""Analyze completed actual data using the demonstrated SAME-grid comparator."""
import argparse
import json
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import OUT,sha,write_json
from curve_phase_assess import physical_xml
from curve_event_grid import analyze
from trial_validation import read_states


def main():
    p=argparse.ArgumentParser();p.add_argument('name',choices=('full_coarse_n41','full_coarse_history1250nm'));a=p.parse_args();path=OUT/a.name;target=path/'metrics_same_grid_v2.json'
    if target.exists():raise ValueError('refuse overwritten reassessment')
    old=json.loads((path/'metrics.json').read_text());c=old['config'];profile=a.name.replace('full_','profile_',1);control=OUT/(profile+'_same_grid_control');proof=json.loads((control/'summary.json').read_text())
    if old['status']!='FAIL'or old.get('execution_completed')or old['process']['exit_code']or not old.get('prefix_state_errors')or proof['status']!='PASS'or proof['same_dt']!=c['dt']:raise ValueError('only known differing-grid comparator failure may use this path')
    if float(ET.parse(control/'scene.scn').getroot().get('dt'))!=c['dt']or physical_xml(control)!=physical_xml(path):raise ValueError('same-grid actual control has different physical scene')
    before=read_states(control/'state.txt');after=[r for r in read_states(path/'state.txt')if r['time']<=.5+1e-8]
    if len(before)!=len(after):raise ValueError('actual prefix frame count')
    errors={k:float(np.max(np.abs(np.array([r[k]for r in before])-np.array([r[k]for r in after]))))for k in('X','V','R')}
    if any(errors.values()):raise ValueError('actual SAME-grid prefix still differs;do not relax exact criterion')
    result=analyze(path,c,old['process']);result.update(prefix_state_errors=errors,original_invalid_different_grid_errors=old['prefix_state_errors'],original_failed_metrics_sha256=sha(path/'metrics.json'),same_grid_control_summary_sha256=sha(control/'summary.json'),scope='Actual completed SOFA raw reanalysis,not a rerun/generated state. Original FAIL is retained;physical formulas/limits unchanged;only comparator corrected after actual same-grid control.')
    write_json(target,result);print(a.name,result['status'],result.get('bounded_hold_pass'),result.get('recovery_pass'),result.get('global_moment_residual'))


if __name__=='__main__':main()
