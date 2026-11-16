"""Supplement the immutable base index without rewriting it or its cohort."""
import json
import hashlib
import shutil
import subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged


def main():
    target=ROOT/'reports/curved_evidence/v2/replay_supplement.json'
    if target.exists():raise ValueError('immutable replay supplement exists')
    names=['tools/curve_replay.py','tools/curve_replay_supplement.py','tests/test_curve_replay_guards.py']
    if subprocess.check_output(['git','diff','HEAD','--name-only','--',*names],cwd=ROOT).strip():raise ValueError('commit replay source before sealing')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    case=ROOT/'results/autonomous_20261116_sealed_replay_a01';summary=json.loads((case/'summary.json').read_text())
    verification=ROOT/'results/autonomous_20261116_phase_grid_a01/evidence_verify_v2';verified=json.loads((verification/'stdout.log').read_text())
    if summary['status']!='PASS'or verified['status']!='PASS':raise ValueError('actual replay/base verification prerequisite failed')
    checks=ROOT/'results/autonomous_20261116_sealed_replay_checks_a01';checks.mkdir(exist_ok=False)
    for name in names:
        path=checks/'sources'/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,path)
    result=logged(['/home/ubuntu/miniconda3/envs/robot_ws/bin/python','-m','unittest','discover','-s','tests','-p','test_curve_replay_guards.py','-v'],checks/'unit',180)
    if result['exit_code']:raise ValueError('current stricter path/role guards failed')
    files=[p for directory in(case,verification,checks)for p in directory.rglob('*')if p.is_file()]
    write_json(target,dict(status='PASS',source_checkpoint=commit,base_manifest_sha256=sha(ROOT/'reports/CURVED_RESEARCH_EVIDENCE_MANIFEST_V2.json'),files={str(p.relative_to(ROOT)):sha(p)for p in files},git_source_blobs={name:hashlib.sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()for name in names},actual_runner_snapshot_sha256=sha(case/'RunnerSource.py'),current_cli_sha256=sha(ROOT/'tools/curve_replay.py'),replay=summary,base_verification=verified,scope='base4945artifact/149blob integrity and actual sealed4s replay only. Actual runner snapshot is explicit;current stricter path guards have separate unit tests. Future supplemental files are outside the immutable base cohort. No physical/grasp certification inferred.'))
    print('replay supplement PASS',len(files),'artifacts')


if __name__=='__main__':main()
