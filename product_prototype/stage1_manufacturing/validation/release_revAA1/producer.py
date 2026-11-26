"""Case-linked, fail-closed current design audit; no physical auto-approval."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
from manufacturing_packet import ROOT
from package_stage1_definition import digest
def proof(path,expected,case=None):
 p=ROOT/path;j=json.loads(p.read_text())
 if j.get('status')!=expected:raise ValueError(f'{path}: status {j.get("status")} != {expected}')
 if case is not None and j.get('case')!=case:raise ValueError(f'{path}: wrong case')
 return j,dict(path=path,sha256=digest(p),status=expected)
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--package',required=True);p.add_argument('--review',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());package=ROOT/'cad/assembly'/a.package/'summary.json';pkg=json.loads(package.read_text());criteria=[];refs=[]
 def check(n,ok,scope):criteria.append(dict(id=n,passed=bool(ok),scope=scope))
 check('architecture_and_full_assembly',idx['part_count']==304 and not idx['collisions'] and idx['all_BRep_single_valid'],'Actual current single-valid BRep/nominal bulk common0; not physical dynamics')
 required=[('revAA_geometry1','CURRENT_GEOMETRY_AND_HEEL_TOOL_PASS',a.case),('revAA_heel_margin1','HEEL_SAMPLED_TOLERANCE_TRANSFER_PASS',a.case),('revAA_service1','SAMPLED_SERVICE_PATH_PASS',None),('revZ_subset1','REMOVAL_ONLY_CLEARANCE_TRANSFER_PASS','revZ_play_groove'),('revZ_combined_play1','COMBINED_PULLEY_PLAY_CLEARANCE_PASS','revZ_play_groove'),('revZ_form_tool1','BROAD_GROOVE_TOOL_GEOMETRY_PASS','revZ_play_groove'),('revY_torque_protocol1','TORQUE_MOTION_SCREEN_PASS','revY_nut_passage'),('revY_shaft_service2','SHAFT_HOLD_AND_SERVICE_PASS','revY_nut_passage'),('revY_drive1','AXIAL_AND_POSITIVE_TORQUE_GEOMETRY_CONTRACT_PASS',None),('revY_fastener_joints1','FASTENER_AXIAL_ENGAGEMENT_PASS','revY_nut_passage'),('revY_nut_passage1','NUT_PLAIN_PASSAGE_DESIGN_PASS','revY_nut_passage'),('revY_stock_threads1','STOCK_LENGTH_ENGAGEMENT_DESIGN_PASS','revY_nut_passage'),('revY_stock_motion1','SAMPLED_MOTION_PASS','revY_nut_passage'),('revY_stock_wire1','WIRE_ROTOR_SCREEN_PASS',None),('revY_stock_wire_long1','WIRE_ROTOR_SCREEN_PASS',None),('revY_stock_wire_short1','WIRE_ROTOR_SCREEN_PASS',None),('revY_space1','CASSETTE_SPACE_AND_WIRE_SECTOR_PASS',None)]
 for tag,status,case in required:
  try:j,r=proof('validation/'+tag+'/summary.json',status,case);refs.append(r);check(tag,True,j.get('scope','See referenced exact bounded geometry scope'))
  except (ValueError,KeyError,FileNotFoundError) as e:check(tag,False,str(e))
 try:review,r=proof('validation/'+a.review+'/summary.json','MANUFACTURING_FILE_AND_FEATURE_AUDIT_PASS',a.case);refs.append(r);check('current_BOM_face_drawing_audit',True,'Case-linked actual face/dimension/material/process requirements, NOT shop process approval')
 except (ValueError,FileNotFoundError) as e:review={};check('current_BOM_face_drawing_audit',False,str(e))
 errors=[]
 for row in pkg['part_files']:
  f=ROOT/row['path']
  if not f.is_file() or digest(f)!=row['sha256']:errors.append(row['path'])
 check('selfcontained_actual_parts_STEP_STL',pkg['case']==a.case and pkg['source_case_SHA256']==digest(src) and len(pkg['part_files'])==608 and not errors,errors)
 ap=ROOT/pkg['assembly_STEP'];check('actual_full_assembly_STEP',ap.is_file() and digest(ap)==pkg['assembly_STEP_SHA256'],'Actual kernel-written/reread assembly, not export recipe')
 for name in ('STAGE1_CURRENT_ASSEMBLY_GUIDE.md','STAGE1_CURRENT_MANUFACTURING_DATUMS.md'):
  f=ROOT/'cad/drawings'/a.package/name;check(name,f.is_file() and digest(f)==digest(ROOT/'reports'/name),'Controlled package copy equals current authority')
 check('current_BOM_unique_all_part_IDs',{r['part_ID'] for r in csv.DictReader((ROOT/pkg['BOM']).open())}==set(idx['parts']),'Actual materials/methods/tolerances and part links; physical lots NOT MEASURED')
 engineering=all(c['passed'] for c in criteria)
 # User's Stage1 is an engineering design release, BEFORE actual load,
 # single-Finger actuation and hardware manufacture. Do not silently add
 # shop/hardware approval as a prerequisite to that different scope, or
 # promote the bounded design release to a production authorization.
 acceptance=ROOT/'config/STAGE1_MANUFACTURING_ACCEPTANCE.json';accept=json.loads(acceptance.read_text()) if acceptance.exists() else {}
 approved=accept.get('case_SHA256')==digest(src) and accept.get('accepted') is True and bool(accept.get('reviewer')) and bool(accept.get('evidence_paths')) and all((ROOT/f).is_file() for f in accept.get('evidence_paths',[]))
 result=dict(status='STAGE1_DESIGN_RELEASE_PASS' if engineering else 'STAGE1_DESIGN_RELEASE_FAIL',engineering_definition_status='STAGE1_ENGINEERING_DEFINITION_PASS' if engineering else 'STAGE1_ENGINEERING_DEFINITION_FAIL',release_scope='UNPOWERED FIRST-ARTICLE ENGINEERING DESIGN ONLY',production_authorization=False,powered_or_load_authorization=False,case=a.case,criteria=criteria,manufacturing_acceptance=accept if accept else dict(state='NOT MEASURED',reason='Actual shop capability and first-article inspections NOT MEASURED; required before fabrication/powered approval, not fabricated by this Stage1 design audit.'),evidence=refs,source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_case_SHA256=digest(src),package_SHA256=digest(package),hardware='NOT MEASURED',Native_run=False,scope='Stage1 bounded engineering definition audit only. Sampled motion/clearance and conditional procurement requirements are not continuousCCD, actual load, free-spin, fatigue, shop capability or100g Holding certification. Historical results remain unchanged.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],engineering=result['engineering_definition_status'],criteria=len(criteria),failed=[r['id'] for r in criteria if not r['passed']],manufacturing_accepted=approved)))
if __name__=='__main__':main()
