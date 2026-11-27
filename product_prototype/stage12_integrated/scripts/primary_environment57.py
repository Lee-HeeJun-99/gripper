"""Actual read-only source/CAD/environment provenance for this Python-only cycle."""
import sys,json,shutil,platform,subprocess,hashlib
from pathlib import Path
from baseline_registry import ROOT,REPO,ref,sha,dump
import primary_auxiliary57b,primary_endpoint_liftoff_finger57,primary_lower_release_finger57
import numpy,scipy,skfem,pyamg,OCP,gmsh
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cadp=ROOT/'cad/exports/primaryP1_integral55e/summary.json';cad=json.loads(cadp.read_text());pins=json.loads((ROOT/'runtime/goal_authorized_20261127_7/ledger.json').read_text())['source_pins'];modules=[]
for name,m in sorted(list(sys.modules.items())):
 p=Path(getattr(m,'__file__','') or '')
 if not p.is_file():continue
 if p.is_relative_to(REPO):modules.append(dict(module=name,source=ref(p)))
versions={name:dict(version=str(getattr(m,'__version__',None)),entry_file=str(m.__file__),entry_file_SHA256=sha(Path(m.__file__))) for name,m in [('numpy',numpy),('scipy',scipy),('skfem',skfem),('pyamg',pyamg),('OCP',OCP),('gmsh',gmsh)]};checks=dict(HEAD=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='ba533ad70760d96047997d9b0c9de87c9100c511',source_pins_unchanged=all(sha(REPO/p)==v for p,v in pins.items()),all77_actual_parts=len(cad['part_references'])==77 and all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values()),assembly_unchanged=sha(REPO/cad['assembly']['path'])==cad['assembly']['SHA256'],BOM_unchanged=sha(REPO/cad['BOM']['path'])==cad['BOM']['SHA256'],STOP_absent=not(ROOT/'runtime/STOP').exists());dump(out/'summary.json',dict(status='ACTUAL_PRODUCT77_SOURCE_CAD_ENVIRONMENT_IDENTITY_PASS' if all(checks.values()) else 'ACTUAL_PRODUCT_SOURCE_IDENTITY_FAIL',candidate=ref(cadp),producer=ref(out/'producer.py'),checks=checks,loaded_repository_modules=modules,Python=sys.version,executable=sys.executable,packages=versions,SOFA_runs=0,compiled_new_binaries=0,SDK_changes=0,CAD_changed_this_cycle=[],source_pins=pins,whole_system_release=False));print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 2)
