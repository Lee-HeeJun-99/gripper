"""Finite-rotation PET against a prescribed circular RIGID rail test fixture.

Independent PET angles, inextensible segments and unilateral normal contact.
Rail fixture is NOT a solved flexible rail or actual whole Finger. Frictionless
limit only. This isolates geometry/axial migration before coupled friction FE.
"""
import argparse,json,math,shutil
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,nnls
from scipy.optimize import brentq
from baseline_registry import ROOT,S2,ref,dump
L=.0874;LR=.088;offset=.00025;gapmax=.00010
def curve(q,n):
    angles=np.r_[0.,q];delta=np.diff(angles);average=(angles[1:]+angles[:-1])/2
    # Exact constant-curvature integration, not chord lengths.
    factor=(L/n)*np.sinc(delta/(2*np.pi))
    step=factor[:,None]*np.column_stack((np.cos(average),np.sin(average)))
    return np.vstack(([0.,offset],np.array([0.,offset])+np.cumsum(step,axis=0)))
def continuous_gap(q,n,R):
    """Exact extrema of distance between each circular rod arc and rail centre."""
    p=curve(q,n);full=np.r_[0.,q];minimum=[]
    for i in range(n):
        lo,hi=sorted(full[i:i+2]);k=(full[i+1]-full[i])/(L/n)
        probes=[p[i],p[i+1]]
        if abs(k)>1e-6:
            centre=p[i]+np.array([-math.sin(full[i]),math.cos(full[i])])/k
            a=centre-np.array([0.,R]);base=math.atan2(-a[0],a[1])
            for j in range(math.floor((lo-base)/math.pi)-1,math.ceil((hi-base)/math.pi)+2):
                phi=base+j*math.pi
                if lo<phi<hi:probes.append(centre+np.array([math.sin(phi),-math.cos(phi)])/k)
        minimum.append(min(R-offset-np.linalg.norm(x-[0.,R]) for x in probes))
    return np.array(minimum)
