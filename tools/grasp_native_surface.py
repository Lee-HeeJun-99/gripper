"""Native surface pipeline probe; no force-balance claim without reaction audit."""
import os,json,argparse,shutil
from grasp_common import ROOT,SOFA,OUT,PLUGIN,write_json,sha
from run_trial import execute_process

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--direct',action='store_true');parser.add_argument('--name');args=parser.parse_args()
    out=OUT/(args.name or ('native_surface_v2' if args.direct else 'native_surface'));out.mkdir(parents=True,exist_ok=False);runtime=ROOT/'.runtime/python312';source=OUT/'trials/settled_sphere_xplus'
    shutil.copy2(ROOT/'scenes/grasp_native_surface.py',out/'scene.py');source_hash=sha(out/'scene.py')
    environment=dict(PYTHONHOME=str(runtime),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(runtime/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'),REGRIP_NATIVE_SOURCE=str(source),REGRIP_NATIVE_OUT=str(out),REGRIP_NATIVE_SCENE=str(out/'scene.py'));os.environ.update(environment)
    command=[str(runtime/'bin/python'),str(ROOT/'tools/grasp_native_direct.py')] if args.direct else [str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n','3600','--hideProgressBar','-l',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so'),'-l',str(PLUGIN),str(ROOT/'scenes/grasp_native_surface.py')];write_json(out/'environment.json',environment);write_json(out/'command.json',command);p=execute_process(command,out,180);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(process=p,status='EXPERIMENTAL' if p['exit_code']==0 and '[ERROR]' not in log and '3600 iterations done' in log else 'FAIL',scope='native3D mapped triangle surfaces and Lagrange friction; 1.8s approach/contact probe only, NOT full grasp/release or energy certification',source_sha256=sha(ROOT/'scenes/grasp_native_surface.py'))
    if (out/'native_states.jsonl').exists():
        rows=[json.loads(line) for line in (out/'native_states.jsonl').read_text().splitlines()];r.update(frames=len(rows),max_constraint_rows=max((len(row['constraint_forces']) for row in rows),default=0),max_constraint_force=max((max(map(abs,row['constraint_forces']),default=0) for row in rows),default=0))
    r['source_sha256']=source_hash;r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',r);print(r)

if __name__=='__main__':main()
