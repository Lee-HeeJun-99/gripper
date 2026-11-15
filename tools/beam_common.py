"""Independent conservative-beam campaign; frozen prior evidence is read-only."""
import os
from pathlib import Path
from verification_common import ROOT,sha,write_json,provenance
OUT=Path(os.environ.get('REGRIP_BEAM_OUT',ROOT/'results/beam_20261115')).resolve()
BUILD=ROOT/'build/beam_20261115'
SDK=ROOT/'build/grasp_20261115/sofa_patched'
PLUGIN=Path(os.environ.get('REGRIP_BEAM_PLUGIN',BUILD/'v2/libReGripConservativeBeam.so')).resolve()
FRAME=ROOT/'build/closure_20261115/frame/libReGripFrameClosure.so'
PREFIX=ROOT/'.runtime/closure_sdk'
PYTHON='/home/ubuntu/miniconda3/envs/robot_ws/bin/python'
def material():
    import math
    I=8*.4**3/12;r=(4*I/math.pi)**.25;A=math.pi*r*r;E=250.;G=E/(2*(1+.32));return dict(EA=E*A,GAy=G*A*5/6,GAz=G*A*5/6,GJ=G*2*I,EIy=E*I,EIz=E*I)
def identity():
    import json
    files=[p for folder in ('models/conservative_beam','diagnostics/conservative_beam') for p in (ROOT/folder).glob('*') if p.is_file()]
    files+=list((ROOT/'tools').glob('beam_*.py'))+list((ROOT/'tests').glob('test_conservative_beam*'))
    manifest_path=PLUGIN.parent/'build_manifest.json';manifest=json.loads(manifest_path.read_text())
    if manifest['plugin_sha256']!=sha(PLUGIN):raise ValueError('beam binary differs from frozen build')
    for name,digest in manifest['compiled_source_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('beam compiled source differs from working tree: '+name)
    for name,digest in manifest.get('dependency_sha256',{}).items():
        if sha(ROOT/name)!=digest:raise ValueError('beam compiled dependency differs from working tree: '+name)
    return dict(source_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},compiled_source_sha256=manifest['compiled_source_sha256'],build_manifest_sha256=sha(manifest_path),plugin_sha256=sha(PLUGIN),frame_sha256=sha(FRAME),sdk_root=str(SDK),sdk_driver_sha256=sha(SDK/'bin/graph_probe'),model='objective_midpoint_so3_rod_v2_equivalent',material=material(),provenance=provenance())
