"""Reconstruct ONE rejected step using archived compiled-model header sources.

This is independent mathematical replay, not an accepted SOFA trajectory.
"""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
from film_guarded_process import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--release-active-set',action='store_true');p.add_argument('--sqp-merit',action='store_true');mode=p.add_mutually_exclusive_group();mode.add_argument('--solve',action='store_true');mode.add_argument('--free-newton',action='store_true');p.add_argument('--step-reference',type=float);a=p.parse_args()
    if a.release_active_set and not a.solve:raise ValueError('release-active-set is a nonlinear solve variant')
    source=ROOT/'results'/('autonomous_film_'+a.case)
    trial=json.loads((source/'summary.json').read_text())
    if trial['status']!='FAIL':raise ValueError('explicit failed trajectory required')
    trace=source/'1/coupled.csv.newton.log'
    if 'SPHERE_FAILURE_V2 ' not in trace.read_text():raise ValueError('failure has no exact-state dump;do not invent a replay')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    for name in ('film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
        shutil.copytree(source/'sources'/name,out/'sources/models'/name)
    if a.release_active_set or a.sqp_merit or a.step_reference is not None:
        shutil.copyfile(ROOT/'models/film_sphere_contact/SphereStep.h',out/'sources/models/film_sphere_contact/SphereStep.h')
    diagnostic=out/'sources/diagnostics/film_sphere_contact/Replay.cpp';diagnostic.parent.mkdir(parents=True)
    shutil.copyfile(ROOT/'diagnostics/film_sphere_contact/Replay.cpp',diagnostic)
    stages={};stages['compile']=logged(['g++','-std=c++17','-O2','-ffp-contract=off','-I/usr/include/eigen3']+(['-DREGRIP_RELEASE_ACTIVE_SET'] if a.release_active_set else [])+(['-DREGRIP_SQP_MERIT'] if a.sqp_merit else [])+[diagnostic,'-o',out/'replay'],out/'compile',180)
    if stages['compile']['exit_code']:raise RuntimeError('replay compilation failed')
    if a.step_reference is not None and (not a.solve or not __import__('math').isfinite(a.step_reference) or a.step_reference<0):raise ValueError('explicit finite nonnegative original-step reference requires solve')
    stages['replay']=guarded([out/'replay',trace]+(['solve'] if a.solve else ['free-newton'] if a.free_newton else [])+([str(a.step_reference)] if a.step_reference is not None else []),out/'replay_process',60)
    write_json(out/'summary.json',dict(status='EXPERIMENTAL',scope='independent rejected-step reconstruction;NOT accepted dynamics',
        original_case=a.case,original_status=trial['status'],stages=stages,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        inputs=dict(trace_sha256=sha(trace),original_summary_sha256=sha(source/'summary.json'),diagnostic_sha256=sha(diagnostic),binary_sha256=sha(out/'replay'))))
    print('\n'.join(line for line in (out/'replay_process/stdout.log').read_text().splitlines() if len(line)<500)[:8000])

if __name__=='__main__':main()
