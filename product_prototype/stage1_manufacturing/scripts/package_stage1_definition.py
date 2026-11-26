"""Self-contained actual CAD/MBD package, no CAD regeneration or auto approval."""
import argparse,csv,hashlib,json,shutil
from manufacturing_packet import ROOT
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--packet',required=True);p.add_argument('--faces',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
 source=ROOT/'cad/exports'/a.case;idx=json.loads((source/'summary.json').read_text());parts=ROOT/'cad/parts'/a.tag;parts.mkdir(exist_ok=False);assembly=ROOT/'cad/assembly'/a.tag;assembly.mkdir(exist_ok=False);draw=ROOT/'cad/drawings'/a.tag;draw.mkdir(exist_ok=False);bom=ROOT/'bom'/a.tag;bom.mkdir(exist_ok=False);rows=list(csv.DictReader((ROOT/'bom'/a.packet/'STAGE1_BOM.csv').open()));manifest=[]
 for r in rows:
  n=r['part_ID'];v=idx['parts'][n]
  for ext in ('.step','.stl'):
   src=(ROOT/v['path']).with_suffix(ext);dst=parts/(n+ext);shutil.copyfile(src,dst);assert digest(src)==digest(dst);manifest.append(dict(path=str(dst.relative_to(ROOT)),sha256=digest(dst),bytes=dst.stat().st_size))
  r['STEP']=str((parts/(n+'.step')).relative_to(ROOT));r['STL']=str((parts/(n+'.stl')).relative_to(ROOT))
 for src in (ROOT/'cad/drawings'/a.packet).glob('*.svg'):
  text=src.read_text().replace('THREE-VIEW REVIEW — NOT SHOP RELEASED','CONTROLLED MBD CANDIDATE — NOT LOAD QUALIFIED').replace('BRep STEP is authority for curved/hidden surfaces; this all-edge view is not a complete fabrication approval.','Use CONTROLLED native STEP + face catalogue + datum/fit notes; this view alone is insufficient.').replace('Supplier bend-radius/terminal-length disposition and independent drawing review remain OPEN.','See actual max-wire, matched-trim, sourced-cutter and manufacturing review dispositions; no hardware certification.')
  (draw/src.name).write_text(text)
 # Keep original source provenance, but every manufacturing lookup resolves
 # to the self-contained part set rather than requiring old trial folders.
 face_rows=list(csv.DictReader((ROOT/'validation'/a.faces/'FACE_FEATURES.csv').open()))
 for r in face_rows:r['SOURCE_STEP']=r['STEP'];r['STEP']=str((parts/(r['part_ID']+'.step')).relative_to(ROOT))
 with (draw/'FACE_FEATURES.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(face_rows[0]));w.writeheader();w.writerows(face_rows)
 shutil.copyfile(ROOT/'bom'/a.packet/'MANUFACTURING_INTERFACES.json',bom/'MANUFACTURING_INTERFACES.json')
 with (bom/'STAGE1_BOM.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 shutil.copyfile(source/'ASSEMBLY.step',assembly/'ASSEMBLY.step')
 local_stl=source/'ASSEMBLY.stl';(assembly/'LOCAL_AGGREGATE_STL.json').write_text(json.dumps(dict(path=str(local_stl.relative_to(ROOT)),bytes=local_stl.stat().st_size,sha256=digest(local_stl),reason='Actual aggregate STL remains local, not Git-tracked >=50MB. All individual part STLs are in self-contained package.'),indent=2))
 for name in ('STAGE1_CURRENT_ASSEMBLY_GUIDE.md','STAGE1_CURRENT_MANUFACTURING_DATUMS.md'):
  shutil.copyfile(ROOT/'reports'/name,draw/name)
 result=dict(status='SELF_CONTAINED_ACTUAL_DESIGN_PACKAGE_GENERATED',case=a.case,tag=a.tag,part_count=len(rows),part_files=manifest,BOM=str((bom/'STAGE1_BOM.csv').relative_to(ROOT)),assembly_STEP=str((assembly/'ASSEMBLY.step').relative_to(ROOT)),assembly_STEP_SHA256=digest(assembly/'ASSEMBLY.step'),drawings=len(list(draw.glob('*.svg'))),source_case_SHA256=digest(source/'summary.json'),shop_process_certification=False,stage1_release=False,scope='Exact copies of actual indexed CAD, not regenerated RevH. Controlled package CANDIDATE only; separate release gate required. No physical load/manufacturing capability certification.')
 (assembly/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,assembly/'producer.py');print(json.dumps(dict(status=result['status'],parts=len(rows),CAD_files=len(manifest),drawings=result['drawings'])))
if __name__=='__main__':main()
