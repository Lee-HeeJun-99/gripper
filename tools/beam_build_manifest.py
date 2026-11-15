"""Freeze binary-to-compiled-source mapping before further trials.

Prototype mapping is independently anchored to first trial and immutable git blobs;
current working-tree metadata is NOT silently called compiled source evidence.
"""
import hashlib,json,subprocess
from beam_common import ROOT,OUT,BUILD,sha,write_json
def main():
    prototype=BUILD/'prototype';first=json.loads((OUT/'single/tip11/metrics.json').read_text());compiled={}
    for name in ('ConservativeBeam.cpp','EnergyKernel.h','CMakeLists.txt'):
        path='models/conservative_beam/'+name;blob=subprocess.run(['git','show','4d19774:'+path],cwd=ROOT,capture_output=True,check=True).stdout;digest=hashlib.sha256(blob).hexdigest()
        if first['identity']['source_sha256'][path]!=digest:raise ValueError('prototype source not anchored by initial trial')
        compiled[path]=digest
    if sha(prototype/'libReGripConservativeBeam.so')!=first['identity']['plugin_sha256']:raise ValueError('prototype binary changed')
    write_json(prototype/'build_manifest.json',dict(plugin_sha256=sha(prototype/'libReGripConservativeBeam.so'),compiled_source_sha256=compiled,source_commit='4d19774',scope='retrospectively anchored immutable prototype; later working-tree source snapshots in queued trials are metadata, not proof of compiled v2'))
    v2=BUILD/'v2';compiled={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'models/conservative_beam').glob('*') if p.suffix in ('.h','.cpp') or p.name=='CMakeLists.txt'};write_json(v2/'build_manifest.json',dict(plugin_sha256=sha(v2/'libReGripConservativeBeam.so'),compiled_source_sha256=compiled,dependency_sha256={'models/finite_rotation/Kernel.h':sha(ROOT/'models/finite_rotation/Kernel.h')},cache_sha256=sha(v2/'CMakeCache.txt'),scope='exact constant propagation+precomputed reference+per-edge cache;100state E/F/J dense reference bit-identical'))
if __name__=='__main__':main()
