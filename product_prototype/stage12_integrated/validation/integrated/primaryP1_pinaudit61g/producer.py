"""Independent reimported installed-pin retention geometry and finite forming/access audit.
No supplier pliers dimensions/force claim; jaw envelopes are explicit proposed access gauges.
"""
import sys,json,math,shutil,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,overlap,bounds,volume,solid_count,translate,box
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN,TopAbs_OUT
def precise(s):
 p=GProp_GProps();e=BRepGProp.VolumeProperties_s(s,p,1e-10,True,False);c=p.CentreOfMass();return np.array([p.Mass(),c.X(),c.Y(),c.Z()]),e
from primary_splitpin61g import pin_local,world
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_splitpin61g/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(q) for n,q in parts.items()};anchors=json.loads((REPO/cad['anchors']['path']).read_text())['groups'];results=[];sequence=[];tools=[];checks={}
def hits(q,excluded):
 r=[];b=bounds(q)
 for n,s in parts.items():
  if n in excluded or not overlap(b,bb[n]):continue
  assert not(ROOT/'runtime/STOP').exists();v=common(q,s)
  if v>1e-8:r.append(dict(part=n,intersection_mm3=v))
 return r
for g in anchors:
 n=g['pin'];d=np.array([0.,1.,0.]) if n.startswith('ROOT') else np.array([-1. if g['x']==7 else 1.,0,0]);pin=parts[n];host=parts[g['body']];gen=world(pin_local(45),g)
 gp,ge=precise(gen);ip,ie=precise(pin);err=float(np.max(np.abs(gp-ip)));bounderr=float(np.max(np.abs(np.array(bounds(gen))-np.array(bounds(pin)))))
 # Actual material/empty probes independently detect the previously fused shaft failure.
 origin=np.array([g.get('anchor_x',g['x']),g['anchor_y_mm'],g['top']+1]);normal=np.array([1.,0,0]) if n.startswith('ROOT') else np.array([0.,1.,0]);probes=[]
 for u in [-.1,-.01,0,.01,.1]:
  p=origin+normal*u;state=BRepClass3d_SolidClassifier(pin,gp_Pnt(*map(float,p)),1e-8).State();expected=TopAbs_OUT if abs(u)<.02 else TopAbs_IN;probes.append(dict(offset_mm=u,expected='OUT' if abs(u)<.02 else 'IN',matches=bool(state==expected)))
 for u in [20,10,5,3,1,0]:
  q=translate(world(pin_local(0),g),*map(float,-u*d));sequence.append(dict(pin=n,operation='straight_insert_or_reverse_extract',distance_mm=u,hits=hits(q,[n])))
 for a in [0,5,10,15,20,25,30,35,40,45]:
  q=world(pin_local(a),g);sequence.append(dict(pin=n,operation='bend_or_reverse_straighten',bend_deg=a,hits=hits(q,[n]),valid=bool(BRepCheck_Analyzer(q).IsValid()),solids=solid_count(q)))
 # Two axial withdrawal directions, actual stop contact bracket using whole host solid.
 stops=[]
 for sign,label in [(-1,'splayed_legs'),(1,'eye')]:
  def iv(u):return common(translate(pin,*map(float,sign*u*d)),host)
  lo=0.;hi=4.
  if iv(hi)<=1e-8:stops.append(dict(stop=label,bracketed=False,max_test_mm=hi));continue
  for _ in range(20):
   m=(lo+hi)/2
   if iv(m)>1e-8:hi=m
   else:lo=m
  stops.append(dict(stop=label,bracketed=True,free_translation_bracket_mm=[lo,hi],intersection_at_upper_mm3=iv(hi),contact_capacity_N=None))
 # Local proposed grip/handle corridors: eye from outside along axis, leg forming through the new Root bridge notch / clear Cap top.
 # Grip corridor contains target pin deliberately. Other product geometry may not be excluded.
 eye=world(box(-27.9,-.6,-1.2,23.4,1.2,2.4),g)
 legs=box(58.4,3.1,-2.6,3.2,2.3,32.6) if n.startswith('ROOT') else box(-3.9 if g['x']==-7 else 1.6,-23.1,29.4,2.3,3.2,25.6)
 for label,q in [('eye_pull_jaw_2.4x1.2_continuous20mm',eye),('splay_leg_top_access_3.2x2.3',legs)]:tools.append(dict(pin=n,tool=label,hits=hits(q,[n]),gauge_bounds_mm=bounds(q),supplier_tool_qualified=False))
 # A material slice through actual split D shaft, not full circular upper envelope.
 # Whole-body intersection volume / thickness is an independent area integral.
 slab=world(box(-.05,-1,-1,.1,2,2),g);area=common(slab,pin)/.1;rad=.45;h=.02;analytic=math.pi*rad**2-2*(h*math.sqrt(rad*rad-h*h)+rad*rad*math.asin(h/rad))
 results.append(dict(pin=n,actual_volume_mm3=volume(pin),reimport_adaptive_volume_COM_max_abs_error=err,reimport_bounds_max_abs_error_mm=bounderr,adaptive_integration_errors=[ge,ie],material_probes=probes,actual_split_section_mm2=area,analytic_split_section_mm2=analytic,split_section_relative_error=abs(area-analytic)/analytic,solid_cylinder_overestimate_fraction=(math.pi*rad**2-area)/area,axial_stops=stops,initial_contact_stiffness='zero inside finite clearance; no preload/tie or capacity inferred',actual_strength_MPa=None))
