"""Unified strict JSON entry point for static research and SOFA length extensions."""
import argparse
from dataclasses import fields
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from models.multilayer.beam import Design,solve
from verification_common import ROOT,sha,write_json,provenance
from research_trial import run,model_hashes

MODELS={'multilayer-static-0.1','planar-length-extension-0.1','objective-3d-0.1'}

def load_config(path):
    def reject(value):raise ValueError('nonfinite JSON constant: '+value)
    c=json.loads(Path(path).read_text(),parse_constant=reject)
    if not isinstance(c,dict) or set(c)!={'model','units','assumptions','parameters'}:raise ValueError('exact model/units/assumptions/parameters keys required')
    if c['model'] not in MODELS or c['units']!='model_F_mm_s' or not isinstance(c['assumptions'],str) or not c['assumptions'].strip():raise ValueError('model, units or assumptions missing')
    if not isinstance(c['parameters'],dict):raise ValueError('parameters must be an object')
    if c['model']=='multilayer-static-0.1':
        if set(c['parameters'])-{f.name for f in fields(Design)}:raise ValueError('unknown static parameter')
        if 'connectors' in c['parameters']:c['parameters']['connectors']=tuple(c['parameters']['connectors'])
        Design(**c['parameters']).validate()
    else:
        if set(c['parameters'])-{'length','n','k','load','dt','duration','connectors'}:raise ValueError('unknown SOFA parameter')
    return c

def execute(config,out):
    c=load_config(config);out=Path(out).resolve()
    if c['model']!='multilayer-static-0.1':
        # The native runner independently validates config, build and actual output.
        r=run(out,**c['parameters'],finite=c['model']=='objective-3d-0.1')
        write_json(out/'experiment_contract.json',c)
        r['experiment_config_sha256']=sha(config);r['artifacts']['experiment_contract.json']=sha(out/'experiment_contract.json')
        write_json(out/'metrics.json',r);return r
    out.mkdir(parents=True,exist_ok=False)
    write_json(out/'config.json',c)
    import numpy
    report=dict(model=c['model'],scope='EXPERIMENTAL uncalibrated static model',provenance=provenance(),
        source_sha256=model_hashes(),runner_sha256=sha(__file__),config_sha256=sha(config),
        binary_sha256=None,backend='numpy.linalg.solve',numpy_version=numpy.__version__,
        command=sys.argv,metrics=solve(Design(**c['parameters'])))
    report['numerical_gate']=report['metrics']['small_rotation_validated'] and report['metrics']['normalized_residual']<1e-6
    write_json(out/'metrics.json',report)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    r=execute(a.config,a.out);print(r.get('status','EXPERIMENTAL'),r.get('numerical_gate'))
