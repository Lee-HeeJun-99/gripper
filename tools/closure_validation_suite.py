"""Bounded independent regression; every invocation has a new output namespace."""
import argparse,csv,json,os
from closure_common import ROOT,OUT,BUILD,PYTHON,write_json,sha,provenance
from run_trial import execute_process
def logged(command,directory,timeout=120):
    command=list(map(str,command));directory.mkdir(parents=True,exist_ok=False);write_json(directory/'command.json',command)
    result=execute_process(list(map(str,command)),directory,timeout)
    result['artifacts']={p.name:sha(p) for p in directory.iterdir() if p.is_file()}
    write_json(directory/'result.json',result);return result
def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['unit','golden']);parser.add_argument('--suffix',default='');args=parser.parse_args();out=OUT/('validation_'+args.stage+args.suffix);out.mkdir(exist_ok=False);write_json(out/'provenance.json',provenance());summary={}
    if args.stage=='unit':
        namespace=out/'python';namespace.mkdir();(namespace/'optimization_guards_release').mkdir();(namespace/'automation').mkdir()
        env=dict(PYTHONPATH='.:tools',REGRIP_VERIFICATION_OUT=str(namespace),REGRIP_AUTOMATION_OUT=str(namespace/'automation'),REGRIP_PHYSICS_OUT=str(ROOT/'results/revalidation_20261114T132734Z/physics_release'),REGRIP_BUILD_ROOT=str(ROOT/'build/revalidation_20261114_final'));os.environ.update(env);write_json(out/'environment.json',env)
        summary['python']=logged([PYTHON,'-m','unittest','discover','-s','tests','-p','test_*.py'],out/'python_command',240)
        for name,command in [('active',[BUILD/'clean/test_closure']),('invariants',[BUILD/'invariants/test_closure_invariants']),('frame',[BUILD/'frame/test_closure_frame'])]:summary[name]=logged(command,out/name)
    else:
        from native_scene import generate
        from baseline_regression import metrics,states
        sdk=ROOT/'build/grasp_20261115/sofa_patched';gold=list(csv.DictReader((ROOT/'handover/20261114/result_V109_00_FREE_LDL.csv').open(encoding='utf-8-sig')))
        for i in (1,2):
            directory=out/str(i);directory.mkdir();generate(directory/'scene.scn');cmd=[sdk/'bin/graph_probe',sdk,directory/'scene.scn','600','0',sdk/'lib/libReGripPatchedDiagnostics.so'];write_json(directory/'command.json',list(map(str,cmd)));r=execute_process(list(map(str,cmd)),directory,90);log=(directory/'stdout.log').read_text()+(directory/'stderr.log').read_text();result=dict(status='FAIL',process=r)
            try:
                if r['exit_code'] or '[ERROR]' in log or '600 iterations done' not in log:raise ValueError('engine failure/incomplete')
                actual=metrics(states(directory/'rigid.txt'),states(directory/'interface.txt'))
                if len(actual)!=600:raise ValueError('record count')
                checks={k:all(abs(float(a[k])-float(b[k]))<=1e-10+1e-6*abs(float(b[k])) for a,b in zip(actual,gold)) for k in actual[0] if k in gold[0]}
                result.update(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,last_row=actual[-1],maximum_absolute_errors={k:max(abs(float(a[k])-float(b[k])) for a,b in zip(actual,gold)) for k in checks})
            except (ValueError,OSError,KeyError) as e:result['failure_reason']=str(e)
            result['artifacts']={p.name:sha(p) for p in directory.iterdir() if p.is_file()};write_json(directory/'result.json',result);summary[str(i)]=result
    write_json(out/'summary.json',summary);print({k:v.get('status',v.get('exit_code')) for k,v in summary.items()})
if __name__=='__main__':main()
