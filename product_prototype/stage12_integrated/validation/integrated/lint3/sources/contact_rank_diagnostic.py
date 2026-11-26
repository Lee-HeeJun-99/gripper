"""Read-only active material-contact Jacobian spectrum; no contact is removed."""
import argparse,ast,json,math,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,ref,dump
import rod_point_jacobian as rod

def inspect(row,L,profile,return_matrix=False):
    q=np.array(row['state_angles_rad']);n=len(q);theta=math.radians(row['fixture_angle_deg']);R=.088/theta
    c,s=math.cos(theta),math.sin(theta);M=np.array([[c,s],[-s,c]])
    shift=np.array([.0504-R*(1-c),-.007-R*s])-M@np.array([.0504,-.095])
    fc=np.array([profile['center_X_mm'],profile['center_Z_mm']])*.001;fr=profile['radius_mm']*.001
    prepared=rod.prepare(q,L);gaps=[];jac=[]
    for key,ts in row['material_contact_points'].items():
        i,side=ast.literal_eval(key)
        for t in ts:
            p,J=rod.point(prepared,i,t,side,M,shift);value,N=rod.walls(p,fc,fr)
            gaps.extend(value.tolist());jac.extend(N@J)
            if side==-1 and not (i==0 and t==0):
                p,J=rod.point(prepared,i,t,0,M,shift,False);v=p-[.0504-R,-.007];radius=np.linalg.norm(v)
                gaps.append(R-.00025-radius);jac.append(-(v/radius)@J)
    gaps=np.array(gaps);jac=np.array(jac);active=jac[np.abs(gaps)<=1e-9]
    norms=np.linalg.norm(active,axis=1);active=active[norms>1e-14];norms=norms[norms>1e-14]
    if not active.size:raise ValueError('No nonzero active contact rows')
    if return_matrix:return active/norms[:,None]
    spectrum=np.linalg.svd(active/norms[:,None],compute_uv=False)
    threshold=np.finfo(float).eps*max(active.shape)*spectrum[0];rank=int(np.count_nonzero(spectrum>threshold))
    return dict(n=n,input_status=row['status'],all_constraint_rows=len(gaps),nonzero_active_rows=len(active),degrees_of_freedom=n,
        normalized_singular_values=spectrum.tolist(),numerical_rank=rank,rank_threshold=float(threshold),
        normalized_condition_number=float(spectrum[0]/spectrum[-1]) if spectrum[-1]>0 else None,
        redundant_row_count_at_least=max(0,len(active)-rank),minimum_recorded_gap_m=float(gaps.min()),state_changed=False,
        interpretation='Linear row dependence is not itself a causal failure proof. Nonnegative normal cones cannot be replaced by an arbitrary signed QR basis.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',nargs='+',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/contact'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    candidate=ROOT/'cad/exports/revAD_funnel1/summary.json';profile=json.loads(candidate.read_text())['funnel_profile'];rows=[];sources=[]
    for tag in a.inputs:
        source=ROOT/'validation/finger'/tag/'summary.json';d=json.loads(source.read_text())
        if d['candidate']!=ref(candidate):raise ValueError('Wrong candidate')
        sources.append(ref(source));rows.extend(inspect(r,d['PET_free_length_m'],profile) for r in d['rows'])
    if not rows:raise ValueError('Empty diagnostic')
    result=dict(status='DIAGNOSTIC_COMPLETE_NOT_PHYSICAL_PASS',scope='STATIC ACTIVE JACOBIAN SPECTRUM; NO STATE OR CONTACT MODIFICATION',rows=rows,sources=sources,candidate=ref(candidate),producer=ref(out/'producer.py'),Jacobian=ref(Path(rod.__file__)),product_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],rows=[{k:r[k] for k in ('n','nonzero_active_rows','numerical_rank','normalized_condition_number','redundant_row_count_at_least')} for r in rows]),indent=2))
if __name__=='__main__':main()
