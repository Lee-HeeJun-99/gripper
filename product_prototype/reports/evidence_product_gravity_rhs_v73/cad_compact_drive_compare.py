"""Matched-reference support-envelope comparison;not stiffness/holding optimization."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();files=[BASE/'meshes'/name/'full_assembly_recipe.json' for name in ('b3_root_canonical_v34',a.candidate)];assemblies=[json.loads(f.read_text())['parts'] for f in files];maps=[{p['name']:p for p in parts} for parts in assemblies]
 if set(maps[0])!=set(maps[1]):raise ValueError('unmatched component set')
 changed=[name for name in maps[0] if maps[0][name]['shape']!=maps[1][name]['shape']]
 if any(maps[0][name]['group']!='root_integral_bridge' for name in changed):raise ValueError('non-support configuration changed')
 records=[]
 for parts in assemblies:
  solids=[evaluate(p['shape']) for p in parts];v=np.vstack([s.vertices for s in solids]);records.append(dict(part_count=len(parts),maximum_radial_extent_mm=float(np.linalg.norm(v[:,:2],axis=1).max()),AABB_mm=[v.min(axis=0).tolist(),v.max(axis=0).tolist()],changed_supports_summed_solid_volume_mm3=sum(s.volume for p,s in zip(parts,solids) if p['name'] in changed)))
 r0,r1=[r['maximum_radial_extent_mm'] for r in records];d=dict(status='MATCHED_SUPPORT_ENVELOPE_COMPARISON_NOT_PHYSICAL_OPTIMUM',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in files+[Path(__file__),BASE/'cad/manufacturing_assembly.py']},records=records,changed_parts=changed,radial_extent_reduction_mm=r0-r1,radial_extent_reduction_percent=100*(r0-r1)/r0,runtime_s=time.monotonic()-start,actual_stiffness_N_per_mm=None,fabrication_ready=False,scope='Exactly matched292component names;shape recipe changes restricted to6supportbridges. Skin/Rails/Guide/Wire/Rootwheel/pin/drum andmaterialconfig notchanged. No actuationposechange/holdinggain/actualmass/stiffness/fatigue/continuousclearance claim. Solidvolume is geometricproxy,not materialselection oroptimizedequalmaterialstudy.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(changed=len(changed),radial_extent_reduction_mm=d['radial_extent_reduction_mm'],radial_extent_reduction_percent=d['radial_extent_reduction_percent'],records=records),indent=2))
if __name__=='__main__':main()
