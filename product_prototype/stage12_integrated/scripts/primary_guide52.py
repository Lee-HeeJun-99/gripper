"""Same P1: two integral downward tongues and open vertical support mortises.
Positive bearing antiyaw design,not assumed friction/preload/loaded equilibrium.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
TAG='primaryP1_guide52'
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports'/TAG;out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_thread49f/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),old['assembly'],old['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()};rail=parts['BENCH_ANCHOR_RAIL'];stand=parts['BENCH_SUPPORT']
 for y in [-58.,39.]:
  # Machining intent: tongues integral to receiver,slots open upward/downward.
  # No new fastener chain;original four bolt/nut/key/pin stacks retained.
  rail=fuse(rail,box(-78,y-3,68,15,6,6));rail=fuse(rail,box(-78,y-3,50,4,6,20))
  stand=cut(stand,box(-78.1,y-3.1,49,4.2,6.2,18))
 changed=[]
 for n,s in [('BENCH_ANCHOR_RAIL',rail),('BENCH_SUPPORT',stand)]:
  s=canonical(s);export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=old['part_references'][n]))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 # New geometry only changes two actual solids;all126 otherpart pairs preserved.
 for n,m in itertools.combinations(parts,2):
  if n not in ['BENCH_ANCHOR_RAIL','BENCH_SUPPORT'] and m not in ['BENCH_ANCHOR_RAIL','BENCH_SUPPORT']:continue
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8 or v < -1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=TAG
 for r in bom['parts']:
  r['STEP']=refs[r['part_ID']]
  if r['part_ID'] in ['BENCH_ANCHOR_RAIL','BENCH_SUPPORT']:r.update(interface='Two integral4x6mm vertical tongues/4.2x6.2mm open mortises;97mm centre separation;finite.1mm sideclearance;no fixedrotation',material='UNCHANGED unqualified support material;new notch/bearing/ligament/process/allowables require revalidation')
 dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(cp),producer=ref(out/'producer.py'),tongue_x_mm=[-78,-74],tongue_y_centres_mm=[-58,39],tongue_z_mm=[50,70],connector_x_mm=[-78,-63],connector_z_mm=[68,74],slot_x_mm=[-78.1,-73.9],slot_half_y_mm=3.1,slot_z_mm=[49,67],nominal_vertical_engagement_mm=16,sideclearance_mm=.1,assembly='Receiver tongue inserted downward into top-open standmortises beforefour bolts/nuts/driver/key/pins;no closedundercut',standard_fasteners_preserved=True,old_standard_sources=old.get('inputs'),source_material_minimum_MPa=None,loaded_contact_capacity_N=None,ultimate_host_fixed=False))
 good=not hits and all(r['valid'] and r['solids']==1 for r in changed);d=dict(old);d.update(revision=TAG,status='ACTUAL_P1_INTEGRAL_GUIDE_GEOMETRY_LOCAL_PASS_NOT_RELEASE' if good else 'ACTUAL_P1_INTEGRAL_GUIDE_GEOMETRY_FAIL',parent=ref(cp),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,unchanged_part_STEP_count=126,design_change='Same128partP1 gains two integral receiver tongues and open standmortises for positive relative antiyaw bearing;all126others unchanged',not_qualified=old['not_qualified']+['Newguide finitebacklash/contacttakeup/coupledthreadcontact/strength/notch/ligament/operatingfield/mass/Stage1revalidation incomplete;oldFEinvalidated'])
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],changed=changed,hits=hits,exact_pairs=pairs)),flush=True);raise SystemExit(0 if good else 2)
if __name__=='__main__':main()
