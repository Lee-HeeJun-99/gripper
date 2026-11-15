"""Actual C++/engine audits, separate from full grasp certification."""
import argparse,json
from integrated_trial import Config,scene
from grasp_common import ROOT,SOFA,OUT,BUILD,write_json,sha
from run_trial import execute_process

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['unit','beam','sdk_memory']);args=parser.parse_args();out=OUT/'audits'/args.stage;out.mkdir(parents=True,exist_ok=False)
    if args.stage=='unit':command=[str(BUILD/'stick_v2/test_grasp_stick')];limit=30
    elif args.stage=='beam':
        scene(out,Config(k=0));command=[str(BUILD/'diagnostics/beam_energy_probe'),str(SOFA),str(out/'scene.scn'),str(ROOT/'build/stabilization_20261115/plugin/libReGripStabilization.so')];limit=90
    else:command=[str(BUILD/'sdk_diagnostics/memory_lifetime'),str(BUILD/'sofa_patched'),str(ROOT/'scenes/integrated/minimal_mapping_graph.scn')];limit=90
    write_json(out/'command.json',command);process=execute_process(command,out,limit);text=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(process=process,binary_sha256=sha(command[0]),status='PASS' if process['exit_code']==0 and '[ERROR]' not in text else 'FAIL')
    if args.stage=='beam':r['measurements']=[json.loads(row[len('ENERGY_CHECK '):]) for row in text.splitlines() if row.startswith('ENERGY_CHECK ')];r['scope']='candidate .5*d*Klocal*d only; derivative comparison required before calling a potential'
    if args.stage=='sdk_memory':
        measurements=[json.loads(row[4:]) for row in text.splitlines() if row.startswith('MEM ')];r['measurements']=measurements
        if measurements:
            positive=[p for p in measurements if p['step']>=0];r['live_growth_last60000']=positive[-1]['live_heap']-positive[-2]['live_heap'];r['plateau']=r['live_growth_last60000']<1024*1024
            if not r['plateau']:r['status']='FAIL'
    r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',r);print(r)

if __name__=='__main__':main()
