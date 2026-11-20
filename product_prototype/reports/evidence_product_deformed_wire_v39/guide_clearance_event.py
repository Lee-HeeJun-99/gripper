"""Pair-level accepted geometry vs end-event native detector outputs;not CCD."""
import argparse,csv,json
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--audit',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;audit=BASE/'results'/a.audit/'summary.json';meta=json.loads(audit.read_text());out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    pair=meta['offending_pairs'][0] if meta['offending_pairs'] else None
    if pair is None:result=dict(status='NO_NEGATIVE_SAMPLED_PAIR',scope=meta['scope'])
    else:
        names=[f'/guides{pair[f"finger{k}"]}/cable{pair[f"cable{k}"]}/' for k in (0,1)];counts={}
        for r in csv.DictReader((src/'detection_pairs.csv').open()):
            if (r['model0'].startswith(names[0]) and r['model1'].startswith(names[1])) or (r['model0'].startswith(names[1]) and r['model1'].startswith(names[0])):counts[r['accepted_time_s']]=counts.get(r['accepted_time_s'],0)+1
        trace=list(csv.DictReader((BASE/'results'/a.audit/'sampled_gap.csv').open()));frames=list(csv.DictReader((src/'guide_frames0.csv').open()));object_rows=list(csv.DictReader((src/'object.csv').open()));event=[]
        for r,f,obj in zip(trace,frames,object_rows):
            t=float(r['actual_time_s'])
            if abs(t-pair['worst_time_s'])<=.015:
                assert t==float(f['time_s'])==float(obj['time_s'])
                event.append(dict(time_s=t,global_minimum_gap_mm=float(r['minimum_native_guide_sphere_gap_mm']),selected_pair_detector_outputs=counts.get(f['time_s'],0),solver_error=float(f['solver_error']),solver_iterations=int(f['solver_iterations']),object_speed_mm_s=float(np.linalg.norm(np.fromstring(obj['rigid_v'],sep=' ')[:3])*1000)))
        result=dict(status='EVENT_DIAGNOSTIC_ONLY_NOT_SOLVER_FIX',case=a.case,selected_pair=pair,records=event,interpretation='End-event narrowphase outputs are not recomputed accepted-state CCD. A small linear constraint residual or absent detection output does not certify full accepted geometry clearance.',clock='Raw time keys matched exactly;no shift/interpolation',source_sha256=sha(__import__('pathlib').Path(__file__)),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (audit,src/'detection_pairs.csv',src/'guide_frames0.csv',src/'object.csv')})
    (out/'producer.py').write_bytes(__import__('pathlib').Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
