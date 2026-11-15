"""Normalized wrench rank, nullspace, cone closure AND bounded force feasibility."""
import argparse,csv,json
import numpy as np
from scipy.optimize import linprog
from trial_validation import read_states
from closure_common import OUT,write_json,sha
def cross(r):
    x,y,z=r;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
def analyze(points,normals,normal_limits,mu,radius):
    points=np.asarray(points);normals=np.asarray(normals);N=len(points)
    if not N:return dict(status='FAIL',reason='no contact')
    if points.shape!=(N,3) or normals.shape!=(N,3) or len(normal_limits)!=N or not np.isfinite(points).all() or not np.isfinite(normals).all() or not np.isfinite(normal_limits).all() or min(normal_limits)<0 or not np.isfinite(mu) or mu<0 or not np.isfinite(radius) or radius<=0 or np.min(np.linalg.norm(normals,axis=1))<1e-14:raise ValueError('invalid wrench geometry/capacity')
    G=np.hstack([np.vstack([np.eye(3),cross(r/radius)]) for r in points]);u,s,v=np.linalg.svd(G,full_matrices=G.shape[1]<6);rank=int(sum(s>1e-10*s[0]));columns=[];owners=[]
    for i,(p,n) in enumerate(zip(points,normals)):
        n=n/np.linalg.norm(n);axis=np.eye(3)[np.argmin(abs(n))];t=np.cross(n,axis);t/=np.linalg.norm(t);b=np.cross(n,t)
        for angle in np.arange(8)*2*np.pi/8:
            f=-n+mu*(np.cos(angle)*t+np.sin(angle)*b);columns.append(np.r_[f,np.cross(p,f)/radius]);owners.append(i)
    W=np.array(columns).T;m=W.shape[1];cone_singular=np.linalg.svd(W,compute_uv=False);cone_rank=int(sum(cone_singular>1e-10*cone_singular[0]))
    # Strictly positive equilibrium of ALL generating rays + rank6 proves
    # closure of this inscribed polyhedral cone, not unbounded load capacity.
    Aeq=np.zeros((7,m+1));Aeq[:6,:m]=W;Aeq[6,:m]=1
    Aineq=np.zeros((m,m+1));Aineq[np.arange(m),np.arange(m)]=-1;Aineq[:,-1]=1
    objective=np.r_[np.zeros(m),-1.];closure=linprog(objective,A_ub=Aineq,b_ub=np.zeros(m),A_eq=Aeq,b_eq=np.r_[np.zeros(6),1],bounds=[(0,None)]*(m+1),method='highs')
    margin=float(closure.x[-1]) if closure.success else 0;closure_pass=rank==6 and cone_rank==6 and margin>1e-9
    caps=np.asarray(normal_limits)/1e-6;A=np.zeros((N,m))
    for j,i in enumerate(owners):A[i,j]=1
    feasibility={}
    for i,axis in enumerate(('Fx','Fy','Fz','Tx','Ty','Tz')):
        for sign,label in [(1,'plus'),(-1,'minus')]:
            demand=np.eye(6)[i]*sign;lp=linprog(np.zeros(m),A_ub=A,b_ub=caps,A_eq=W,b_eq=-demand,bounds=(0,None),method='highs');error=float(np.max(abs(W@lp.x+demand))) if lp.success else None
            feasibility[axis+label]=dict(feasible=bool(lp.success and error<1e-7),normalized_balance_error=error,solver_message=lp.message,force_scale=1e-6,torque_scale=1e-6*radius)
    return dict(status='PASS',rank=rank,singular_values=s.tolist(),left_nullspace=u[:,rank:].T.tolist(),normalization_length_mm=radius,points_relative_com_mm=points.tolist(),normals=normals.tolist(),normal_capacity_measured=normal_limits,mu=mu,cone_rays=8,cone_rank=cone_rank,cone_singular_values=cone_singular.tolist(),cone_origin_strict_interior=closure_pass,positive_equilibrium_margin=margin,bounded_feasibility=feasibility,scope='rank6 is not sufficient; inscribed friction-cone closure and fixed measured normal-force caps are separate conservative tests; not ultimate structural load capacity')
def main():
    p=argparse.ArgumentParser();p.add_argument('--trial',default='convergence_n11q8');args=p.parse_args();directory=OUT/'trials'/args.trial;record=json.loads((directory/'metrics.json').read_text());c=record['config'];raw=read_states(directory/'state.txt');frame=min(raw,key=lambda r:abs(r['time']-(c['hold_until']-.02)));time=frame['time'];o=np.array(frame['X']).reshape(-1,7)[c['object_index'],:3]
    with (directory/'contact.csv.patch.csv').open() as f:rows=[r for r in csv.DictReader(f) if abs(float(r['time'])-time)<1e-7]
    pts=[[float(r[k])-o[j] for j,k in enumerate(('px','py','pz'))] for r in rows];normals=[[float(r[k]) for k in ('nx','ny','nz')] for r in rows];limits=[float(r['Fn']) for r in rows];result=analyze(pts,normals,limits,c['mu'],c['object_radius'])
    result.update(trial=args.trial,time=time,metrics_sha256=sha(directory/'metrics.json'),patch_sha256=sha(directory/'contact.csv.patch.csv'))
    baseline=analyze([[0,0,5],[0,0,-5]],[[0,0,1],[0,0,-1]],[5e-6,5e-6],.3,5)
    assumed=analyze([[5,0,0],[-2.5,4.330127018922193,0],[-2.5,-4.330127018922193,0]],[[1,0,0],[-.5,.8660254037844386,0],[-.5,-.8660254037844386,0]],[5e-6]*3,.3,5)
    out=OUT/'wrench';out.mkdir(exist_ok=True);write_json(out/(args.trial+'.json'),dict(actual_sofa_patch=result,ideal_two_point_control=baseline,assumed_three_contact_geometry=assumed,three_contact_scope='MATH ONLY; no claim that a SOFA three-finger actuator generates these forces'))
    print('rank',result['rank'],'cone',result['cone_origin_strict_interior'],'bounded',{k:v['feasible'] for k,v in result['bounded_feasibility'].items()})
if __name__=='__main__':main()
