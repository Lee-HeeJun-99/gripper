"""Actual AO three-module top-entry assembly alternative; finite rigid samples only."""
import json,shutil,sys
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds,overlap,common

def main():
 assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/stage1/batch6_module_entry1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/revAO_root2/summary.json';d=json.loads(src.read_text())
 for r in d['part_references'].values():assert sha(REPO/r['path'])==r['SHA256']
 parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()}
 def module(n):
  return n.startswith(('F0_','F1_','F2_')) and n[3:].startswith(('SKIN','RAIL_','ROOT_','TERMINAL_','SWIVEL_','TIP_FACTORY','CASSETTE_','JAMMING_'))
 groups={i:[n for n in parts if n.startswith(f'F{i}_') and module(n)] for i in range(3)}
 deferred=[n for n in parts if n.endswith('TENDON_WIRE') or (n.startswith(('F0_','F1_','F2_')) and n[3:].startswith(('RF0_','RF1_')))]
 fixed={n:s for n,s in parts.items() if not module(n) and n not in deferred};bb={n:bounds(s) for n,s in fixed.items()}
 dump(out/'inputs.json',dict(candidate=ref(src),parts=d['part_references'],producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')],threshold_mm3=1e-8,groups=groups,deferred=deferred,initial_fixed=list(fixed),contract='Counterfactual ordered preassembled modules F0 then F1 then F2 enter vertically from +Z at120,80,40,10,2,0mm. All root clamp pins/layers/terminal/cassette move together. RF Palm mounting fasteners and tendon wires installed later, not silently removed from final inventory. No internal module assembly or continuous path certification.'))
 rows=[];comparisons=0
 for i in range(3):
  for dz in (120,80,40,10,2,0):
   hits=[]
   for n in groups[i]:
    assert not (ROOT/'runtime/STOP').exists()
    moved=translate(parts[n],0,0,dz);b=bounds(moved)
    for m,t in fixed.items():
     if overlap(b,bb[m]):
      comparisons+=1;v=common(moved,t)
      if v>1e-8:hits.append(dict(moving=n,fixed=m,common_mm3=v))
   rows.append(dict(sector=i,dz_mm=dz,hits=hits))
  # Later poses assume earlier modules reach nominal location: diagnostic counterfactual if rejected.
  for n in groups[i]:fixed[n]=parts[n];bb[n]=bounds(parts[n])
 nominal=[r for r in rows if r['dz_mm']==0];bad=[r for r in rows if r['hits']]
 result=dict(status='ASSEMBLY_ALTERNATIVE_REJECTED' if bad else 'FINITE_ASSEMBLY_SAMPLES_CLEAR',inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),candidate=ref(src),rows=rows,comparisons=comparisons,module_parts={i:len(g) for i,g in groups.items()},nominal_samples_clear=not any(r['hits'] for r in nominal),collision_rows=len(bad),first_collision=bad[0] if bad else None,whole_system_release=False,continuous_path_qualified=False,adopted=False,actual_capacity_qualified=False,changed_part_IDs=[],custom_parts_removed=0,custom_processes_removed=0,limitations=['Rigid nominal reference only; no finite loaded PET/Rail trajectory','Later sectors evaluated counterfactually after earlier nominal installation even if earlier entry fails','No internal preassembly, RF fastener installation, cable routing, tool or tolerance certificate','A sampled collision rejects this entry direction, not all assembly sequences'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],comparisons=comparisons,collision_rows=len(bad),first_collision=result['first_collision'])));raise SystemExit(2 if bad else 0)
if __name__=='__main__':main()
