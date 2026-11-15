import os,json
from pathlib import Path
from beam_common import ROOT,SDK,PREFIX,FRAME,PLUGIN as BEAM,identity as beam_identity
from verification_common import write_json,sha,provenance
OUT=Path(os.environ.get('REGRIP_HISTORY_OUT',ROOT/'results/history_20261115')).resolve()
BUILD=ROOT/'build/history_20261115/v1'
PLUGIN=BUILD/'libReGripMaterialHistory.so'
def sources():
    paths=list((ROOT/'models/contact_history').glob('*'))+[ROOT/p for p in ('models/grasp/StickSlip.cpp','models/grasp/StickSlip.h','models/closure/Quadrature.h','models/stabilization/ContactKernel.h','models/integrated/Components.cpp','models/integrated/Kernels.h','models/integrated/Recorder.inc')]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}
def identity():
    m=json.loads((BUILD/'build_manifest.json').read_text())
    if m['source_sha256']!=sources() or m['binary_sha256']!=sha(PLUGIN):raise ValueError('history compiled source/binary mismatch')
    return dict(history_build=m,beam=beam_identity(),provenance=provenance(),model='material_node_transport_cell_quadrature_v1')
