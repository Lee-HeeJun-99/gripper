"""Accepted-state mesh/formulation comparisons,guarded independent reference."""
import argparse,csv,json,subprocess,sys
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_bending_reference import reference
from layer_coupon_assess import overlap
def assess(case):
 src=BASE/'results'/case;m=json.loads((src/'mesh.json').read_text());q0=np.array(m['q0']);tet=np.array(m['tetrahedra']);F=np.zeros_like(q0);F[q0[:,0]==.04,2]=-1e-4/8;r=reference(q0,tet,F);records=[];allq=[]
 for i in (0,1):
  with (src/f'layer{i}.csv').open() as f:rows=list(csv.DictReader(f))
  q=np.array([np.fromstring(x['q'],sep=' ').reshape(-1,3) for x in rows]);v=np.array([np.fromstring(x['v'],sep=' ').reshape(-1,3) for x in rows]);init=q0+[0,0,i*.000202];u=q[-1]-init;tip=np.mean(q[:,q0[:,0]==.04,2]-init[q0[:,0]==.04,2],axis=1);D=(q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2);D0=(q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1);res=r['K']@u.ravel()-F.ravel();last50=float(abs(tip[-50:]-tip[-1]).max()/abs(tip[-1])) if tip[-1]!=0 else None;records.append(dict(layer=i,outputs=len(rows),final_tip_m=float(tip[-1]),reference_tip_m=r['reference_tip_m'],relative_tip_reference_error=float(abs(tip[-1]-r['reference_tip_m'])/abs(r['reference_tip_m'])),max_displacement_reference_error_m=float(abs(u-r['u']).max()),linear_reference_residual_relative=float(np.linalg.norm(res[r['free']])/np.linalg.norm(F.ravel()[r['free']])),last50_relative_tip_drift=last50,final_max_node_speed_m_s=float(np.linalg.norm(v[-1],axis=1).max()),minimum_volume_ratio=float((np.linalg.det(D)/np.linalg.det(D0)).min())));allq.append(q)
 with (src/'constraints.csv').open() as f:cr=list(csv.DictReader(f))
 imax=max(float(abs(np.fromstring(x['impulses_Ns'],sep=' ')).max()) if x['impulses_Ns'].strip() else 0 for x in cr);witnesses=0
 # Full original accepted output coverage,not endpoint-only geometry audit.
 for k in range(len(allq[0])):witnesses+=overlap(np.array([allq[0][k],allq[1][k]]),tet)
 return dict(case=case,records=records,strict_tet_centroid_overlap_witnesses=witnesses,maximum_contact_impulse_Ns=imax,iteration_limit_outputs=sum(int(x['iterations'])>=1000 for x in cr),native_internal_force=None,root_reaction=None,whole_energy=None,scope='Final Native q inserted in independent LINEAR K is a diagnostic,NOT actual nonlinear force query. Tiny q agreement does not certify force balance. All accepted tetra geometry checked;centroid overlap absence is not complete nonintersection proof.',input_hashes={str((src/f).relative_to(BASE)):sha(src/f) for f in ('scene.scn','mesh.json','layer0.csv','layer1.csv','constraints.csv')})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',120)));return
 records=[assess(c) for c in ('layer_free1189','layer_mesh_native1260','layer_linear_native1261')];a0=records[0]['records'][0]['final_tip_m'];b=records[1]['records'][0]['final_tip_m'];pair=abs(a0-b)/max(abs(a0),abs(b));d=dict(status='FAIL_NATIVE_LAYER_MESH_GATE' if pair>.01 else 'PASS_MESH_PAIR_SCOPE_ONLY',mesh_pair_relative=pair,mesh_gate=.01,records=records,physical_validation='NOT QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
