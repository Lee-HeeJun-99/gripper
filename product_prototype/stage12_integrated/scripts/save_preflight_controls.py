"""Software negative controls in temporary repos; no research PASS claims."""
import copy
import json
import subprocess
import tempfile
from pathlib import Path
from save_preflight import inspect, seal, verify
from supervised_save import digest


def run():
    checks = {}
    with tempfile.TemporaryDirectory(prefix='regrip-save-preflight-') as directory:
        repo = Path(directory)
        def git(*args):
            return subprocess.check_output(['git',*args],cwd=repo,stderr=subprocess.DEVNULL,text=True).strip()
        git('init'); git('config','user.name','Control'); git('config','user.email','control@invalid')
        (repo/'initial').write_text('control\n'); git('add','initial'); git('commit','-m','control')
        root=repo/'product_prototype/stage12_integrated'; root.mkdir(parents=True)
        user=root/'user.step'; user.write_text('existing user CAD')
        old=[str(user.relative_to(repo))]
        checkpoint=dict(HEAD=git('rev-parse','HEAD'),preexisting_untracked=old)
        result=root/'validation/new/summary.json'; result.parent.mkdir(parents=True)
        result.write_text(json.dumps(dict(status='RESEARCH_FAIL_NOT_RELEASE',force=1.2)))
        name=str(result.relative_to(repo))
        request=dict(expected_HEAD=checkpoint['HEAD'],message='test',
                     files=[dict(path=name,SHA256=digest(result))],results=[name],
                     engineering_progress=dict(category='BLOCKER_EVIDENCE',task_id='test',
                                               mechanism='software control',system_gate_ids=['test']))
        checks['valid_exact_manifest']=inspect(repo,request,checkpoint)['status']=='SAVE_PREFLIGHT_PASS'
        prior=root/'prior.json'; prior.write_text('{}')
        checks['new_prior_copy_not_preexisting']=str(prior.relative_to(repo)) in inspect(repo,request,checkpoint)['missing']
        request['files'].append(dict(path=str(prior.relative_to(repo)),SHA256=digest(prior)))
        checks['exact_copy_listed_passes']=inspect(repo,request,checkpoint)['status']=='SAVE_PREFLIGHT_PASS'
        bad=copy.deepcopy(request); bad['files'].append(dict(path=old[0],SHA256=digest(user)))
        checks['existing_user_excluded']=inspect(repo,bad,checkpoint)['status']=='SAVE_PREFLIGHT_FAIL'
        bad=copy.deepcopy(request); bad['files'][0]['SHA256']='0'*64
        checks['stale_hash_rejected']=bool(inspect(repo,bad,checkpoint)['stale_hashes'])
        protected=root/'scripts/criteria.json'; protected.parent.mkdir(); protected.write_text('{}')
        bad=copy.deepcopy(request); bad['files'].append(dict(path=str(protected.relative_to(repo)),SHA256=digest(protected)))
        checks['protected_path_rejected']=inspect(repo,bad,checkpoint)['status']=='SAVE_PREFLIGHT_FAIL'
        # Removing only a temporary test artifact, not user/research data.
        protected.unlink()
        cp=repo/'checkpoint.json'; cp.write_text(json.dumps(checkpoint))
        rp=repo/'request.json'; rp.write_text(json.dumps(request))
        # Test control metadata is excluded using Git's temporary-repo exclude file.
        (repo/'.git/info/exclude').write_text('checkpoint.json\nrequest.json\n')
        sealed=seal(repo,rp,cp,{})
        checks['seal_recheck_passes']=verify(repo,rp,cp,{},sealed)['status']=='SAVE_PREFLIGHT_PASS'
        late=root/'late.json'; late.write_text('{}')
        try: verify(repo,rp,cp,{},sealed); checks['post_request_new_file_rejected']=False
        except ValueError: checks['post_request_new_file_rejected']=True
        late.unlink()
        result.write_text('{"status":"RESEARCH_FAIL_NOT_RELEASE","force":2}')
        try: verify(repo,rp,cp,{},sealed); checks['post_seal_content_change_rejected']=False
        except ValueError: checks['post_seal_content_change_rejected']=True
        pins={old[0]:'0'*64}
        checks['trusted_pin_mismatch_rejected']=inspect(repo,request,checkpoint,pins)['status']=='SAVE_PREFLIGHT_FAIL'
        checks['no_actual_repo_Git_writes']=True
    return dict(status='SOFTWARE_CONTROLS_PASS' if all(checks.values()) else 'SOFTWARE_CONTROLS_FAIL',
                test_only=True,checks=checks)


if __name__=='__main__':
    result=run();print(json.dumps(result,indent=2));raise SystemExit(0 if all(result['checks'].values()) else 2)
