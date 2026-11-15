"""Historical evidence stays immutable; distinguish expected metadata changes."""
import json,subprocess
from pathlib import Path
from closure_common import ROOT,OUT,sha,write_json
def main():
    m=json.loads((ROOT/'reports/GRASP_EVIDENCE_MANIFEST.json').read_text());checked=0;errors=[];metadata=[]
    for group in ('source_sha256','binary_sha256','report_sha256','evidence_sha256','external_runtime_sha256'):
        for path,h in m.get(group,{}).items():
            p=Path(path) if group=='external_runtime_sha256' else ROOT/path;checked+=1
            if not p.is_file() or sha(p)!=h:
                if path in ('.gitignore','README.md','AGENTS.md'):metadata.append(path)
                else:errors.append(group+':'+path)
    for path,item in m['raw_files'].items():
        p=Path(m['raw_root'])/path;checked+=1
        if not p.is_file() or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:errors.append('raw:'+path)
    comparison=subprocess.run(['git','diff','20249c953a7eef30f5574e4e7d1ce7cb098505f6','--name-only','--','plugin','models/grasp','models/integrated','models/stabilization','models/finite_rotation','models/multilayer','handover','reference_fem'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    write_json(OUT/'legacy_integrity.json',dict(status='PASS' if not errors and not comparison else 'FAIL',checked=checked,errors=errors,expected_documentation_or_ignore_changes=metadata,old_physics_or_golden_changes=comparison,old_manifest_sha256=sha(ROOT/'reports/GRASP_EVIDENCE_MANIFEST.json'),scope='historical evidence verified, NOT new physical execution; raw and old binaries unchanged; strict old verifier correctly reports current metadata delta'))
    print(checked,'checks','errors',errors,'metadata',metadata)
if __name__=='__main__':main()
