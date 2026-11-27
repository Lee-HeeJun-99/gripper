"""Revise the SAME P1 motor clamp: integral finite contact lands and open split.
No new purchased part, no motor rating or preload/minimum-material claim.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports/primaryP1_interfaces18';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_fixture15/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'models/standard_drive/batch6_sources1/reviewed.json')],parts=refs,intersection_mm3_max=1e-8,design='Same78partP1 two10x6mm integral lower-cradle motor side lands close0.05mm xgap. OriginalRootBack and existing160mm2 Frame wall retained: independent17wall audit proves new key unnecessary at current positiveFx demand. Original lateral cartridge assembly retained. Nominal zero-gap not fit/strength/process qualification.'))
 parts={n:read(REPO/r['path']) for n,r in refs.items()}
 frame=parts['OPEN_FRAME']
 for x in (-5.06,5.):frame=fuse(frame,box(x,-21.5,14,.06,10,6))
 frame=canonical(frame)
 changed=[]
 for n,s in [('OPEN_FRAME',frame)]:
  export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=old['part_references'][n]))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   count+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_interfaces18'
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 dump(out/'BOM.json',bom)
 result=dict(old);result.update(revision='primaryP1_interfaces18',status='PRIMARY_CLAMP_GEOMETRY_FAIL' if hits or not all(x['valid'] and x['solids']==1 for x in changed) else 'PRIMARY_CLAMP_NOMINAL_GEOMETRY_PASS',part_references=refs,changed=changed,parent=ref(src),assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=count,design_change='Same78partP1 motor lateral bearing lands only. ExistingRoot wall shoulder reused; proposed16/17key withdrawn after full-contact audit. Source1101,stock1996 and all hardware reused. Fit/case capacity/material/Frame compliance unresolved.',not_qualified=old['not_qualified']+['Land location on real gearbox vs source simplified motor envelope; finite contact pressure,case stiffness,tolerance and preload must be qualified','Finite Ground still needs an external physical bench attachment; no fixed-DOF substitute'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],changed=changed,interferences=hits,exact_pairs=count)));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
