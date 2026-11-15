import os,json
from pathlib import Path
from beam_common import ROOT,SDK,PREFIX,FRAME,PLUGIN as BEAM,identity as beam_identity
from verification_common import write_json,sha,provenance
OUT=Path(os.environ.get('REGRIP_HISTORY_OUT',ROOT/'results/history_20261115')).resolve()
BUILD=Path(os.environ.get('REGRIP_HISTORY_BUILD',ROOT/'build/history_20261115/v3')).resolve()
PLUGIN=BUILD/'libReGripMaterialHistory.so'
def sources():
    paths=[p for folder in ('models/contact_history','models/grasp','models/closure','models/stabilization','models/integrated','models/finite_rotation') for p in (ROOT/folder).rglob('*') if p.is_file() and (p.suffix in ('.h','.cpp','.inc') or p.name=='CMakeLists.txt')];paths+=[ROOT/'tests/test_contact_history.cpp']
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}
def identity():
    m=json.loads((BUILD/'build_manifest.json').read_text())
    if m['source_sha256']!=sources() or m['binary_sha256']!=sha(PLUGIN):raise ValueError('history compiled source/binary mismatch')
    return dict(history_build=m,beam=beam_identity(),provenance=provenance(),model='material_node_transport_cell_quadrature_'+BUILD.name)
