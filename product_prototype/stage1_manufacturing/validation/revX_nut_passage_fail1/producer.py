"""Independent native plain-passage bound, not a fake helical contact model."""
import argparse,json,shutil
from incremental_stage1 import ROOT,read,sha
from build_stage1 import box,cyl,cut,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';j=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);shaft=read(ROOT/j['parts']['F0_SHAFT']['path']);span=j['design_geometry'].get('shaft_plain_passage_Y_mm',[-18,-12.4]);band=BRepAlgoAPI_Common(shaft,box(70,span[0],10,20,span[1]-span[0],20)).Shape();go=cyl(2.21,(80,span[0]-.01,20),span[1]-span[0]+.02,(0,1,0));nogo=cyl(2.35,(80,span[0]-.01,20),span[1]-span[0]+.02,(0,1,0));outside=volume(cut(band,go));favourable=volume(cut(band,nogo));defined='shaft_plain_passage_D_mm' in j['design_geometry']
 result=dict(status='NUT_PLAIN_PASSAGE_DESIGN_PASS' if defined and abs(outside)<1e-7 else 'NUT_PLAIN_PASSAGE_CERTIFICATE_FAIL',case=a.case,actual_native_passage_span_Y_mm=span,actual_grip_outside_GO4_42_mm3=outside,actual_grip_outside_largest_accepted_NOGO4_70_mm3=favourable,additional_nut_acceptance=dict(plain_GO_mm=4.42,plain_NOGO_mm=4.70,actual_thread_gauge='M5x0.5-6H REQUIRED',hardware_measurements='NOT MEASURED'),scope='A4.42GO-passing nut necessarily admits a shaft contained in4.40 cylinder before thread entry. Old5mm-major-hole collision-free CAD is NOT such a certificate; an overlapping minor-bore witness alone is not a physical force/seizure experiment. Threading on6g/6H boss requires standard mating/gauge, not modeled helical force. Acceptance limits are design requirements, not asserted supplier minor diameter.',input_sha256=sha(src),stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result))
if __name__=='__main__':main()
