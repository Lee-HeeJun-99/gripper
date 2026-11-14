"""Targeted symmetric-solver experiments after the original 8-layer mesh gate fails.

Original failed output is read-only. Same model/material/load/tolerances; only
numerical solver and declared convergence settings change in new experiments.
"""
from dataclasses import replace,asdict
import xml.etree.ElementTree as ET
from integrated_trial import Config,scene,analyze
from integrated_common import ROOT,SOFA,OUT,BUILD,sha,write_json,provenance
from run_trial import execute_process

def main():
    root=OUT/'solver_retry';root.mkdir(parents=True,exist_ok=False);results={}
    base=Config(layers=8,k=100)
    for name,c in [('L8_11_LDL',base),('L8_21_LDL',replace(base,nodes=21,connectors=tuple(range(2,21,2)))),
        ('L8_21_LDL_dt_double',replace(base,nodes=21,connectors=tuple(range(2,21,2)),dt=.001)),
        ('L8_21_LDL_extended',replace(base,nodes=21,connectors=tuple(range(2,21,2)),duration=18))]:
        out=root/name;out.mkdir();g=scene(out,c);tree=ET.parse(out/'scene.scn');solver=tree.getroot().find('EigenSparseLU');solver.tag='SparseLDLSolver';solver.set('template','CompressedRowSparseMatrixd');tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
        plugin=BUILD/'plugin/libReGripIntegrated.so';cmd=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(round(c.duration/c.dt)),'--hideProgressBar','-l',str(plugin),str(out/'scene.scn')]
        write_json(out/'config.json',dict(**asdict(c),solver='SparseLDL'));write_json(out/'command.json',cmd);p=execute_process(cmd,out,180)
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(config=dict(**asdict(c),solver='SparseLDL'),provenance=provenance(),binary_sha256=sha(plugin),process=p)
        try:r.update(analyze(out,c,g,p,log))
        except (ValueError,KeyError,OSError) as e:r.update(status='FAIL',reason=str(e))
        r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='metrics.json'};write_json(out/'metrics.json',r);results[name]=r;write_json(root/'summary.json',results)
        print(name,r['status'],r.get('tip_deflection_mm'),r.get('relative_residual'),flush=True)

if __name__=='__main__':main()