checks=dict(source_and83part_hashes=True,three_installed_single_valid_solids=all(solid_count(parts[g['pin']])==1 and BRepCheck_Analyzer(parts[g['pin']]).IsValid() for g in anchors),reimport_adaptive_integrals_bounds_and_split_probes_match=all(q['reimport_adaptive_volume_COM_max_abs_error']<1e-6 and q['reimport_bounds_max_abs_error_mm']<1e-6 and all(p['matches'] for p in q['material_probes']) for q in results),actual_split_section_integral=all(q['split_section_relative_error']<1e-6 for q in results),all_six_axial_stops_bracketed=all(q['bracketed'] for r in results for q in r['axial_stops']),sampled_straight_insert_bend_reverse_clear=all(not q['hits'] and q.get('valid',True) and q.get('solids',1)==1 for q in sequence),proposed_access_gauges_clear=all(not q['hits'] for q in tools))
dump(out/'sequence.json',sequence);dump(out/'tools.json',tools)
dump(out/'summary.json',dict(status='ACTUAL_P1_INSTALLED_PIN_GEOMETRY_LOCAL_PASS_NOT_STRENGTH' if all(checks.values()) else 'ACTUAL_P1_INSTALLED_PIN_GEOMETRY_OR_ACCESS_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),geometry_model=ref(ROOT/'scripts/primary_splitpin61g.py'),checks={k:bool(v) for k,v in checks.items()},pin_results=results,sequence=ref(out/'sequence.json'),tools=ref(out/'tools.json'),finite_sequence_poses=len(sequence),newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0,whole_system_release=False,limitations=['Nominal proposed formed split pin, source-size only; eye circular-wire and angular leg transitions are not exact supplier CAD/forming/radius tolerances','Sampled angles/positions are not full surface CCD or a material forming/plastic-damage solution','Jaw boxes are explicit product access gauges, not source-backed plier geometry/handle/strength/usable tool certification','Adaptive mass/COM/bounds and sampled material probes are reimport checks; failed coincident whole-shape Boolean comparison61c/d is retained and NOT a shape-equivalence certificate','Finite interference brackets establish geometric retention only; no allowable force, elastic finite contact or detachment certificate','Actual preload,60degreeindex/helicallead/nutbacklash,finitehostattachment/source-minimumstrength/mesh1percent/time.1percent/globalenergy and final3Finger remain']))
print(json.dumps(dict(checks=checks,pin_results=results,sequence_hits=[q for q in sequence if q['hits']],tool_hits=[q for q in tools if q['hits']])));raise SystemExit(0 if all(checks.values()) else 2)
