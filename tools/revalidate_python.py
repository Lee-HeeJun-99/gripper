"""Attempt a project-local runtime recovery and run copies of original scenes."""
import json
import os
from pathlib import Path
import shutil
import sys
from verification_common import ROOT,RUN,SOFA,command,write_json


def main():
    env=os.environ.copy();env['CONDA_PKGS_DIRS']=str(ROOT/'.conda-pkgs');env['CONDA_ENVS_PATH']=str(ROOT/'.conda-envs')
    conda='/home/ubuntu/miniconda3/bin/conda'
    offline=command('python312_offline',[conda,'create','--prefix',str(ROOT/'.venv-sofa-revalidation'),
        '--offline','--solver','classic','--yes','python=3.12','numpy'],timeout=60,env=env)
    online=command('python312_online',[conda,'create','--prefix',str(ROOT/'.venv-sofa-revalidation'),
        '--solver','classic','--yes','python=3.12','numpy'],timeout=60,env=env)
    scene=RUN/'python_original_scene';scene.mkdir(exist_ok=False)
    source=ROOT/'handover/20261114/SOFA_V109_SparseLDL_Tangential'
    for path in source.glob('*.py'):shutil.copyfile(path,scene/path.name)
    cmd=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n','600','--hideProgressBar','-l','SofaPython3']
    free=command('original_python_free',cmd+[str(scene/'00_FREE_LDL.py')],timeout=30)
    shear=command('original_python_shear',cmd+[str(scene/'01_TAN_K001_LDL.py')],timeout=30)
    log=Path(free['log']).read_text()
    passed=free['exit_code']==0 and '[ERROR]' not in log and (scene/'result_V109_00_FREE_LDL.csv').exists()
    write_json(RUN/'python_recovery.json',dict(status='PASS' if passed else 'BLOCKED',offline=offline,online=online,
        original_free=free,original_shear=shear,original_scene_loaded=passed,
        reason='' if passed else 'SofaPython3 loader cannot find libpython3.12.so.1.0; runtime installation unavailable',
        note='A zero SOFA exit status does not establish scene loading. Sources were copied; handover originals were not modified.'))


if __name__=='__main__':main()
