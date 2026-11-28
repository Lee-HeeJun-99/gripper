"""Independent actual STEP radii and plug cross sections; no manufacturing certification."""
import sys,json,math,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,common,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Torus
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_round64c/summary.json';d=json.loads(cp.read_text());groups=json.loads((REPO/d['anchors']['path']).read_text())['groups'];rows=[]
r=.15;theory=math.sqrt(3)/2*2.4**2-6*r*r*(1/math.sqrt(3)-math.pi/6)
for g in groups:
 assert not(ROOT/'runtime/STOP').exists();f=REPO/d['part_references'][g['name']]['path'];assert sha(f)==d['part_references'][g['name']]['SHA256'];s=read(f);ex=TopExp_Explorer(s,TopAbs_FACE);radii=[];minor=[]
 while ex.More():
  face=TopoDS.Face_s(ex.Current());ex.Next();a=BRepAdaptor_Surface(face)
  if a.GetType()==GeomAbs_Cylinder:radii.append(a.Cylinder().Radius())
  if a.GetType()==GeomAbs_Torus:minor.append(a.Torus().MinorRadius())
 sections=[]
 for y in g['ys']:
  x=g['x'];z=g['headtop']-.75;area=common(s,box(x-1.6,y-1.6,z,3.2,3.2,.02))/.02;sections.append(dict(x_mm=x,y_mm=y,z_mm=z,measured_section_area_mm2=area,analytic_rounded_hex_area_mm2=theory,relative_error=abs(area/theory-1)))
 checks=dict(six_external_corner_cylinders_per_plug=sum(abs(v-.15)<1e-7 for v in radii)==12,actual_root_minor_radius_present=any(abs(v-.10)<1e-7 for v in radii+minor),section_area=all(q['relative_error']<1e-7 for q in sections))
 rows.append(dict(part=g['name'],STEP=ref(f),cylindrical_surface_radii_mm=radii,toroidal_minor_radii_mm=minor,sections=sections,checks=checks))
checks=all(all(r['checks'].values()) for r in rows);dump(out/'summary.json',dict(status='ACTUAL_ROUNDED_KEEPER_SECTION_RADII_VERIFIED' if checks else 'ACTUAL_ROUNDED_KEEPER_SECTION_RADII_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),rows=rows,all_checks=checks,process_qualified=False,capacity_qualified=False,newly_qualified_system_gate_ids=[],whole_system_release=False));print(json.dumps(rows));raise SystemExit(0 if checks else 2)
