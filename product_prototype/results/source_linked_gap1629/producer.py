"""Actual contact-child positions and Jacobians vs native linear gap at same step."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='identified_contact_phase1626');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;run=json.loads((src/'summary.json').read_text());assert run['maximum_observer_q_v_surface_impulse_error']==0;target=run['target_accepted_time_s'];root=ET.parse(src/'scene.scn').getroot();distance=float(root.find('MinProximityIntersection').get('contactDistance'));owners={int(r['row_id']):(r['constraint_path'],[r[k].rsplit('/',1)[0]+'/' for k in ('model0','model1')]) for r in read(src/'response_rows.csv') if abs(float(r['time_s'])-target)<1e-12};raw=read(src/'probe.rows.csv');solve=[r for r in raw if r['phase']=='solve_end'];time=float(solve[0]['time_s']);n=len(solve);W=np.zeros((n,n));d=np.zeros(n);f=np.zeros(n)
 for r in solve:i=int(r['row']);d[i]=float(r['dFree']);f[i]=float(r['f'])
 for r in read(src/'probe.W.csv'):
  if r['phase']=='solve_end' and float(r['time_s'])==time:W[int(r['i']),int(r['j'])]=float(r['W'])
 sums={};seen=set();sides={}
 for r in read(src/'probe.children.csv'):
  t=float(r['time_s']);phase=r['phase'];row=int(r['row']);side=int(r['side']);col=int(r['column'])
  owner=owners.get(row)
  if owner is None or owner[0]!=r['constraint'] or not r['state'].startswith(owner[1][side]):continue
  if not ((phase=='build_end' and t==time) or (phase=='accepted_end' and abs(t-target)<1e-12)):continue
  key=(phase,row,side,col);assert key not in seen;seen.add(key);J=np.fromstring(r['J'],sep=' ');q=np.fromstring(r['q'],sep=' ');fq=np.fromstring(r['free_q'],sep=' ');key=(phase,row);sums[key]=sums.get(key,np.zeros(2))+[J@q,J@fq];sides.setdefault(key,set()).add(side)
 for phase in ('build_end','accepted_end'):
  assert all(sides.get((phase,i))=={0,1} for i in range(n)),'Bothactualcontactstatesrequiredforeachglobalrow'
 buildfree=np.array([sums['build_end',i][1]-distance for i in range(n)]);accepted=np.array([sums['accepted_end',i][0]-distance for i in range(n)]);linear=W@f+d;dfree_error=float(abs(buildfree-d).max());nonlinear=float(abs(accepted-linear).max());diag=np.diag(W);assert np.all(diag>0);natural=float(abs(np.minimum(diag*f,linear)).max());record=dict(status='ACTUAL_MAPPED_CONTACT_GAP_DECOMPOSITION_ONLY' if dfree_error<=1e-12 else 'FAIL_CONTACT_CHILD_RECONSTRUCTION',dimension=n,target_accepted_time_s=target,maximum_actual_free_child_gap_vs_Native_dFree_error_m=dfree_error,minimum_Native_linearized_gap_m=float(linear.min()),minimum_actual_accepted_child_halfspace_gap_m=float(accepted.min()),maximum_accepted_mapping_vs_linearized_gap_difference_m=nonlinear,maximum_diagonal_scaled_NCP_residual_m=natural,maximum_negative_multiplier_Ns=float(max(0,-f.min())),actual_wire_vertex_solid_gap_m=-4.602854460679719e-6,scope='Zero-friction normals and2umcontactDistance/zeroexplicitmodelproximity. Bothactual childstates andNativeJrows linkedbyconstraintpathANDfirstrow,not ambiguouspathalone. NativegetPositionViolation formula requiresindependentcrosscheck<=1e-12beforeinterpretation. Nativehalfspaceusesfrozencontacts,notsignedsolid/CCD. NCP min(diagW*f,W*f+d) dimensionallygap,notrelativefloor. Noforce/statecorrection ornewsolver.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','summary.json','probe.rows.csv','probe.W.csv','probe.children.csv','response_rows.csv')});(out/'summary.json').write_text(json.dumps(record,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());np.savez(out/'gaps.npz',dFree=d,actual_free_gap=buildfree,Native_linear_gap=linear,accepted_child_gap=accepted,f=f);print(json.dumps(record,indent=2))
if __name__=='__main__':main()
