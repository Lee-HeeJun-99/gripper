import os,json
from pathlib import Path
from history_common import ROOT,SDK,PREFIX,FRAME,BEAM
from beam_common import identity as beam_identity
from verification_common import write_json,sha,provenance
OUT=Path(os.environ.get('REGRIP_BIRTH_OUT',ROOT/'results/birth_20261115')).resolve()
BUILD=Path(os.environ.get('REGRIP_BIRTH_BUILD',ROOT/'build/birth_20261115/v1')).resolve()
PLUGIN=BUILD/'libReGripBirthContact.so'
def sources():
    paths=[p for folder in ('models/contact_birth','models/contact_history','models/grasp','models/closure','models/stabilization','models/integrated','models/finite_rotation') for p in (ROOT/folder).rglob('*') if p.is_file() and (p.suffix in ('.h','.cpp','.inc') or p.name=='CMakeLists.txt')]+[ROOT/'tests/test_birth.cpp']
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}
def identity():
    m=json.loads((BUILD/'build_manifest.json').read_text())
    if m['source_sha256']!=sources() or m['binary_sha256']!=sha(PLUGIN):raise ValueError('birth compiled-source/binary mismatch')
    return dict(birth_build=m,beam=beam_identity(),provenance=provenance(),model='birth_chord_implicit_J_'+BUILD.name)
