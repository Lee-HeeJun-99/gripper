"""Independent virtual-work pull direction for saved direct-route specimens."""
import json,math,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def path(a):
    # Direct integration of prescribed 88mm backbone plus rigid tip offset.
    if abs(a)<1e-8:x,z=43.,-92.
    else:x=50-88*(1-math.cos(a))/a-7*math.cos(a)+3*math.sin(a);z=-7-88*math.sin(a)/a+3*math.cos(a)+7*math.sin(a)
    P=np.array([x,z]);v=P-np.array([110.,20]);D=np.linalg.norm(v);u=v/D;k=11.25/D
    n=k*u+math.sqrt(1-k*k)*np.array([u[1],-u[0]]);Q=np.array([110.,20])+11.25*n;t=(Q-P)/np.linalg.norm(Q-P)
    length=11.25*(math.atan2(n[1],n[0])+math.pi/2)+math.sqrt(D*D-11.25**2)-16
    if abs(a)<1e-8:dp=np.array([-41.,7.])
    else:dp=np.array([-88*(a*math.sin(a)-(1-math.cos(a)))/a**2+7*math.sin(a)+3*math.cos(a),-88*(a*math.cos(a)-math.sin(a))/a**2-3*math.sin(a)+7*math.cos(a)])
    return length,-float(t@dp)
def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/batch6_route_work1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAW_direct_route2/summary.json';d=json.loads(src.read_text());rows=[]
    for r in d['rows']:
        if r['sector']:continue
        a=math.radians(r['pose_deg']);L,deriv=path(a);assert abs(L-r['free_reference_mm'])<1e-9
        h=1e-4
        # One-sided at REST to avoid cancellation near zero; refined check.
        differences=[]
        for h in (1e-3,5e-4,2.5e-4):
            fd=(-3*path(a)[0]+4*path(a+h)[0]-path(a+2*h)[0])/(2*h) if a==0 else (path(a+h)[0]-path(a-h)[0])/(2*h)
            differences.append(abs(fd-deriv))
        assert differences[-1]<1e-4
        rows.append(dict(pose_deg=r['pose_deg'],length_mm=L,dlength_dangle_mm_per_rad=deriv,closing_torque_Nm_per_N=-deriv/1000,finite_difference_errors_mm_per_rad=differences))
    lo,hi=0.,math.pi/3
    assert path(lo)[1]>0 and path(hi)[1]<0
    for _ in range(50):
        mid=(lo+hi)/2
        if path(mid)[1]>0:lo=mid
        else:hi=mid
    zero=(lo+hi)/2
    dump(out/'summary.json',dict(status='DIRECT_ROUTE_CLOSING_ACTUATION_FAIL',scope='Virtual work of the actual saved route on prescribed poses; not equilibrium, motor rating or Stage3 operation',source=ref(src),producer=ref(out/'producer.py'),rows=rows,dead_point_deg=math.degrees(zero),dead_point_length_mm=path(zero)[0],pull_direction='Positive cable tension gives negative closing torque at REST and through initial path; sign reverses at dead point. Winding reversal cannot make a tension-only cable push.',fixed_drum_torque_Nm_per_N=.01125,stroke_0_to_60_mm=path(0)[0]-path(math.pi/3)[0],finite_difference_verification=True,whole_system_release=False))
    print(json.dumps(dict(status='DIRECT_ROUTE_CLOSING_ACTUATION_FAIL',dead_point_deg=math.degrees(zero),rows=rows),indent=2));raise SystemExit(2)
if __name__=='__main__':main()
