import os,json
from pathlib import Path
from research_common import ROOT,SDK,FRAME,BEAM,PREFIX,identity as parent_identity,sha,write_json,provenance
OUT=Path(os.environ.get('REGRIP_CURVE_OUT',ROOT/'results/autonomous_20261116_curve_a01')).resolve()
BUILD=Path(os.environ.get('REGRIP_CURVE_BUILD',ROOT/'build/autonomous_20261116_curve_a01/v3')).resolve()
PLUGIN=BUILD/'libReGripCurvedContact.so'
def sources():
    paths=list((ROOT/'models/curved_contact').glob('*'))+[ROOT/'tests/test_curved_contact.cpp',ROOT/'models/contact_kinematics/HermiteMap.h']
    return {str(p.relative_to(ROOT)):sha(p)for p in paths if p.is_file()}
def identity():
    manifest=json.loads((BUILD/'build_manifest.json').read_text())
    if manifest['sources']!=sources()or manifest['binary']!=sha(PLUGIN)or manifest['generated']!=sha(BUILD/'CurvedGenerated.inc'):raise ValueError('curved compiled artifact mismatch')
    return dict(curved=manifest,inherited=parent_identity(),provenance=provenance(),model='director_hermite_fixed_material_midpoints_normal_and_tangent_v1')
