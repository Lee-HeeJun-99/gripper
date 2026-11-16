"""Post-run SDK/test binary identity supplement; never modifies either SDK."""
import argparse,json,subprocess
from pathlib import Path
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args();target=ROOT/'reports/FILM_CONTACT_SDK_IDENTITY_20261116.json'
 if a.verify:
  d=json.loads(target.read_text());bad=[name for name,value in d['binary_sha256'].items() if not Path(name).is_file() or sha(Path(name))!=value];print(json.dumps(dict(status='FAIL' if bad else 'PASS',files=len(d['binary_sha256']),mismatches=bad)));raise SystemExit(bool(bad))
 if target.exists():raise RuntimeError('identity supplement already exists')
 paths=set();sdk=ROOT/'build/grasp_20261115/sofa_patched';installed=Path('/home/ubuntu/SOFA/v26.06.00')
 for prefix in (sdk,installed):paths.update(f.resolve() for f in (prefix/'lib').glob('libSofa*.so*') if f.is_file())
 paths.update((sdk/'bin/graph_probe',installed/'bin/runSofa-26.06.00'))
 for pattern in ('build/film_shell_20261116_native_be_core105/test_film*','build/film_rail_20261116_rail_native95/test_film*','build/film_rail_mapping144/test_film*'):
  paths.update(f for f in ROOT.glob(pattern) if f.is_file())
 write_json(target,dict(scope='Post-run read-only SDK and test binary byte identities,not memory/physics certification;not represented as a per-step launch-time monitor',ledger_sha256=sha(ROOT/'reports/FILM_CONTACT_EVIDENCE_20261116_v2.json'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),tool_sha256=sha(__file__),binary_sha256={str(f):sha(f) for f in sorted(paths)}));print(json.dumps(dict(files=len(paths))))
if __name__=='__main__':main()
