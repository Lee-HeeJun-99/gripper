"""Same P1 receiver: integral open-top, corner-relieved nut cages and bench ports.
Not a thread tie, bolt lock, external fixture, or strength qualification.
"""
import json,sys,shutil,itertools,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from mechanisms_stage1 import hex_axis
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
 assert not(ROOT/'runtime/STOP').exists()
 out=ROOT/'cad/exports/primaryP1_nutcapture43b';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_anchor36b/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 rail=parts['BENCH_ANCHOR_RAIL'];before=volume(rail);stations=[(-44,34),(86,34),(21,-53)]
 for x,y in stations:
  # Circular outer boss blends into existing receiver top, open pocket above
  # original nut bearing seat. Corner relief permits circular cutter access.
  boss=cyl(7,(x,y,73.9),5.3)
  pocket=hex_axis((x,y,73.89),(0,0,1),8.2,5.41)
  for k in range(6):
   t=k*math.pi/3;r=8.2/math.sqrt(3)
   pocket=fuse(pocket,cyl(.6,(x+r*math.cos(t),y+r*math.sin(t),73.89),5.41))
  rail=fuse(rail,cut(boss,pocket))
 ports=[(-59,-58),(101,-58),(-59,39),(101,39)]
 for x,y in ports:rail=cut(rail,cyl(2.75,(x,y,65.9),8.2))
 rail=canonical(rail);export(rail,out/'BENCH_ANCHOR_RAIL');parts['BENCH_ANCHOR_RAIL']=read(out/'BENCH_ANCHOR_RAIL.step');refs['BENCH_ANCHOR_RAIL']=ref(out/'BENCH_ANCHOR_RAIL.step')
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_nutcapture43b'
 for row in bom['parts']:
  row['STEP']=refs[row['part_ID']]
  if row['part_ID']=='BENCH_ANCHOR_RAIL':row['interface']='Integral 8.2AF corner-relieved top nut cages;four dia5.5 external mounting ports. No external support supplied;material/process/strength unqualified.'
 dump(out/'BOM.json',bom)
 valid=bool(BRepCheck_Analyzer(rail).IsValid());solids=solid_count(rail)
 changed=[dict(part_ID='BENCH_ANCHOR_RAIL',STEP=refs['BENCH_ANCHOR_RAIL'],STL=ref(out/'BENCH_ANCHOR_RAIL.stl'),parent=old['part_references']['BENCH_ANCHOR_RAIL'],valid=valid,solids=solids,volume_mm3=volume(rail),parent_volume_mm3=before)]
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),standard_source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),cages=dict(stations_xy_mm=stations,outer_radius_mm=7,pocket_AF_mm=8.2,corner_cutter_radius_mm=.6,z_top_mm=79.2,nut_seat_z_mm=74),external_mount_ports=dict(xy_mm=ports,diameter_mm=5.5,through_z_mm=[66,74],external_support=None),criteria=dict(intersection_mm3_max=1e-8)))
 r=dict(old);r.update(revision='primaryP1_nutcapture43b',status='ACTUAL_NUT_CAPTURE_GEOMETRY_LOCAL_PASS_NOT_RELEASE' if valid and solids==1 and not hits else 'ACTUAL_NUT_CAPTURE_GEOMETRY_FAIL',parent=ref(src),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='SAME85part P1 receiver integral nut antirotation cages and four external mounting ports;bolt rotational lock and external bench body remain absent.',not_qualified=old['not_qualified']+['Changed receiver invalidates historical receiver FE/mass/contact evidence. Nut cage has finite backlash;bolt still free to rotate. No physical thread or external support.'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],changed=changed,hits=hits,pairs=pairs)));raise SystemExit(0 if valid and solids==1 and not hits else 2)
if __name__=='__main__':main()
