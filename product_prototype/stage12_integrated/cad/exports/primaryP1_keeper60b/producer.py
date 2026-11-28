"""Actual same-P1 socket keeper bridges with finite transverse-pin anchor bosses.
Pin is source-size shaft ENVELOPE, not a fabricated installed split-pin certificate.
"""
import sys,json,shutil,math,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,bounds,common,overlap,volume,solid_count,translate
from build_stage1 import compound
from primary_captive59b import hexz
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
 tag=sys.argv[1];out=ROOT/'cad/exports'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_captive59c/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};spec=json.loads((REPO/old['cages']['path']).read_text())['specifications'];changed=[];rows=[];anchors=[]
 groups=[dict(name='ROOT_SOCKET_KEEPER',body='F0_ROOT_BACK',x=64,ys=[-16,16],top=-3,headtop=0,anchor_x=62),*[dict(name=f'CAP_SOCKET_KEEPER_{x}',body='MOTOR_CAP',x=x,ys=[-29.5,-13.5],top=29,headtop=32) for x in [-7,7]]]
 for g in groups:
  assert not(ROOT/'runtime/STOP').exists();x=g['x'];yc=sum(g['ys'])/2;top=g['top'];bridge=max(top+4,g['headtop']+2);ax=g.get('anchor_x',x);body=parts[g['body']];boss=box(ax-3,yc-2,top-.2,6,4,2.2);fused=fuse(body,boss);attachment=common(body,boss)
  # Real slot and pin tunnel; neither interface is tied or friction-rated.
  slot=box(ax-1.05,yc-1.05,top-.1,2.1,2.1,3.0);tunnel=cyl(.5,(ax-3.1,yc,top+1),6.2,(1,0,0));parts[g['body']]=canonical(cut(fused,slot,tunnel))
  keeper=box(x-2,yc-(g['ys'][1]-g['ys'][0])/2-2,bridge,4,g['ys'][1]-g['ys'][0]+4,1.5)
  keeper=fuse(keeper,box(ax-1,yc-1,top+.1,2,2,bridge-top+.3))
  for y in g['ys']:keeper=fuse(keeper,hexz(x,y,g['headtop']-1.25,2.4,bridge-g['headtop']+1.55))
  parts[g['name']]=canonical(cut(keeper,tunnel));pin=g['name']+'_PIN_SHAFT_ENVELOPE';parts[pin]=cyl(.45,(ax-5,yc,top+1),10,(1,0,0));changed.extend([g['name'],pin]);anchors.append(dict(**g,anchor_y_mm=yc,bridge_bottom_mm=bridge,boss_attachment_overlap_mm3=attachment,pin=pin,pin_axis=[1,0,0],pin_start=[ax-5,yc,top+1],pin_length_mm=10,source_pin_diameter_mm=[.8,.9],hole_diameter_mm=1,slot_XY_mm=2.1,tongue_XY_mm=2,axial_retention='NOT_IMPLEMENTED: split-pin eye and bent legs absent. Shaft envelope is a clearance/load-transfer contrast, not an installed standard-part solid.'))
 changed=['F0_ROOT_BACK','MOTOR_CAP']+changed
 for n in changed:
  export(parts[n],out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=old['part_references'].get(n),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n])))
 bb={n:bounds(s) for n,s in parts.items()};queries=[]
 for n,m in itertools.combinations(parts,2):
  if not(n in changed or m in changed) or not overlap(bb[n],bb[m]):continue
  assert not(ROOT/'runtime/STOP').exists();v=common(parts[n],parts[m]);row=dict(pair=[n,m],intersection_mm3=v);queries.append(row)
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 hits=[q for q in queries if abs(q['intersection_mm3'])>1e-8];w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=tag
 for q in bom['parts']:q['STEP']=refs[q['part_ID']]
 for n in changed:
  if n not in old['part_references']:bom['parts'].append(dict(part_ID=n,STEP=refs[n],interface='Actual socket bridge/anchor tongue' if 'SHAFT' not in n else 'DIN94 1x10 source-size shaft envelope ONLY; installed eye/bent-leg geometry NOT implemented',material='UNQUALIFIED stainless steel / unknown process; no strength credit',quantity=1))
 dump(out/'BOM.json',bom);dump(out/'anchors.json',dict(groups=anchors,socket_AF_mm=2.5,keeper_AF_mm=2.4,engagement_mm=1.25,source=ref(ROOT/'models/standard_drive/primary_keeper_sources60/reviewed.json'),index_step_deg=60,max_nearest_index_deg=30,max_nearest_index_helical_setting_mm=.5/12,guide_clearance_mm=.1,installed_retention_qualified=False))
 d=dict(old);d.update(revision=tag,parts=len(parts),part_references=refs,part_bounds_mm=bb,parent=ref(cp),producer=ref(out/'producer.py'),changed=rows,unchanged_part_STEP_count=75,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),anchors=ref(out/'anchors.json'),interferences=hits,exact_pairs=len(queries),status='ACTUAL_P1_INDEXED_KEEPER_DESIGN_GEOMETRY_CLEAR_NOT_RELEASE' if not hits else 'ACTUAL_P1_INDEXED_KEEPER_DESIGN_GEOMETRY_FAIL',design_change='Same one P1: three actual hex-socket keeper bridges and three source-size cross-pin shaft envelopes; actual two host bodies gain integral pin bosses, slots and transverse tunnels. All77 original functions retained; finite positive rotation path tested, split-pin retention and setting unresolved.',capacity_qualified=False,whole_system_release=False,newly_qualified_system_gate_ids=[])
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],solids=rows,hits=hits,anchors=anchors)));return 0 if not hits and all(r['valid'] and r['solids']==1 for r in rows) else 2
if __name__=='__main__':sys.exit(main())
