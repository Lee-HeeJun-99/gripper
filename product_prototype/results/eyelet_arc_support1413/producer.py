"""Independent finite R5 arc/support check, even though local bore candidate failed."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from analyse import BASE,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/eyelet_entry1412/summary.json';support=BASE/'results/four_route_support1409/summary.json';d=json.loads(src.read_text());rods=np.array(json.loads(support.read_text())['support_segments_mm']);best=None;groups={i:[] for i in range(4)};spacing=max(x['arc_spacing_mm'] for x in d['arcs'])
    for arc in d['arcs']:
        points=np.array(arc['points_mm']);groups[arc['route']].extend(points.tolist())
        for j,(start,end) in enumerate(rods):
            delta=end-start;t=np.clip((points-start)@delta/(delta@delta),0,1);dist=np.linalg.norm(points-start-t[:,None]*delta,axis=1);k=int(np.argmin(dist));gap=float(dist[k]-.5);lower=gap-arc['arc_spacing_mm']/2
            if best is None or lower<best['lower_bound_mm']:best=dict(route=arc['route'],guide=arc['guide'],support=j,actual_sample_capsule_gap_mm=gap,lower_bound_mm=lower,arc_point_mm=points[k].tolist())
    pairs=[]
    for i in range(4):
        for j in range(i):
            nearest=cKDTree(groups[j]).query(groups[i])[0].min();pairs.append(dict(routes=[j,i],lower_bound_mm=float(nearest-.5-spacing)))
    bad=[r for r in d['records'] if r.get('actual_sample_wire_solid_gap_mm',1)<0]
    result=dict(status='PASS_INITIAL_ARC_SUPPORT_PROXY_ONLY' if min(best['lower_bound_mm'],min(x['lower_bound_mm'] for x in pairs))>0 else 'REJECT_INITIAL_ARC_SUPPORT_PROXY',minimum_arc_support=best,arc_arc_pairs=pairs,local_bore_collision_witnesses=bad,overall_four_route='REJECTED_LOCAL_BORE_COLLISION',Native='NOT RUN',scope='R5 sampled circular arcs ONLY against finite OD.5 support capsules and other-route arcs. Lipschitz bounds;unchanged straight spans retain prior1409 test but joins/endanchors/fullguide/support/interfinger/dynamic checks NOT QUALIFIED. No force,contact or grasp evidence.',input_hashes={str(x.relative_to(BASE)):sha(x) for x in (src,support)},source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)))
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
