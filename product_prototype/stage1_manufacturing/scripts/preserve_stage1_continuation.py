"""Preserve local originals; version manifests/snapshots rather than trial gigabytes."""
import argparse,hashlib,importlib.metadata,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 states={'revK_wireclear':'FAIL orphan bracket sliver','revK_openrelief':'FAIL cap screw exceeds original hole length','revK_threadclear':'Scoped CAD/motion/wire PASS, superseded','revL_interfaces':'INTERMEDIATE, source edited near job completion; not used as qualified source evidence','revL_bore':'Scoped geometry/keys/service PASS, supplier end and bend updates supersede','revM_supplier_end':'Manufacturer D-total corrected; scoped CAD/motion/keys PASS','revN_bend22':'FAIL60deg swivel bolt/nut interFinger contact','revN_recessed':'FAIL3lower-receiver STLs zero-wall tangency','revN_openface':'Motion PASS; nut approach FAIL in original assembly order','revN_motor_gap':'Full laminate motion/40keys/21nut tools PASS before machining pocket update','revP_machinable':'Accessible2mm-endmill pocket; independent motion/wire/keys/profile PASS','revQ_wire_assembly':'Actual3free-wire solids,292parts, independent envelope-volume match,0bulk collisions','revR_fit_clearance':'Only6carrier parts relieved for diameter+paired-axis tolerance margin,292parts0bulk collisions','revS_documented_motor':'Documented alternative17HS15-1504S1 maxbody40/maxshaft25/maxpilot2.5,292parts0bulk collisions; final checks authoritative'}
 states.update({'revT_inner_relief':'Actual own flexible material correction;31poses PASS after66hits in prior S','revU_maxwire':'Actual maximum-wire groove correction;0.52D and finished-length endpoints PASS','revV_pocket_blend':'Producer assertion FAIL duplicate edge occurrences; no STEP generation','revV_pocket_blend2':'Actual R0.35 native pocket blends/stepped purchased-end envelope; cutter78positions and retainer-stack motion PASS'})
 for tag,status in states.items():
  src=ROOT/'cad/exports'/tag;dest=out/tag;dest.mkdir()
  files={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(src.iterdir()) if p.is_file()}
  for name in ('summary.json','FAILURE.json','producer.py','mechanisms_producer.py','bend_producer.py','relief_producer.py','tolerance_producer.py','fillet_producer.py','dependencies_sha256.json'):
   if (src/name).is_file():shutil.copyfile(src/name,dest/name)
  (dest/'local_originals_manifest.json').write_text(json.dumps(dict(status=status,files=files,originals_deleted=False),indent=2))
 for p in Path('/tmp').glob('regrip_stage1_*.log'):
  if p.stat().st_size<5_000_000:shutil.copyfile(p,out/p.name)
 binaries={str(p):dict(bytes=p.stat().st_size,sha256=digest(p)) for pattern in ('OCP/*.so','cadquery_ocp.libs/libTKBRep*','cadquery_ocp.libs/libTKBool*','cadquery_ocp.libs/libTKSTEP*') for p in Path('/tmp/regrip_stage1_ocp').glob(pattern) if p.is_file()}
 sources={str(p):digest(p) for p in (Path('/tmp/regrip_soyo_motor_interface.pdf'),Path('/tmp/regrip_skf_tolerances.pdf'),Path('/tmp/regrip_ni000032_diagram.jpg')) if p.exists()}
 meta=dict(git_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),versions={k:importlib.metadata.version(k) for k in ('cadquery-ocp','vtk')},native_CAD_binaries=binaries,downloaded_primary_source_SHA256=sources,scope='No SOFA binary or Native scene used; CAD-only. Local files unchanged/deletion forbidden; large aggregate STLs remain local ignored, individual parts/full STEP versioned.')
 (out/'toolchain_and_sources.json').write_text(json.dumps(meta,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(cases=len(states),native_binaries=len(binaries))))
if __name__=='__main__':main()
