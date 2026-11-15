"""Validate the actual saved loader resolution,not merely ldd exit0."""
import re
from pathlib import Path
from curve_common import OUT,SDK,sha,write_json


def main():
    target=OUT/'patch_refinement_v2/runtime_resolution.json'
    if target.exists():raise ValueError('immutable loader evidence exists')
    source=OUT/'patch_refinement_v2/build/ldd/stdout.log';log=source.read_text();libraries={};errors=[]
    if'not found'in log:errors.append('unresolved dependency')
    for name,path in re.findall(r'^\s*(libSofa\S+)\s+=>\s+(\S+)',log,re.M):
        resolved=Path(path).resolve()
        if SDK.resolve()not in resolved.parents:errors.append('mixed SOFA library '+path)
        libraries[name]=dict(resolved=str(resolved),sha256=sha(resolved))
    if not libraries:errors.append('no actual SOFA dependencies')
    write_json(target,dict(status='FAIL'if errors else'PASS',sdk=str(SDK.resolve()),actual_ldd_log_sha256=sha(source),libraries=libraries,errors=errors,scope='actual ldd resolution of compiled v2 plugin;aliases resolved before comparison;not physics or whole-engine memory certification'))
    print('actual loader',len(libraries),'SDK libraries',errors)
    if errors:raise SystemExit(1)


if __name__=='__main__':main()
