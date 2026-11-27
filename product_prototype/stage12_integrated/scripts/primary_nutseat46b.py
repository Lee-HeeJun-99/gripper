"""Same 112-part P1: finite integral nut reaction pockets at eight new stacks.
No bolt-spin fixation, preloading, locking guarantee or ultimate bench support.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from mechanisms_stage1 import hex_axis
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
TAG='primaryP1_nutseat46b'
STATIONS=[('BENCH_MOUNT',i,x,y,55.3,60.,'BENCH_SUPPORT') for i,(x,y) in enumerate([(-59,-58),(101,-58),(-59,39),(101,39)])]+[('BENCH_THROUGH',i,x,y,-142.7,-138.,'EXTERNAL_BENCH_PLATE') for i,(x,y) in enumerate([(-65,-35),(107,-35),(-65,15),(107,15)])]
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports'/TAG;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_benchattachment45/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};new={n:parts[n] for n in ['BENCH_SUPPORT','EXTERNAL_BENCH_PLATE']}
 for prefix,i,x,y,z0,z1,parent in STATIONS:
  # Collar shares the exact parent seat plane; empty pocket ends at original bearing
  # seat. The original 5.5mm parent clearance bore stays open above that seat.
  ring=cut(cyl(7.5,(x,y,z0),z1-z0),hex_axis((x,y,z0-.01),(0,0,1),8.2,z1-z0+.03))
  new[parent]=fuse(new[parent],ring)
 changed=[]
 for n,s in new.items():
  s=canonical(s);export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=old['part_references'][n]))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=TAG
 for row in bom['parts']:
  row['STEP']=refs[row['part_ID']]
  if row['part_ID'] in new:row.update(interface='Four integral downward-open 8.2AF nut pockets;original bearing seats and key dimensions unchanged;finite nut yaw clearance;bolt spin remains free',material='UNQUALIFIED custom support minimum;new machining and notch/strength require qualification')
 dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(cp),producer=ref(out/'producer.py'),stations=[dict(prefix=p,index=i,xy_mm=[x,y],nut_z_mm=[z0,z1],support=b) for p,i,x,y,z0,z1,b in STATIONS],pocket_AF_mm=8.2,outer_radius_mm=7.5,pocket_depth_mm=4.7,source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),effective_thread_engagement_mm=None,bolt_rotation_restraint=None,external_ground_attachment=None))
 good=not hits and all(r['valid'] and r['solids']==1 for r in changed)
 d=dict(old);d.update(revision=TAG,status='ACTUAL_EIGHT_NUT_SEATS_GEOMETRY_PASS_NOT_RELEASE' if good else 'ACTUAL_EIGHT_NUT_SEATS_GEOMETRY_FAIL',parent=ref(cp),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Same 112-part P1;four integral nut reaction collars on stand plus four on finite bench plate,original stack/bearing/key positions preserved.',not_qualified=old['not_qualified']+['Eight nominal nut yaw reactions implemented;bolt spin,thread friction,material/strength,ultimate external support and actual operating loads remain unqualified. Changed supports invalidate old physical fields.'])
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],parts=len(parts),hits=hits)));raise SystemExit(0 if good else 2)
if __name__=='__main__':main()
