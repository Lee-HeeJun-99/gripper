"""Actual bolt CAD coverage versus normalized chord-FEM traction; no exact-face claim."""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from primary_motor_bearing_wrenches import faces
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

def area(shape):
 g=GProp_GProps();BRepGProp.SurfaceProperties_s(shape,g);return g.Mass()
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_anchor36b/summary.json';cad=json.loads(cp.read_text());rows=[]
 for tag in sys.argv[2:]:
  src=ROOT/'validation/integrated'/tag/'summary.json';d=json.loads(src.read_text());assert d['candidate']==ref(cp);part=read(REPO/d['actual_part']['path']);base=read(REPO/cad['part_references']['TEST_BASE']['path']);ports=[sum(area(BRepAlgoAPI_Common(a,b).Shape()) for a in faces(part,2,60) for b in faces(base,2,60)),sum(area(f) for f in faces(part,2,80))];mapped=[p['integrated_area_mm2'] for p in d['boundary_journal']];gaps=[abs(a-b) for a,b in zip(ports,mapped)];rows.append(dict(source=ref(src),h_mm=d['h_mm'],actual_face_areas_mm2=ports,mapped_chord_face_areas_mm2=mapped,missing_or_extra_area_mm2=gaps,original_exact_area1e_minus7_mm2_pass=all(g<1e-7 for g in gaps),CAD_volume_mm3=d['CAD_volume_mm3'],mesh_volume_mm3=d['mesh_volume_mm3'],relative_volume_discrepancy=abs(d['CAD_volume_mm3']-d['mesh_volume_mm3'])/d['CAD_volume_mm3']))
 dump(out/'summary.json',dict(status='ACTUAL_P1_BOLT_CAD_TRACTION_COVERAGE_REVIEW_NOT_QUALIFIED',candidate=ref(cp),verifier=ref(out/'verifier.py'),rows=rows,exact_area_coverage_pass=all(r['original_exact_area1e_minus7_mm2_pass'] for r in rows),normalization_is_not_exact_geometry=True,physical_stack_qualified=False,whole_system_release=False,limitations=['Unit wrench and weak force/work can pass on normalized chord-limited surface despite missing actual CAD area.','This independent geometry review does not overwrite prior local force/work PASS or qualify physical pressure.']))
 print(json.dumps(rows))
if __name__=='__main__':main()
