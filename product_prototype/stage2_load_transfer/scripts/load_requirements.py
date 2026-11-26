"""Conditional wrench feasibility and work-conjugate Rev AA cable geometry.
Not a grasp prediction: friction and contact latitude are declared scenarios.
"""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pivot(t):
    a=(1-math.cos(t))/t if abs(t)>1e-6 else t/2-t**3/24
    b=math.sin(t)/t if abs(t)>1e-6 else 1-t*t/6
    return np.array([50-88*a+3*math.sin(t)-7*math.cos(t),-7-88*b+3*math.cos(t)+7*math.sin(t)])*.001
def dpivot(t):
    da=(t*math.sin(t)-(1-math.cos(t)))/t**2 if abs(t)>1e-5 else .5-t*t/8
    db=(t*math.cos(t)-math.sin(t))/t**2 if abs(t)>1e-5 else -t/3+t**3/30
    return np.array([-88*da+3*math.cos(t)+7*math.sin(t),-88*db-3*math.sin(t)+7*math.cos(t)])*.001
def path(t,r):
    p=pivot(t);c=np.array([.044,.025]);d=p-c
    b=-(math.atan2(-d[1],-d[0])-math.acos(r/np.linalg.norm(d)))
    n=np.array([math.cos(b),-math.sin(b)]);q=c-r*n
    cd=np.array([-.036,.005]);normal=np.array([-cd[1],cd[0]])/np.linalg.norm(cd)
    if normal[1]<0:normal=-normal
    phi=math.atan2(normal[1],normal[0]);end=math.atan2(-n[1],-n[0])
    while end<phi:end+=2*math.pi
    length=np.linalg.norm(cd)+r*(end-phi)+np.linalg.norm(p-q)-.020
    # Envelope theorem eliminates tangent-point derivatives.
    gradient=(p-q)/np.linalg.norm(p-q)
    return float(length),float(-gradient@dpivot(t)),p,q
def contact_case(lat,mu,count):
    a=math.radians(lat);normals=[];tangents=[];positions=[]
    for phi in np.arange(count)*2*math.pi/count:
        e=np.array([math.cos(phi),math.sin(phi),0.]);z=np.array([0.,0.,1.])
        radial=math.cos(a)*e+math.sin(a)*z
        normals.append(-radial);tangents.append(-math.sin(a)*e+math.cos(a)*z);positions.append(.03*radial)
    # A one-contact sphere is generally not moment-balanced: LP enforces
    # all six wrench components, unlike mg/(mu*N) on a single finger.
    columns=[]
    for n,t,p in zip(normals,tangents,positions):
        for f in (n+mu*t,n-mu*t):columns.append(np.r_[f,np.cross(p,f)])
    A=np.array(columns).T;b=np.array([0,0,.981,0,0,0.])
    lp=linprog(np.ones(2*count),A_eq=A,b_eq=b,bounds=(0,None),method='highs')
    return dict(latitude_deg=lat,assumed_mu=mu,fingers=count,feasible=bool(lp.success),
        normal_forces_N=(lp.x.reshape(count,2).sum(axis=1).tolist() if lp.success else None),
        force_moment_residual=(float(np.linalg.norm(A@lp.x-b)) if lp.success else None),
        scope='Ideal prescribed contact points; no claim these contacts exist on Rev AA')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    poses=[]
    for diameter in (.00048,.00050,.00052):
        # actual groove floor minimum/nominal from released manufacturing datums
        for floor in (.021850/2,.021860/2):
            r=floor+diameter/2;l0=path(0,r)[0]
            for deg in (0,10,20,30,40,50,60):
                t=math.radians(deg);length,arm,point,q=path(t,r)
                h=1e-5;fd=-(path(t+h,r)[0]-path(t-h,r)[0])/(2*h)
                error=abs(fd-arm)/abs(arm)
                assert error<1e-6,(deg,error)
                poses.append(dict(diameter_m=diameter,groove_floor_radius_m=floor,seated_radius_m=r,angle_deg=deg,
                    free_length_m=length,takeup_m=l0-length,drum_angle_rad=(l0-length)/r,
                    generalized_moment_arm_m=arm,finite_difference_relative_error=error,
                    pivot_m=point.tolist(),idler_tangent_m=q.tolist()))
    contacts=[contact_case(lat,mu,n) for lat in (-30,0,30) for mu in (.2,.4,.6) for n in (1,3)]
    assert all(x['force_moment_residual']<1e-10 for x in contacts if x['feasible'])
    result=dict(status='PASS',scope='CONDITIONAL STATIC WRENCH AND GEOMETRIC VIRTUAL-WORK VERIFICATION ONLY',
        case='revAA_heel_relief2',object_weight_N=.981,geometry=poses,contacts=contacts,
        acceptance=dict(wrench_residual_max=1e-10,derivative_relative_max=1e-6),
        material_properties_used=False,actual_required_tendon_tension_N=None,
        missing='Actual contact locations/friction and nonlinear Finger response must determine required tension; 1.5 N is NOT certified',
        source_SHA256=sha(Path(__file__)),cad_integrals_SHA256=sha(ROOT/'models/geometry/revAA_extract2/summary.json'),
        command='python scripts/load_requirements.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],pose_count=len(poses),max_derivative_error=max(x['finite_difference_relative_error'] for x in poses),
        seated_radius_m=sorted(set(x['seated_radius_m'] for x in poses)),takeup_60_m=[x['takeup_m'] for x in poses if x['angle_deg']==60],
        contact_scenarios=contacts),indent=2))
if __name__=='__main__':main()
