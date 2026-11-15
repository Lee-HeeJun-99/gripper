import os,json
from pathlib import Path
from birth_common import ROOT,SDK,FRAME,BEAM,PREFIX,identity as inherited_identity,sha,write_json,provenance
OUT=Path(os.environ.get('REGRIP_RESEARCH_OUT',ROOT/'results/autonomous_20261115_a01')).resolve()
BUILD=Path(os.environ.get('REGRIP_RESEARCH_BUILD',ROOT/'build/autonomous_20261115_a01/v3')).resolve()
PLUGIN=BUILD/'libReGripMaterialPointContact.so'
def sources():
    paths=list((ROOT/'models/material_point_contact').glob('*'))+[ROOT/'tests/test_material_point.cpp']
    return {str(p.relative_to(ROOT)):sha(p)for p in paths if p.is_file()}
def identity():
    manifest=json.loads((BUILD/'build_manifest.json').read_text())
    if manifest['sources']!=sources()or manifest['binary']!=sha(PLUGIN)or manifest['generated']!=sha(BUILD/'MaterialPointGenerated.inc'):raise ValueError('material-point compiled artifact mismatch')
    return dict(material_point=manifest,inherited=inherited_identity(),provenance=provenance(),model='immutable_material_midpoints_no_history_interpolation_v1')
