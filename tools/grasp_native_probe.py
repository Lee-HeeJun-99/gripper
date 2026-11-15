"""Read-only link provenance and MappingGraph lifetime on the rebuilt engine."""
import os,subprocess
from grasp_common import ROOT,OUT,BUILD,write_json,sha
from run_trial import execute_process

def main():
    out=OUT/'sdk_probe';out.mkdir(parents=True,exist_ok=False);sdk=BUILD/'sofa_patched';binary=sdk/'bin/graph_probe';command=[str(binary),str(sdk),str(ROOT/'scenes/integrated/minimal_mapping_graph.scn'),'10','0']
    os.environ['REGRIP_GRAPH_PROBE']='1';write_json(out/'command.json',command);p=execute_process(command,out,30);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();ldd=subprocess.run(['ldd',str(binary)],capture_output=True,text=True);(out/'ldd.log').write_text(ldd.stdout+ldd.stderr)
    if '/home/ubuntu/SOFA' in ldd.stdout:raise RuntimeError('installed engine accidentally linked')
    r=dict(process=p,status='PASS' if p['exit_code']==0 and '[ERROR]' not in log and 'retained=0' in log else 'FAIL',binary_sha256=sha(binary),matched_sdk_lib_sha256={f.name:sha(f) for f in (sdk/'lib').glob('libSofa*.so.26.06.00')},installed_engine_linked=False)
    r['artifacts']={f.name:sha(f) for f in out.iterdir() if f.is_file()};write_json(out/'result.json',r);print(r['status'],[line for line in log.splitlines() if 'GRAPH_CLEAR' in line])

if __name__=='__main__':main()
