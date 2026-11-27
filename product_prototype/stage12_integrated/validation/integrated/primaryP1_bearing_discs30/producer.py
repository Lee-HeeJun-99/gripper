"""Replace conditional point-bearing witnesses by actual finite-area CAD discs.
Nonnegative static traction witnesses, not elastic pressure or thread certification.
"""
import sys,json,time,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_bore_seating30 import planar,area_centroid
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex,BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt,gp_Circ,gp_Ax2,gp_Dir

def boundary_distance(faces,q):
 v=BRepBuilderAPI_MakeVertex(gp_Pnt(*q)).Vertex();ds=[]
 for f in faces:
  it=TopExp_Explorer(f,TopAbs_EDGE)
  while it.More():
   d=BRepExtrema_DistShapeShape(v,it.Current());d.Perform();assert d.IsDone();ds.append(d.Value());it.Next()
 return min(ds)
def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 sp=ROOT/'validation/integrated/primaryP1_bore_seating30e/summary.json';s=json.loads(sp.read_text());cad=json.loads((REPO/s['candidate']['path']).read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());rows=json.loads((REPO/s['geometry']['path']).read_text());cases=json.loads((REPO/s['numerical_cases']['path']).read_text());names={n for r in rows for f in r['bearing_footprints'] for n in [f['hardware'],f['body']]};shapes={n:read(REPO/cad['part_references'][n]['path']) for n in names};results=[];discs=[]
 dump(out/'inputs.json',dict(candidate=s['candidate'],source=ref(sp),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_bore_seating30.py')],policy='Exact circles strictly inside both finite bearing faces. Uniform pressure integrates to selected LP force and exact centroid. Overlapping discs add nonnegative pressure; no optimal/unique elastic pressure or strength claim. Bore remains ideal line and thread wrench unrestricted.'))
 for r in rows:
  assert not(ROOT/'runtime/STOP').exists();case=next(c for c in cases if c['branch']==r['branch'] and c['sign']==r['sign'] and c['LP_success']);x=case['solution'];k=0
  for f in r['bearing_footprints']:
   shift=np.array(f['shift_mm']);z=f['actual_shifted_overlap_centroid_mm'][2];hf=[translate(ff,*shift) for ff in planar(shapes[f['hardware']],z)];sf=planar(shapes[f['body']],z);expected=np.zeros(3);actual=np.zeros(3);force=0.;count=0;pressure_sum=0.;minrad=1.
   for q0 in f['actual_interior_point_force_sites_mm']:
    F=float(x[k]);k+=1;q=np.array(q0)
    if F<=0:continue
    clearance=min(boundary_distance(hf,q),boundary_distance(sf,q));assert clearance>0;radius=min(.1,clearance/4);circle=gp_Circ(gp_Ax2(gp_Pnt(*q),gp_Dir(0,0,1)),radius);disc=BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circle).Edge()).Wire()).Face();area,centroid=area_centroid(disc);errors=[]
    for fs in [hf,sf]:
     ar=0.
     for ff in fs:
      op=BRepAlgoAPI_Common(disc,ff);op.Build();assert op.IsDone();aa,cc=area_centroid(op.Shape());ar+=aa
     errors.append(abs(ar-area))
    expected+=F*q;actual+=F*centroid;force+=F;count+=1;pressure=F/area;pressure_sum+=pressure;minrad=min(minrad,radius)
    discs.append(dict(branch=r['branch'],sign=r['sign'],side=f['side'],center_mm=q.tolist(),radius_mm=radius,boundary_clearance_mm=clearance,area_mm2=area,analytic_area_error_mm2=abs(area-np.pi*radius**2),finite_face_containment_area_errors_mm2=errors,centroid_error_mm=float(np.linalg.norm(centroid-q)),force_N=F,uniform_pressure_MPa=pressure,elastic_pressure_qualified=False))
   results.append(dict(branch=r['branch'],sign=r['sign'],side=f['side'],finite_discs=count,total_compression_N=force,finite_traction_first_moment_error_Nmm=float(np.max(abs(actual-expected))),pressure_sum_upper_bound_MPa=pressure_sum,min_radius_mm=minrad if count else None,pressure_is_unique=False,allowable_available=False))
 dump(out/'finite_pressure_discs.json',discs)
 checks=dict(all56footprint_results=len(results)==56,positive_finite_pressure=bool(discs) and all(d['area_mm2']>0 and d['uniform_pressure_MPa']>0 for d in discs),all_actual_CAD_containment=all(max(d['finite_face_containment_area_errors_mm2'])<1e-9 for d in discs),exact_disc_area_centroid=all(d['analytic_area_error_mm2']<1e-10 and d['centroid_error_mm']<1e-8 for d in discs),all_traction_force_moments=all(r['finite_traction_first_moment_error_Nmm']<1e-8 for r in results))
 dump(out/'summary.json',dict(status='ACTUAL_P1_SHIFTED_BEARING_FINITE_AREA_STATIC_TRACTION_WITNESSES' if all(checks.values()) else 'ACTUAL_P1_FINITE_AREA_BEARING_WITNESS_FAIL',candidate=s['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=results,finite_discs=ref(out/'finite_pressure_discs.json'),disc_count=len(discs),max_conditional_pressure_sum_upper_bound_MPa=max(r['pressure_sum_upper_bound_MPa'] for r in results),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,limitations=['Finite discs are derived conditional positive traction witnesses for LP bearing forces; chosen radius is mathematical support construction, not material fitting, design tolerance, strength criterion or elastic contact solution.','Actual finite bearing area can carry these conditional resultants statically, but bore remains zero-area ideal line and thread shear/tilt constitutive response unknown. No full product physical equilibrium, preload/rest setting, pin split, support solve, anchor, convergence, energy or release. Hardware NOT_MEASURED.']))
 print(json.dumps(dict(checks=checks,discs=len(discs))));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
