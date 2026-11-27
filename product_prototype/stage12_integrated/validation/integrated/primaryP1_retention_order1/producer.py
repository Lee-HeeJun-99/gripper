"""Close actual P1 Frame/Ground/internalretention -> Basefixture assembly order."""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds,overlap,common

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'cad/exports/primaryP1_retention20/summary.json';d=json.loads(src.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values());s={n:read(REPO/r['path']) for n,r in d['part_references'].items()};bb={n:bounds(q) for n,q in s.items()};fixed=['OPEN_FRAME','GROUND_PLATE']+[n for n in s if n.startswith(('GROUND_BOLT','GROUND_NUT'))];rows=[];hits=[];comparisons=0
 stages=[('TEST_BASE',[0,1,3,6,12,30,80])]+[(n,[-80,-30,-12,-6,-3,-1,0] if 'BOLT' in n else [80,30,12,6,3,1,0]) for n in s if n.startswith('FIXTURE_')]
 for name,poses in stages:
  for dz in poses:
   assert not(ROOT/'runtime/STOP').exists();q=translate(s[name],0,0,dz);local=[]
   for n in fixed:
    if overlap(bounds(q),bb[n]):
     comparisons+=1;v=common(q,s[n])
     if v>1e-8:local.append(dict(part=n,common_mm3=v))
   rows.append(dict(moving=name,dz_mm=dz,hits=local));hits+=local
  fixed.append(name)
 witness=ROOT/'validation/integrated/primaryP1_retention_witness4/summary.json';module=ROOT/'validation/integrated/primaryP1_retention_assembly1/summary.json';w=json.loads(witness.read_text());m=json.loads(module.read_text());assert w['candidate']==m['candidate']==ref(src)
 result=dict(status='ACTUAL_P1_ORDERED_INTERNAL_RETENTION_BASE_MODULE_SCREEN_PASS' if not hits and all(w['checks'].values()) and all(m['checks'].values()) else 'ACTUAL_P1_RETENTION_ORDER_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),prerequisite_internal_retention=ref(witness),subsequent_module=ref(module),stages=rows,poses=len(rows),exact_comparisons=comparisons,hits=hits,order=['FrameintoGround','fourinternalGroundbolt/nutpairs+holdtool/LkeybeforeFingerandBase','withdrawtools','BaseverticalontoGroundkeyoverinternalbolttips','fourfixturebolt/nutpairs','Fingerlateral','Drivevertical','Capvertical','RFandCapfasteners'],newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Discretecollisionchecksandconditionaltoolcorridorsonly,nocontinuousCCD/actualthreadtorque/preload/tolerance/process/physicalassembly orfull3FingerStage1.','Baseexternaltractionremainsmathematicalboundary,notphysicalbenchanchor.','Originalgeometry/designfailuresandfirsttoolpathfailuresremainpreserved.'])
 dump(out/'summary.json',result);print(dict(status=result['status'],poses=len(rows),comparisons=comparisons,hits=hits));raise SystemExit(0 if not hits else 2)
if __name__=='__main__':main()