def solve(n,theta,endstop=True,funnel=None):
    R=LR/theta;h=L/n
    # Actual taper approximated from24mm at material z=0 to12mm at z=-100.
    s=(np.arange(n)+.5)*h;width=.024-(.024-.012)*(.007+s)/.100
    E=507000*6894.757293168 # manufacturer typical, NOT allowable
    EI=E*width*.0003**3/12
    energy_scale=float(np.mean(EI)*theta*theta/LR)
    def energy(q):return float(np.sum(EI*np.diff(np.r_[0.,q])**2/(2*h))/energy_scale)
    def gradient(q):
        d=np.diff(np.r_[0.,q]);g=EI*d/h;g[:-1]-=EI[1:]*d[1:]/h
        return g/energy_scale
    def wall_constraints(q):
        if funnel is None:return np.empty(0)
        nodes=curve(q,n);full=np.r_[0.,q];allg=[]
        # Finite rigid terminal fixture is positioned by its own rail-end datum.
        c,s=math.cos(theta),math.sin(theta);M=np.array([[c,s],[-s,c]])
        end=np.array([.0504-R*(1-c),-.007-R*s]);shift=end-M@np.array([.0504,-.095])
        def distances(pts):
            def rectangle(lo,hi):
                lo=np.array(lo);hi=np.array(hi);z=np.abs(pts-(hi+lo)/2)-(hi-lo)/2
                return np.linalg.norm(np.maximum(z,0),axis=1)+np.minimum(np.max(z,axis=1),0)
            core=rectangle([.040,-.095],[.049,-.084]);bottom=rectangle([.040,-.100],[.050,-.095])
            lipbox=rectangle([.04898,-.095],[.04990,-.090])
            centre=np.array([funnel['center_X_mm'],funnel['center_Z_mm']])*.001
            circle=np.linalg.norm(pts-centre,axis=1)-funnel['radius_mm']*.001
            return np.column_stack((core,bottom,np.maximum(lipbox,circle)))
        centre=np.array([funnel['center_X_mm'],funnel['center_Z_mm']])*.001
        for i in range(n):
            delta=full[i+1]-full[i]
            def point(t,side):
                d=(full[i+1]-full[i])*t;a=full[i]+d/2
                xy=nodes[i]+h*t*np.sinc(d/(2*np.pi))*np.array([math.cos(a),math.sin(a)])
                world=np.array([.0504-xy[1],-.007-xy[0]])
                normal=np.array([-math.cos(full[i]+d),math.sin(full[i]+d)])
                return M.T@(world+side*.00015*normal-shift)
            for side in (-1,1):
                events=[0.,1.];splits=[0.,1.]
                if abs(delta)>1e-12:
                    # Exact coordinate extrema split each component into monotone arcs.
                    lo,hi=sorted((full[i]-theta,full[i+1]-theta))
                    for k in range(math.floor(2*lo/math.pi)-1,math.ceil(2*hi/math.pi)+2):
                        t=(k*math.pi/2-(full[i]-theta))/delta
                        if 0<t<1:splits.append(t)
                splits=sorted(splits);events+=splits
                # Exact coordinate-extremum broad phase: if the whole circular
                # corner arc misses the union's bounding box, no wall contact
                # is possible. Positive separation is a certified lower bound,
                # not disabled collision or a changed physical tolerance.
                extrema=np.array([point(t,side) for t in splits]);low=extrema.min(axis=0);high=extrema.max(axis=0)
                separation=max(.040-high[0],low[0]-.050,-.100-high[1],low[1]+.084)
                if separation>0:
                    allg.extend([separation]*3);continue
                for axis,levels in [(0,(.040,.04898,.049,.0499,.050)),(1,(-.100,-.095,-.090,-.084))]:
                    for level in levels:
                        fn=lambda t:point(t,side)[axis]-level
                        for left,right in zip(splits[:-1],splits[1:]):
                            if fn(left)*fn(right)<0:events.append(brentq(fn,left,right,xtol=1e-13))
                # Coordinate-extremum intervals span <=pi/2, also during solver
                # trial configurations. Never force/clamp the PET angles.
                def derivative(t):
                    phi=full[i]+delta*t-theta
                    tangent=(h-side*.00015*delta)*np.array([-math.sin(phi),-math.cos(phi)])
                    return float((point(t,side)-centre)@tangent)
                radial_splits=list(splits)
                for left,right in zip(splits[:-1],splits[1:]):
                    if derivative(left)*derivative(right)<0:radial_splits.append(brentq(derivative,left,right,xtol=1e-13))
                radial_splits=sorted(radial_splits);events+=radial_splits
                fn=lambda t:np.linalg.norm(point(t,side)-centre)-funnel['radius_mm']*.001
                for left,right in zip(radial_splits[:-1],radial_splits[1:]):
                    if fn(left)*fn(right)<0:events.append(brentq(fn,left,right,xtol=1e-13))
                events=sorted(set(events));probes=events+[(l+r)/2 for l,r in zip(events[:-1],events[1:])]
                # Boundary roots + interval witnesses detect entry between probes,
                # rather than repeatedly raising contact sampling resolution.
                allg.extend(np.min(distances(np.array([point(t,side) for t in probes])),axis=0))
        return np.array(allg)/1e-4
    def constraints(q):
        p=curve(q,n);rad=np.linalg.norm(p[1:]-[0.,R],axis=1)
        gap=R-offset-rad
        # Channel lip is a finite rear bound only in last4.4mm of rail.
        arc=R*np.arctan2(p[-1,0],R-p[-1,1])
        return np.r_[continuous_gap(q,n,R)/1e-4,((gapmax-gap[-1])/1e-4 if funnel is None else 1.),(arc-.083)/.001,((LR-arc)/.001 if endstop and funnel is None else 1.),wall_constraints(q)]
    initial=np.arange(1,n+1)*h/(R-offset)
    result=minimize(energy,initial,jac=gradient,method='SLSQP',constraints=[dict(type='ineq',fun=constraints)],options=dict(ftol=1e-12,maxiter=600))
    q=result.x;p=curve(q,n);c=constraints(q)
    # Finite-difference stationarity + nonnegative unilateral multipliers.
    eps=1e-6
    grad=gradient(q)
    jac=np.column_stack([(constraints(q+np.eye(n)[i]*eps)-constraints(q-np.eye(n)[i]*eps))/(2*eps) for i in range(n)])
    active=np.flatnonzero(c<1e-5)
    multip,res=nnls(jac[active].T,grad,maxiter=20*n) if len(active) else (np.zeros(0),np.linalg.norm(grad))
    # Independent dense witness only; explicitly NOT continuous contact proof.
    dense=[]
    full=np.r_[0.,q]
    for i in range(n):
        for t in np.linspace(0,1,21):
            d=(full[i+1]-full[i])*t;a=full[i]+d/2
            pt=p[i]+h*t*np.sinc(d/(2*np.pi))*np.array([np.cos(a),np.sin(a)])
            dense.append(R-offset-np.linalg.norm(pt-[0.,R]))
    arc=R*math.atan2(p[-1,0],R-p[-1,1]);expected_arc=L*R/(R-offset)
    contact_min=float(continuous_gap(q,n,R).min())
    enddual=float(multip[list(active).index(n+2)]) if n+2 in active else 0.
    return dict(n=n,endstop=endstop,finite_wall_mode=funnel is not None,fixture_angle_deg=math.degrees(theta),solver_success=bool(result.success),message=result.message,
        energy_J=energy(q)*energy_scale,minimum_node_constraint=float(c.min()),sampled_min_gap_m=float(min(dense)),
        stationarity_scaled=float(res),continuous_min_gap_m=contact_min,axial_endstop_reaction_N=enddual*energy_scale/.001,PET_end_projection_m=arc,axial_migration_m=arc-L,
        circular_contact_reference_projection_m=expected_arc,projection_reference_relative=abs(arc-expected_arc)/expected_arc,
        PET_end_angle_rad=float(q[-1]),state_angles_rad=q.tolist(),PET_nodes_m=p.tolist(),
        active_constraints=active.tolist(),scaled_multipliers=multip.tolist(),
        status='PASS' if result.success and c.min()>-1e-5 and contact_min>-1e-9 and res<1e-5 else 'FAIL')
