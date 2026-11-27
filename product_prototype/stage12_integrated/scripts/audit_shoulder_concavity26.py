"""Independent finite-triangle nearest-distance falsification of concave edge hull."""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def distance(q,t):
 e=t[1:]-t[0];v=q-t[0];uv=np.linalg.solve(e@e.T,e@v);w=np.r_[1-uv.sum(),uv]
 if w.min()>=0:return np.linalg.norm(q-w@t)
 ans=[]
 for i,j in [(0,1),(0,2),(1,2)]:
  d=t[j]-t[i];a=np.clip((q-t[i])@d/(d@d),0,1);ans.append(np.linalg.norm(q-t[i]-a*d))
 return min(ans)

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated/primaryP1_shoulder_edges26/summary.json';s=json.loads(src.read_text());edges=json.loads((REPO/s['edges']['path']).read_text());triangles={};rows=[]
 for level in [2,3]:
  ms=json.loads((ROOT/f'validation/integrated/primaryP1_ycapture_mesh{level}/summary.json').read_text());data=np.load(REPO/ms['mesh']['path']);p=data['OPEN_FRAME_points_mm'];t=data['OPEN_FRAME_tetra'];f=np.concatenate([t[:,v] for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);u,idx,c=np.unique(np.sort(f,axis=1),axis=0,return_index=True,return_counts=True);triangles[level]=p[f[idx[c==1]]]
 for r in edges:
  edge=np.array(r['edge_mm']);e=edge.mean(0);n=np.array(r['normal_cone_test_direction']);q=e+.1*n;d=min(distance(q,triangles[r['mesh_level']][i]) for i in r['owner_triangles']);convex=r['local_convex'];rows.append(dict(mesh_level=r['mesh_level'],sign=r['sign'],edge_nodes=r['edge_nodes'],convex=convex,edge_distance_mm=.1,nearest_incident_face_distance_mm=float(d),false_edge_hull_rejected=bool(d<.1-1e-8) if not convex else None,convex_edge_nearest=bool(abs(d-.1)<1e-8) if convex else None))
 conc=[r for r in rows if not r['convex']];conv=[r for r in rows if r['convex']];checks=dict(every_concave_hull_falsified=all(r['false_edge_hull_rejected'] for r in conc),convex_edge_nearest_verified=all(r['convex_edge_nearest'] for r in conv),both_controls_nonempty=bool(conc and conv));dump(out/'edge_probes.json',rows);dump(out/'summary.json',dict(status='ACTUAL_P1_CONCAVE_EDGE_HULL_REJECTION_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_CONCAVE_EDGE_HULL_AUDIT_FAIL',candidate=s['candidate'],source=ref(src),verifier=ref(out/'verifier.py'),probes=ref(out/'edge_probes.json'),checks=checks,concave_probes=len(conc),convex_probes=len(conv),concave_face_distance_range_mm=[min(r['nearest_incident_face_distance_mm'] for r in conc),max(r['nearest_incident_face_distance_mm'] for r in conc)],max_convex_distance_error_mm=max(abs(r['nearest_incident_face_distance_mm']-.1) for r in conv),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],whole_system_release=False,accepted_equilibria=0,required_next_mechanism='At concave shoulder/fillet junctions use finite adjacent-face alternatives, not positive-hull edge forces. At convex boundary retain finite edge/vertex ownership and cone checks. Rebuild full material-boundary contact before fivebody equilibrium.',limitations=['Actual linear tetra boundary geometric probe; not exact smooth CAD fillet collision or force law.','No attached load, pressure solution, implicit update or new equilibrium accepted.']));print(json.dumps(dict(checks=checks,concave=len(conc),convex=len(conv))));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
