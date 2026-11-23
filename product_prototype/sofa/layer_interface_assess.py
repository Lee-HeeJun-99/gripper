"""Read accepted FEM state/constraint/geometry;no inferred vacuum calibration."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from layer_coupon_assess import overlap
def assess(case):
 src=BASE/'results'/case;m=json.loads((src/'mesh.json').read_text());q0=np.array(m['q0']);tet=np.array(m['tetrahedra']);rr=[]
 for i in (0,1):
  with (src/f'layer{i}.csv').open() as f:rr.append(list(csv.DictReader(f)))
 q=np.array([[np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows] for rows in rr]);v=np.array([[np.fromstring(r['v'],sep=' ').reshape(-1,3) for r in rows] for rows in rr]);pre=json.loads((src/'preflight.json').read_text());init=np.array([q0,q0+[0,0,.000202]]);tip=q0[:,0]==.04;tip_d=np.array([.5*((q[0,k,tip,2]-init[0,tip,2]).mean()+(q[1,k,tip,2]-init[1,tip,2]).mean()) for k in range(q.shape[1])]);det0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));ratio=np.linalg.det((q[:,:,tet[:,1:]]-q[:,:,tet[:,0,None]]).transpose(0,1,2,4,3))/det0
 witnessed=sum(overlap(q[:,k],tet) for k in range(q.shape[1]));lo=np.flatnonzero((q0[:,2]==.0002)&(q0[:,0]>0));hi=lo-1;error=q[1,:,hi]-q[0,:,lo]-[0,0,.000002];max_interface=float(abs(error).max());speed=float(np.linalg.norm(v[:,-1],axis=-1).max());slope=float(abs(np.diff(q[:,-1,::4,2],axis=1)/.005).max());last=tip_d[-50:];relative=float(np.max(abs(last-tip_d[-1]))/abs(tip_d[-1])) if tip_d[-1]!=0 else None
 with (src/'constraints.csv').open() as f:constraints=list(csv.DictReader(f))
 return dict(case=case,outputs=q.shape[1],final_mean_tip_displacement_m=float(tip_d[-1]),last50_relative_tip_drift=relative,final_max_node_speed_m_s=speed,minimum_volume_ratio=float(ratio.min()),strict_overlap_witnesses=witnessed,max_interface_rest_vector_error_m=max_interface,maximum_final_longitudinal_slope=slope,iteration_limit_outputs=sum(int(r['iterations'])>=1000 for r in constraints),max_solver_error=max(float(r['error']) for r in constraints),classification=pre['classification'],effective_EI=None,pressure_law=None,root_reaction=None,energy_work=None,input_hashes={str((src/f).relative_to(BASE)):sha(src/f) for f in ('scene.scn','mesh.json','preflight.json','layer0.csv','layer1.csv','constraints.csv')})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[assess(c) for c in ('layer_free1189','layer_interface_limit1239')];free,tied=records;ratio=abs(free['final_mean_tip_displacement_m']/tied['final_mean_tip_displacement_m']);d=dict(status='IDEAL_INTERFACE_DISPLACEMENT_DIAGNOSTIC_ONLY',records=records,free_to_tied_displacement_ratio=ratio,ideal_zero_gap_beam_two_layer_ratio=4,scope='Same assumed E/material/mesh/mass/bending load/dt;pressure0. Added explicit world-vector interface constraint. Small slope approximation only;not actual friction/pressure/adhesion/jamming law. Coarse thin tetrahedra unqualified;no effective EI certification.',physical_validation='NOT QUALIFIED',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