def main():
    global L
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate');p.add_argument('--finite-walls',action='store_true');p.add_argument('--angles',nargs='+',type=float,default=[15.,30.,60.]);p.add_argument('--meshes',nargs='+',type=int,default=[8,16,32]);a=p.parse_args()
    candidate=S2/'revised_cad/revAB_sliding_pet1/summary.json'
    definition={}
    if a.candidate:
        candidate=ROOT/'cad/exports'/a.candidate/'summary.json'
        definition=json.loads(candidate.read_text());L=LR-definition['nominal_end_gap_mm']*.001
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    funnel=definition.get('funnel_profile') if a.finite_walls else None
    if a.finite_walls and funnel is None:raise ValueError('Finite walls require actual funnel candidate profile')
    rows=[]
    for angle in a.angles:
        for n in a.meshes:
            rows.append(solve(n,math.radians(angle),funnel=funnel))
            dump(out/'partial_states.json',dict(rows=rows,complete=False))
    controls=[] if a.finite_walls else [solve(n,math.pi/3,False) for n in (16,32)]
    conv=[]
    for angle in a.angles:
        values=[r for r in rows if abs(r['fixture_angle_deg']-angle)<1e-8];coarse,fine=values[-2:]
        error=abs(coarse['energy_J']-fine['energy_J'])/fine['energy_J'];conv.append(dict(angle_deg=angle,energy_refinement_relative=error,status='PASS' if error<.01 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows+controls+conv) else 'FAIL',scope='FRICTIONLESS FINITE-ROTATION PET / RIGID CIRCULAR RAIL FIXTURE COUPON ONLY',
        PET_free_length_m=L,rows=rows,controls_without_endstop=controls,convergence=conv,producer=ref(out/'producer.py'),candidate=ref(candidate),
        finite_wall_mode=a.finite_walls,
        typical_modulus_not_allowable=True,friction=0,rail_is_prescribed_fixture=True,
        coupled_finger_validated=False,limitations=['No flexible-rail coupling, friction, PET extension, shell wrinkling or material certification','Analytic contact extrema valid only for declared circular rod arcs / circular rigid fixture','Actual 3D finite guide geometry replaced by declared projected channel inequalities'])
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],rows=[{k:r[k] for k in ('n','fixture_angle_deg','status','sampled_min_gap_m','stationarity_scaled','axial_migration_m')} for r in rows],convergence=conv),indent=2))
if __name__=='__main__':main()
