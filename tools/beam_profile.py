"""Profile bounded41-node integration before any new full high-resolution retry."""
import json
from beam_common import ROOT,OUT,BUILD,PREFIX,SDK,FRAME,PLUGIN,write_json
from beam_grasp_trial import run
from closure_validation_suite import logged
from run_trial import execute_process
def main():
    out=OUT/'profile';out.mkdir(parents=True,exist_ok=False);build=BUILD/'profile_diagnostics'
    for name,cmd in [('configure',['cmake','-S','diagnostics/conservative_beam','-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',str(build),'--target','beam_profile','-j2'])]:
        r=logged(cmd,out/name,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='BLOCKED',result=r));return
    trial=run('profile41',nodes=41,samples=32,prepare_only=True);cmd=[str(build/'beam_profile'),str(SDK),str(trial/'scene.scn'),str(FRAME),str(PLUGIN)];write_json(out/'command.json',cmd);p=execute_process(cmd,out,480);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();steps=[json.loads(s[14:]) for s in log.splitlines() if s.startswith('PROFILE_STEPS ')];fields=[json.loads(s[14:]) for s in log.splitlines() if s.startswith('PROFILE_FIELD ')];write_json(out/'summary.json',dict(status='PASS' if p['exit_code']==0 and '[ERROR]' not in log and steps and fields else 'FAIL',process=p,steps=steps,fields=fields,scope='8000 actual time steps plus100query samples; no full48k-step grasp certificate; force queries alone do not update friction history'));print(steps,fields)
if __name__=='__main__':main()
