"""Compare NEW actual22 coarse bearing patches with exact saved same-part CAD.
Global tetra-volume PASS is not finite bearing-face 1% geometry convergence.
"""
import json,sys,shutil,math
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_front_h5_2/summary.json';f=json.loads(src.read_text());cs=REPO/f['candidate']['path'];cad=json.loads(cs.read_text());ws=ROOT/'validation/integrated/primaryP1_retention_witness4/summary.json';w=json.loads(ws.read_text());old=json.loads((REPO/w['candidate']['path']).read_text());rows=[]
 for i,station in enumerate(w['stations']):
  names=['OPEN_FRAME','GROUND_PLATE',f'GROUND_BOLT_{i}',f'GROUND_NUT_{i}'];assert all(cad['part_references'][n]==old['part_references'][n] and sha(REPO/cad['part_references'][n]['path'])==cad['part_references'][n]['SHA256'] for n in names);idx=f['bolt_names'].index(f'GROUND{i}');mesh=np.array(f['bearing_areas_head_nut_mm2'][idx]);exact=np.array(station['footprints_mm2'])[[1,0]];err=mesh/exact-1
  polyfactor=16*math.sin(2*math.pi/16)/(2*math.pi);hexarea=math.sqrt(3)/2*8**2;pred=np.array([hexarea-polyfactor*math.pi*2.75**2,polyfactor*math.pi*(4.25**2-2.75**2)])
  rows.append(dict(station=i,parts={n:cad['part_references'][n] for n in names},area_order=['nut_Ground','head_Frame'],exact_CAD_area_mm2=exact.tolist(),coarse_mesh_area_mm2=mesh.tolist(),relative_error=err.tolist(),predicted_16_edge_circle_area_mm2=pred.tolist(),polygon_prediction_relative=float(np.max(abs(mesh/pred-1))),passes_existing_one_percent=bool(np.max(abs(err))<.01)))
 maxerr=max(max(abs(np.array(r['relative_error']))) for r in rows);result=dict(status='ACTUAL_P1_COARSE_BEARING_FOOTPRINT_ONE_PERCENT_FAIL' if maxerr>=.01 else 'ACTUAL_P1_COARSE_BEARING_FOOTPRINT_PASS',candidate=f['candidate'],source=ref(src),exact_same_part_source=ref(ws),verifier=ref(out/'verifier.py'),rows=rows,maximum_absolute_relative_error=float(maxerr),one_percent_limit=.01,checks=dict(part_identity=True,polygon_cause_verified=all(r['polygon_prediction_relative']<1e-8 for r in rows),one_percent_footprints=maxerr<.01),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['ExactsamepartCADpatchesandindependentarea/overlapformulaversusNEWcoarsemeshtriangles. Thisisageometriccontactpatchcontrast,notelasticstressmeshconvergence.','No material/density/forcefittingandnoremeshorcriteriarelaxation. ActualcoarseKKTcanclosethisdiscretizationwhilefinitebearingareasremainunqualified.','Do notauto-retryfine/gap/420s; nextstrategyneedsactualfixedpointandfocusedgeometry/meshplan.']);result['checks']={k:bool(v) for k,v in result['checks'].items()};dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if maxerr<.01 else 2)
if __name__=='__main__':main()
