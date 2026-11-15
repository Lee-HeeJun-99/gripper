"""Build all components used by V109, compare full600 golden records on new SDK."""
import csv,json,argparse
from grasp_common import ROOT,OUT,BUILD,write_json,sha
from run_trial import execute_process
from native_scene import generate
from baseline_regression import metrics,states

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='sdk_regression');args=parser.parse_args()
    directory=OUT/args.name;directory.mkdir(parents=True,exist_ok=False);sdk=BUILD/'sofa_patched';build=directory/'build';build.mkdir()
    command=['cmake','--build',str(sdk),'--target','Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.MechanicalLoad','Sofa.Component.Mapping.NonLinear','Sofa.Component.Playback','Sofa.Component.Constraint.Projective','ReGripPatchedDiagnostics','-j4'];write_json(build/'command.json',command);process=execute_process(command,build,600);write_json(build/'result.json',process)
    if process['exit_code']!=0:print('SDK physical component build blocked',process);return
    summaries={}
    for repeat in (1,2):
        out=directory/str(repeat);out.mkdir();generate(out/'scene.scn');plugin=sdk/'lib/libReGripPatchedDiagnostics.so';command=[str(sdk/'bin/graph_probe'),str(sdk),str(out/'scene.scn'),'600','0',str(plugin)];write_json(out/'command.json',command);p=execute_process(command,out,90);text=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(process=p,status='FAIL')
        try:
            if p['exit_code'] or '[ERROR]' in text or '600 iterations done' not in text:raise ValueError('native error/incomplete')
            actual=metrics(states(out/'rigid.txt'),states(out/'interface.txt'));gold=list(csv.DictReader((ROOT/'handover/20261114/result_V109_00_FREE_LDL.csv').open(encoding='utf-8-sig')));checks={};errors={}
            if len(actual)!=600 or len(gold)!=600:raise ValueError('record count')
            for key in actual[0]:
                if key not in gold[0]:continue
                pairs=[(float(a[key]),float(b[key])) for a,b in zip(actual,gold)];checks[key]=all(abs(a-b)<=1e-10+1e-6*abs(b) for a,b in pairs);errors[key]=max(abs(a-b) for a,b in pairs)
            r.update(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,max_abs_errors=errors,last_row=actual[-1])
        except (ValueError,OSError,KeyError) as e:r['reason']=str(e)
        r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',r);summaries[str(repeat)]=r;write_json(directory/'summary.json',summaries);print(repeat,r['status'],r.get('last_row'),flush=True)

if __name__=='__main__':main()
