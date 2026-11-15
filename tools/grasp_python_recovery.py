"""Run byte-identical copies of originals so their CSV writers cannot touch handover."""
import csv,json,os,shutil,subprocess
from pathlib import Path
from grasp_common import ROOT,SOFA,OUT,sha,write_json
from run_trial import execute_process

def main():
    directory=OUT/'python_recovery';directory.mkdir(parents=True,exist_ok=False);runtime=ROOT/'.runtime/python312'
    environment=dict(PYTHONHOME=str(runtime),PYTHONPATH=str(SOFA/'plugins/SofaPython3/lib/python3/site-packages')+':'+str(SOFA/'plugins/SofaPython3/lib'),LD_LIBRARY_PATH=str(runtime/'lib')+':'+str(SOFA/'lib')+':'+str(SOFA/'plugins/SofaPython3/lib'))
    os.environ.update(environment);write_json(directory/'environment.json',environment);results={}
    abi=subprocess.run(['ldd',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')],capture_output=True,text=True);(directory/'ldd.log').write_text(abi.stdout+abi.stderr)
    targets=[('smoke',None,'scenes/python_smoke.py',3),('V109_FREE','handover/20261114/SOFA_V109_SparseLDL_Tangential','00_FREE_LDL.py',600),('V110_FREE','handover/20261114/SOFA_V110_Native_Tangent/scenes','00_FREE.py',600),('V110_SHEAR','handover/20261114/SOFA_V110_Native_Tangent/scenes','02_TAN_K01.py',600)]
    for name,folder,scene,steps in targets:
        out=directory/name;out.mkdir();copies={}
        if folder:
            for source in (ROOT/folder).glob('*.py'):
                shutil.copy2(source,out/source.name);copies[str(source.relative_to(ROOT))]=dict(source_sha256=sha(source),copy_sha256=sha(out/source.name))
            file=out/scene
        else:shutil.copy2(ROOT/scene,out/'scene.py');file=out/'scene.py'
        command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar','-l',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')]
        if name.startswith('V110'):command+=['-l',str(ROOT/'build/revalidation_20261114_final/plugin/bin/libSofaTangentialV110.so')]
        command.append(str(file));write_json(out/'command.json',command);process=execute_process(command,out,90);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        r=dict(process=process,status='PASS' if process['exit_code']==0 and '[ERROR]' not in log and f'{steps} iterations done' in log else 'FAIL',source_copies=copies)
        csvs=list(out.glob('result_*.csv'))
        if folder:
            if not csvs:r.update(status='FAIL',reason='no original recorder CSV')
            else:
                rows=list(csv.DictReader(csvs[0].open(encoding='utf-8-sig')));r['rows']=len(rows);r['last_row']=rows[-1] if rows else None
                if len(rows)!=600:r.update(status='FAIL',reason='original recorder count mismatch')
                if name=='V109_FREE' and len(rows)==600:
                    golden=list(csv.DictReader((ROOT/'handover/20261114/result_V109_00_FREE_LDL.csv').open(encoding='utf-8-sig')));errors={};checks={}
                    for key in ('time_s','tip_deflection_mm','tip_velocity_z_mm_s','max_x_slip_mm','max_y_rel_mm','max_z_rel_mm'):
                        if key not in rows[0] or key not in golden[0]:continue
                        pairs=[(float(a[key]),float(b[key])) for a,b in zip(rows,golden)];errors[key]=max(abs(a-b) for a,b in pairs);checks[key]=all(abs(a-b)<=1e-10+1e-6*abs(b) for a,b in pairs)
                    r['golden_max_abs_errors']=errors;r['golden_checks']=checks
                    if not checks or not all(checks.values()):r['status']='FAIL'
        else:
            if 'REGRIP_PYTHON_SMOKE' not in log:r['status']='FAIL'
        r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'result.json',r);results[name]=r;write_json(directory/'summary.json',results);print(name,r['status'],r.get('last_row'),flush=True)

if __name__=='__main__':main()
