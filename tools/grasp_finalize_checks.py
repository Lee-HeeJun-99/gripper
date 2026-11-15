"""Bounded clean release build and independent structural force reconstruction."""
import json,subprocess,os
from grasp_common import ROOT,OUT,BUILD,SOFA,sha,write_json,provenance
from run_trial import execute_process
from stabilization_audit import audit

def main():
    out=OUT/'final_checks';out.mkdir(parents=True,exist_ok=False)
    build=BUILD/'release_final';commands=[['cmake','-S',str(ROOT/'models/grasp'),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SOFA)],['cmake','--build',str(build),'-j2'],[str(build/'test_grasp_stick')]]
    stages=[]
    for i,command in enumerate(commands):
        stage=out/str(i);stage.mkdir();write_json(stage/'command.json',command);p=execute_process(command,stage,120);log=(stage/'stdout.log').read_text()+(stage/'stderr.log').read_text();stages.append(dict(command=command,process=p,status='PASS' if p['exit_code']==0 and '[ERROR]' not in log else 'FAIL',warnings=[line for line in log.splitlines() if 'warning:' in line]))
        if p['exit_code']!=0:break
    (out/'python_tests.log').write_text('')
    env=dict(os.environ,PYTHONPATH=str(ROOT)+':'+str(ROOT/'tools'),OPENBLAS_NUM_THREADS='1')
    pycommand=['/home/ubuntu/miniconda3/envs/robot_ws/bin/python','-m','unittest','discover','-s','tests','-p','test_*.py']
    p=subprocess.run(pycommand,cwd=ROOT,env=env,capture_output=True,text=True,timeout=120);(out/'python_tests.log').write_text(p.stdout+p.stderr)
    structural={}
    for name in ('base_patched','halfdt_patched','quarterdt_patched'):
        directory=OUT/'structural'/name;record=json.loads((directory/'metrics.json').read_text());structural[name]=dict(metrics=record,independent_force=audit(directory))
    reference=structural['base_patched']['metrics']['tip_deflection_mm'];differences={name:abs(value['metrics']['tip_deflection_mm']/reference-1) for name,value in structural.items()}
    write_json(out/'structural.json',dict(runs=structural,relative_tip_changes=differences,tolerance=.001,status='PASS' if all(v<.001 for v in differences.values()) and all(v['independent_force']['relative_force']<1e-3 and v['independent_force']['relative_moment']<1e-3 for v in structural.values()) else 'FAIL'))
    write_json(out/'result.json',dict(provenance=provenance(),clean_build=stages,python_tests=dict(command=pycommand,exit_code=p.returncode,status='PASS' if p.returncode==0 else 'FAIL'),binary_sha256=sha(build/'libReGripStickSlip.so') if (build/'libReGripStickSlip.so').exists() else None))
    print('CLEAN BUILD',[(r['status'],len(r['warnings'])) for r in stages],'PYTHON',p.returncode,'STRUCTURE',differences)

if __name__=='__main__':main()
