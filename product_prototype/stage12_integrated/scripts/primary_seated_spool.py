"""Same primary P1, nominal seated spool floor matches factory nipple tangent.
Remanufactured ONE custom spool, not a shim/weld retrofit or new architecture.
"""
import sys,json,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
 out=ROOT/'cad/exports/primaryP1_seated21';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'cad/exports/primaryP1_retention20/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 # Restore material only in the old circumferential broad-groove region, then
 # turn a nominal R11.00 floor with the SAME .9 flat / .1 corner /1.1 width.
 fill=cut(cyl(11.10,(0,-.55,20),1.1,(0,1,0)),cyl(10.5,(0,-.56,20),1.12,(0,1,0)))
 ring=cut(cyl(19,(0,-.45,20),.9,(0,1,0)),cyl(11,(0,-.46,20),.92,(0,1,0)))
 opening=cut(cyl(19,(0,-.55,20),1.1,(0,1,0)),cyl(11.10,(0,-.56,20),1.12,(0,1,0)))
 corners=[BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(0,y,20),gp_Dir(0,1,0)),11.10,.10).Shape() for y in (-.45,.45)]
 # Preserve the exact inherited source pocket and .8 outlet through the fill.
 pocket=fuse(box(-5.2,-2.2,28.15,4.2,10.2,6.2),box(-6.2,-2.2,29.15,6.2,10.2,4.2))
 for x in (-5.2,-1):
  for z in (29.15,33.35):pocket=fuse(pocket,cyl(1,(x,-2.2,z),10.2,(0,1,0)))
 spool=canonical(cut(fuse(parts['F0_SPOOL'],fill),ring,opening,*corners,pocket,cyl(.4,(-.2,0,31.25),2.4,(1,0,0))))
 export(spool,out/'F0_SPOOL');parts['F0_SPOOL']=read(out/'F0_SPOOL.step');refs['F0_SPOOL']=ref(out/'F0_SPOOL.step');changed=[dict(part_ID='F0_SPOOL',STEP=refs['F0_SPOOL'],STL=ref(out/'F0_SPOOL.stl'),parent=old['part_references']['F0_SPOOL'],valid=bool(BRepCheck_Analyzer(parts['F0_SPOOL']).IsValid()),solids=solid_count(parts['F0_SPOOL']),volume_mm3=volume(parts['F0_SPOOL']),added_mm3=volume(cut(parts['F0_SPOOL'],read(REPO/old['part_references']['F0_SPOOL']['path']))),removed_mm3=volume(cut(read(REPO/old['part_references']['F0_SPOOL']['path']),parts['F0_SPOOL'])))]
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),failure=ref(ROOT/'validation/integrated/primaryP1_spatial_verify1/summary.json'),dependencies=[ref(S1/'scripts/play_groove_stage1.py'),ref(S1/'scripts/bend_aware_stage1.py'),ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'models/standard_drive/batch6_sources1/reviewed.json')],design='SAME78partP1; ONLYspoolfloorR10.93->11.00,flat.90/overall1.10/R.10cornerretained. Seatednominal.50wirecenter11.25matchesfactorynippleoutlet. Sourcepocket/.8outlet/stock1996hub/1101motor unchanged. NEWturnfromstock,notadditiverepair. HistoricalplayclearanceNOTtransferred; actualshaftplay/toleranceand.48...52diametersremainunqualified.',criteria=dict(intersection_mm3_max=1e-8)))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_seated21'
 for row in bom['parts']:
  row['STEP']=refs[row['part_ID']]
  if row['part_ID']=='F0_SPOOL':row['interface']='CNC6061nominalfloorR11.00,flat.90,R.10corners,nominal.5wireseatedR11.25; sourcepocket/stock1996hubunchanged. OldplayclearanceNOTqualified.'
 dump(out/'BOM.json',bom);r=dict(old);r.update(revision='primaryP1_seated21',status='PRIMARY_SEATED_SPOOL_GEOMETRY_PASS' if not hits and changed[0]['valid'] and changed[0]['solids']==1 else 'PRIMARY_SEATED_SPOOL_GEOMETRY_FAIL',parent=ref(src),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='SAME78partP1,ONLYcustomspoolre-cutfromstockwithR11.00seatedfloor;77STEPrefsunchanged. Restorenominaltangentfactoryexitwithoutnewsmallparts.',not_qualified=old['not_qualified']+['Changedspoolrequiresnewloadedwire/assembly/mass/sourceplay/tolerance/bend/friction/strengthandfullsame-revisionrelease. OldR10.93playboundsnottransferred.'])
 dump(out/'summary.json',r);print(dict(status=r['status'],changed=changed,pairs=pairs,hits=hits));raise SystemExit(0 if not hits and changed[0]['valid'] and changed[0]['solids']==1 else 2)
if __name__=='__main__':main()
