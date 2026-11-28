"""Independent reimported installed-pin retention geometry and finite forming/access audit.
No supplier pliers dimensions/force claim; jaw envelopes are explicit proposed access gauges.
"""
import sys,json,math,shutil,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,overlap,bounds,volume,solid_count,translate,box
from OCP.BRepCheck import BRepCheck_Analyzer
from primary_splitpin61c import pin_local,world
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_splitpin61c/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(q) for n,q in parts.items()};anchors=json.loads((REPO/cad['anchors']['path']).read_text())['groups'];results=[];sequence=[];tools=[];checks={}
def hits(q,excluded):
 r=[];b=bounds(q)
 for n,s in parts.items():
  if n in excluded or not overlap(b,bb[n]):continue
  assert not(ROOT/'runtime/STOP').exists();v=common(q,s)
  if v>1e-8:r.append(dict(part=n,intersection_mm3=v))
 return r
for g in anchors:
 n=g['pin'];d=np.array([0.,1.,0.]) if n.startswith('ROOT') else np.array([-1. if g['x']==7 else 1.,0,0]);pin=parts[n];host=parts[g['body']];gen=world(pin_local(45),g);err=volume(gen)+volume(pin)-2*common(gen,pin)
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
 # Local proposed grip/handle corridors: eye from outside along axis, leg forming from a lateral corridor below bridge.
 # Grip corridor contains target pin deliberately. Other product geometry may not be excluded.
 eye=world(box(-27.9,-.6,-1.2,23.4,1.2,2.4),g)
 legs=box(35,3.1,-2.6,26.6,2.3,1.2) if n.startswith('ROOT') else box(-3.9 if g['x']==-7 else 1.6,-46.5,29.4,2.3,26.6,1.2)
 for label,q in [('eye_pull_jaw_2.4x1.2_continuous20mm',eye),('splay_leg_jaw_2.3x1.2_lateral20mm',legs)]:tools.append(dict(pin=n,tool=label,hits=hits(q,[n]),gauge_bounds_mm=bounds(q),supplier_tool_qualified=False))
 # A material slice through actual split D shaft, not full circular upper envelope.
 # Whole-body intersection volume / thickness is an independent area integral.
 slab=world(box(-.05,-1,-1,.1,2,2),g);area=common(slab,pin)/.1;rad=.45;h=.02;analytic=math.pi*rad**2-2*(h*math.sqrt(rad*rad-h*h)+rad*rad*math.asin(h/rad))
 results.append(dict(pin=n,actual_volume_mm3=volume(pin),reimport_geometry_difference_mm3=err,actual_split_section_mm2=area,analytic_split_section_mm2=analytic,split_section_relative_error=abs(area-analytic)/analytic,solid_cylinder_overestimate_fraction=(math.pi*rad**2-area)/area,axial_stops=stops,initial_contact_stiffness='zero inside finite clearance; no preload/tie or capacity inferred',actual_strength_MPa=None))
checks=dict(source_and83part_hashes=True,three_installed_single_valid_solids=all(solid_count(parts[g['pin']])==1 and BRepCheck_Analyzer(parts[g['pin']]).IsValid() for g in anchors),reimported_formed_geometry_matches=all(abs(q['reimport_geometry_difference_mm3'])<1e-6 for q in results),actual_split_section_integral=all(q['split_section_relative_error']<1e-6 for q in results),all_six_axial_stops_bracketed=all(q['bracketed'] for r in results for q in r['axial_stops']),sampled_straight_insert_bend_reverse_clear=all(not q['hits'] and q.get('valid',True) and q.get('solids',1)==1 for q in sequence),proposed_access_gauges_clear=all(not q['hits'] for q in tools))
dump(out/'sequence.json',sequence);dump(out/'tools.json',tools)
dump(out/'summary.json',dict(status='ACTUAL_P1_INSTALLED_PIN_GEOMETRY_LOCAL_PASS_NOT_STRENGTH' if all(checks.values()) else 'ACTUAL_P1_INSTALLED_PIN_GEOMETRY_OR_ACCESS_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),geometry_model=ref(ROOT/'scripts/primary_splitpin61c.py'),checks={k:bool(v) for k,v in checks.items()},pin_results=results,sequence=ref(out/'sequence.json'),tools=ref(out/'tools.json'),finite_sequence_poses=len(sequence),newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0,whole_system_release=False,limitations=['Nominal proposed formed split pin, source-size only; eye circular-wire and angular leg transitions are not exact supplier CAD/forming/radius tolerances','Sampled angles/positions are not full surface CCD or a material forming/plastic-damage solution','Jaw boxes are explicit product access gauges, not source-backed plier geometry/handle/strength/usable tool certification','Finite interference brackets establish geometric retention only; no allowable force, elastic finite contact or detachment certificate','Actual preload,60degreeindex/helicallead/nutbacklash,finitehostattachment/source-minimumstrength/mesh1percent/time.1percent/globalenergy and final3Finger remain']))
print(json.dumps(dict(checks=checks,pin_results=results,sequence_hits=[q for q in sequence if q['hits']],tool_hits=[q for q in tools if q['hits']])));raise SystemExit(0 if all(checks.values()) else 2)
