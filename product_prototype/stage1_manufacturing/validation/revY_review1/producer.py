"""Fail-closed traceability/actual-feature review, NOT automatic shop approval."""
import argparse,ast,csv,hashlib,json,shutil
from pathlib import Path
from manufacturing_packet import ROOT
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--packet',required=True);p.add_argument('--faces',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());bp=ROOT/'bom'/a.packet/'STAGE1_BOM.csv';rows=list(csv.DictReader(bp.open()));fp=ROOT/'validation'/a.faces/'FACE_FEATURES.csv';faces=list(csv.DictReader(fp.open()));dp=ROOT/'cad/drawings'/a.packet/'summary.json';draw=json.loads(dp.read_text());checks=[]
 def check(name,ok,detail):checks.append(dict(check=name,passed=bool(ok),detail=detail))
 check('BOM_unique_actual_IDs',len(rows)==len(idx['parts']) and {r['part_ID'] for r in rows}==set(idx['parts']),len(rows))
 errors=[]
 for r in rows:
  n=r['part_ID'];v=idx['parts'][n];f=ROOT/r['STEP'];stl=ROOT/r['STL']
  if not f.is_file() or not stl.is_file() or r['STEP_SHA256']!=digest(f) or v['sha256']!=r['STEP_SHA256']:errors.append(n)
 check('actual_part_STEP_STL_and_SHA_links',not errors,errors)
 made=[r for r in rows if not r['part_ID'].startswith(('F1_','F2_')) and r['make_or_buy'] in ('MAKE','FINISH PURCHASED')]
 missing=[r['part_ID'] for r in made if not r['material'] or not r['method'] or not r['interface_notes'] or not (ROOT/'cad/drawings'/a.packet/(r['part_ID']+'.svg')).is_file()]
 check('all_made_trimmed_material_process_interface_drawings',len(made)>0 and not missing and {r['part_ID'] for r in made}==set(draw['drawings']),missing)
 declared=json.loads((ROOT/'validation'/a.faces/'summary.json').read_text())
 check('actual_faces_complete',len(faces)==declared['face_count'] and {r['part_ID'] for r in faces}=={r['part_ID'] for r in made},len(faces))
 check('actual_face_catalogue_matches_current_part_SHA',all(r['STEP_SHA256']==idx['parts'][r['part_ID']]['sha256'] for r in faces),'Every recorded face linked to actual part source')
 def surf(n,kind,key,value):return any(r['part_ID']==n and kind in r['surface'] and abs(ast.literal_eval(r['parameters']).get(key,-999)-value)<1e-6 for r in faces)
 for n,d in [('F0_SHAFT',4.986),('F0_PEDESTAL_L',16.03),('F0_PEDESTAL_R',16.03),('F0_DRUM',8.10),('F0_IDLER',3.040)]:check(n+'_actual_cylinder',surf(n,'Cylinder','diameter_mm',d),d)
 for n in ('F0_DRUM','F0_IDLER'):check(n+'_actual_groove_profile',surf(n,'Torus','minor_radius_mm',.30) and surf(n,'Torus','major_radius_mm',11.28),'Actual0.30minor/11.28major, not superseded0.28')
 check('DIN7991_actual90deg_countersink',surf('F0_TERMINAL_FRONT','Cone','included_angle_deg',90),'Actual front bearing cone retained')
 check('two_end_tendons_purchased_as_whole',sum(r['part_ID'].endswith('TENDON_WIRE') and r['purchase_quantity']=='1' for r in rows)==3 and all(r['purchase_quantity']=='0' for r in rows if 'FACTORY_NIPPLE' in r['part_ID']),'Three whole cables, no loose swage-end purchases')
 check('current_review_packet_identifies_itself',draw['case']==a.case and draw['shop_release'] is False,'No self-promotion of review drawings to shop approval')
 issues=[dict(id='shop_process_acceptance',state='NOT MEASURED',reason='Review drawings/MBD do not by themselves verify actual micro-machining reach, thin0.45mm rim process capability or complete shop dimensional acceptance.'),dict(id='full_tolerance_clearance',state='OPEN',reason='Nominal and wire-size/length extrema tested; finish retainer stack-envelope disposition and coupled fit/geometry tolerance review before shop release.'),dict(id='physical_strength',state='NOT MEASURED_STAGE2',reason='No clamp preload/pin shear/swage pullout/fatigue/drive performance measurement; not a Stage1 manufacturing geometry PASS.')]
 result=dict(status='MANUFACTURING_FILE_AND_FEATURE_AUDIT_PASS' if all(r['passed'] for r in checks) else 'MANUFACTURING_FILE_AND_FEATURE_AUDIT_FAIL',case=a.case,checks=checks,open_issues=issues,shop_release=False,stage1_release=False,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in (src,bp,fp,dp)},scope='Actual source/part/BOM/drawing/hidden-face dimensions and declared requirements checked. This bounded automatic audit is NOT a process-capability or physical certification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],checks=len(checks),failed=[r for r in checks if not r['passed']],open_issues=issues)))
if __name__=='__main__':main()
