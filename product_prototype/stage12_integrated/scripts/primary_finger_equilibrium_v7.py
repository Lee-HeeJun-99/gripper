"""P1 actual cable-port, separate extensible Rail/PET static continuation.
Conditional planar strip reduction. Contact witnesses are NOT a surface CCD.
No release/capacity claim. Root ideal clamp is explicitly an assumption.
"""
import sys,json,shutil,math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,nnls
from scipy.optimize._numdiff import approx_derivative
from baseline_registry import ROOT,REPO,ref,dump,sha,S1
from rod_point_jacobian import integrated,walls
sys.path.insert(0,str(ROOT.parent/'stage2_load_transfer/scripts'))
from finger_structure import E_RAIL,E_PET,width
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,volume
from OCP.BRepCheck import BRepCheck_Analyzer
import primary_finger_tangent_v7 as tangent
EXTRA_POINTS=[]
CHECKPOINT=None
L=.077;LP=.0862;ES=1e-4;US=1e-4;GS=1e-3

def rod(v,length,n,pet=False,stations=None):
    th=np.r_[0.,v[:n]];e=v[n:]*ES;h=length/n
    p=np.array([.05015 if pet else .0504,-.007]);nodes=[p]
    for i in range(n):
        w=integrated(float(th[i]),float(th[i+1]),h,1)[0]*(1+e[i])
        p=p+np.array([-w.imag,-w.real]);nodes.append(p)
    if stations is None:return np.array(nodes),th,e
    result=[]
    for s in stations:
        if s>length:
            angle=th[-1];result.append((nodes[-1]+(s-length)*np.array([-np.sin(angle),-np.cos(angle)]),angle));continue
        i=min(int(s/h),n-1);t=(s-i*h)/h
        w=integrated(float(th[i]),float(th[i+1]),h,t)[0]*(1+e[i])
        angle=(1-t)*th[i]+t*th[i+1]
        result.append((nodes[i]+np.array([-w.imag,-w.real]),angle))
    return result

def state(v,n):
    r,tr,er=rod(v[:2*n],L,n);p,tp,ep=rod(v[2*n:],LP,n,True)
    a=tr[-1];c,s=np.cos(a),np.sin(a);R=np.array([[c,s],[-s,c]])
    P=r[-1]+R@np.array([-.0074,-.008]);tip=r[-1]+R@np.array([-.0004,-.016])
    C=np.array([0.,.020]);u=(P-C)/np.linalg.norm(P-C);k=.01125/np.linalg.norm(P-C)
    normal=k*u+np.sqrt(1-k*k)*np.array([-u[1],u[0]])
    Q=C+.01125*normal;t=(Q-P)/np.linalg.norm(Q-P)
    free=.01125*(np.pi/2-np.arctan2(normal[1],normal[0]))+np.linalg.norm(P-Q)-.016
    return r,p,tr,tp,er,ep,R,P,tip,t,free

def energy(v,n,T):
    r,p,tr,tp,er,ep,R,P,tip,t,free=state(v,n)
    sr=(np.arange(n)+.5)*L/n;sp=(np.arange(n)+.5)*LP/n
    EAr=2*E_RAIL*.003*.0002;EIr=2*E_RAIL*.003*.0002**3/12
    EAp=E_PET*width(sp)*.0003;EIp=E_PET*width(sp)*.0003**3/12
    U=np.sum(L/n*(EAr*er**2+EIr*(np.diff(tr)/(L/n))**2)/2)+np.sum(LP/n*(EAp*ep**2+EIp*(np.diff(tp)/(LP/n))**2)/2)
    return float(U),float(free)

def constraints(v,n,delta,dense=2):
    r,p,tr,tp,er,ep,R,P,tip,t,free=state(v,n)
    stations=np.array(sorted(set(np.linspace(0,LP,dense*n+1)[1:].tolist()+[L]+EXTRA_POINTS)))
    rr=rod(v[:2*n],L,n,stations=stations);pp=rod(v[2*n:],LP,n,True,stations)
    g=[];labels=[]
    for s,(pr,a),(ps,b) in zip(stations,rr,pp):
        # Exact circular-strip side offsets, material witness pairing.
        nr=np.array([-np.cos(a),np.sin(a)]);np_=np.array([-np.cos(b),np.sin(b)])
        g.append(float((ps-.00015*np_-pr-.0001*nr)@nr));labels.append(('interface',float(s)))
    # Actual terminal front/back/funnel SDF in terminal rest coordinates.
    for s,(ps,a) in zip(stations,pp):
        if s<L:continue
        for side in (-1,1):
            z=ps+side*.00015*np.array([-np.cos(a),np.sin(a)])
            local=R.T@(z-r[-1])+np.array([.0504,-.084])
            val,_=walls(local,np.array([-.03363880995252074,-.095]),.08350880995252075)
            g.extend(val.tolist());labels.extend([('terminal_'+str(side)+'_'+str(j),float(s)) for j in range(3)])
    if delta is not None:g.append(float(tip[0]-(.050-delta)));labels.append(('object',0.))
    return np.array(g),labels

def feature_stations(v,n):
    """Finite side-arc extrema, CAD face planes and circle/plane seam roots.
    Witness material coordinates stay fixed during each nonlinear solve.
    Recompute after Newton; never accept a subsequent unchecked polish.
    """
    from scipy.optimize import brentq,minimize_scalar
    from rod_point_jacobian import rectangle
    r,p,tr,tp,er,ep,R,P,tip,t,free=state(v,n)
    def point(s,side):
        ps,a=rod(v[2*n:],LP,n,True,[s])[0]
        return R.T@(ps+side*.00015*np.array([-np.cos(a),np.sin(a)])-r[-1])+[.0504,-.084]
    knots=sorted(set([L,LP]+[x for x in np.linspace(0,LP,n+1) if L<x<LP]));found=set(knots)
    for side in (-1,1):
        for left,right in zip(knots[:-1],knots[1:]):
            funcs=[lambda s,axis=axis,level=level:point(s,side)[axis]-level for axis,levels in [(0,(.040,.04898,.049,.0499,.050)),(1,(-.100,-.095,-.090,-.084))] for level in levels]
            funcs.append(lambda s:rectangle(point(s,side),[.04898,-.095],[.04990,-.090])[0]-(np.linalg.norm(point(s,side)-[-.03363880995252074,-.095])-.08350880995252075))
            for fn in funcs:
                split=np.linspace(left,right,9)
                for a,b in zip(split[:-1],split[1:]):
                    if fn(a)*fn(b)<0:found.add(float(brentq(fn,a,b,xtol=1e-15)))
            for j in range(3):
                fn=lambda s:walls(point(s,side),np.array([-.03363880995252074,-.095]),.08350880995252075)[0][j]
                opt=minimize_scalar(fn,bounds=(left,right),method='bounded',options={'xatol':1e-16})
                if opt.fun<1e-7:found.add(float(opt.x))
    return sorted(found)

def solve(n,T,delta,seed=None):
    global EXTRA_POINTS
    EXTRA_POINTS=[];tangent.EXTRA_POINTS=[]
    v=np.zeros(4*n) if seed is None else seed.copy()
    obj=lambda x:(energy(x,n,T)[0]+T*energy(x,n,T)[1])/US
    cf=lambda x:constraints(x,n,delta)[0]/GS
    exchange_history=[]
    for exchange in range(12):
        EXTRA_POINTS=sorted(set(EXTRA_POINTS+feature_stations(v,n)));tangent.EXTRA_POINTS=EXTRA_POINTS.copy()
        sol=minimize(obj,v,method='SLSQP',jac=lambda x:tangent.gradient(x,n,T,E_RAIL,E_PET,width)/US,constraints=[dict(type='ineq',fun=cf,jac=lambda x:tangent.constraints_jac(x,n,delta)/GS)],options=dict(ftol=1e-16,maxiter=350),bounds=[(-1.4,1.4)]*n+[(-100,100)]*n+[(-1.4,1.4)]*n+[(-100,100)]*n)
        candidate,prepolish=tangent.polish(sol.x,n,T,delta,sys.modules[__name__])
        frozen=EXTRA_POINTS.copy();features=feature_stations(candidate,n)
        EXTRA_POINTS=sorted(set(frozen+features));dg,dl=constraints(candidate,n,delta,24);EXTRA_POINTS=frozen
        worst=float(dg.min());where=dl[int(dg.argmin())]
        exchange_history.append(dict(exchange=exchange,optimizer_success=bool(sol.success),message=str(sol.message),minimum_dense_gap_m=worst,witness=where,extra_points=EXTRA_POINTS.copy(),feature_witnesses=features,prepolish=prepolish))
        v=candidate
        if CHECKPOINT is not None:CHECKPOINT(n,T,exchange,candidate,exchange_history,EXTRA_POINTS)
        if worst>=-1e-12:break
        EXTRA_POINTS=sorted(set(frozen+features+[where[1]]))
    tangent.EXTRA_POINTS=EXTRA_POINTS.copy()
    polishing=exchange_history[-1]["prepolish"];g,labels=constraints(v,n,delta);J=tangent.constraints_jac(v,n,delta);grad=tangent.gradient(v,n,T,E_RAIL,E_PET,width)
    active=np.flatnonzero(g<1e-8)
    lam=np.zeros(len(g));weights=1/np.r_[np.full(n,L),np.full(n,ES*L),np.full(n,LP),np.full(n,ES*LP)];lam[active]=nnls((J[active]*weights).T,grad*weights,maxiter=10000)[0] if len(active) else []
    residual=grad-J.T@lam
    # Scaled generalized residual in Newton-equivalent units.
    res=float(np.linalg.norm(residual/np.r_[np.full(n,L),np.full(n,ES*L),np.full(n,LP),np.full(n,ES*LP)]))
    dense,dl=constraints(v,n,delta,24);r,p,tr,tp,er,ep,R,P,tip,t,free=state(v,n);U,_=energy(v,n,T)
    moment=float(np.cross(P-np.array([.0504,-.007]),T*t));N=float(lam[-1]) if delta is not None else 0.
    root=-(T*t+np.array([N,0.]));M=-moment-float(np.cross(tip-np.array([.0504,-.007]),np.array([N,0.])))
    artificial=bool(max(abs(v[:n]))>1.399 or max(abs(v[2*n:3*n]))>1.399 or max(abs(np.r_[er,ep]))>.00999)
    return dict(n=n,rail_free_length_m=L,terminal_anchor_Z_m=-.084,T_N=T,object_inward_stop_m=delta,optimizer_success=bool(sol.success),optimizer_message=sol.message,iterations=int(sol.nit),polishing=polishing,contact_exchange=exchange_history,extra_contact_stations_m=EXTRA_POINTS.copy(),state=v.tolist(),rail_nodes_m=r.tolist(),PET_nodes_m=p.tolist(),rail_angles_rad=tr.tolist(),PET_angles_rad=tp.tolist(),rail_strain=er.tolist(),PET_strain=ep.tolist(),rail_tip_m=r[-1].tolist(),terminal_tip_m=tip.tolist(),cable_port_m=P.tolist(),cable_direction=t.tolist(),free_cable_m=free,stored_energy_J=U,normal_N=N,root_total_force_N=root.tolist(),root_total_moment_Nm=M,tendon_torque_Nm=T*.01125,KKT_force_equivalent_N=res,minimum_sample_gap_m=float(g.min()),minimum_dense_gap_m=float(dense.min()),dense_witness=dl[int(dense.argmin())],complementarity_J=float(np.max(abs(lam*g))),artificial_bound_active=artificial,multipliers_N=lam.tolist(),constraint_labels=labels,status='CONDITIONAL_EQUILIBRIUM' if (sol.success or polishing['success']) and res<1e-8 and dense.min()>=-1e-9 and not artificial else 'FAIL')

def main():
    tag=sys.argv[1];out=ROOT/'validation/finger'/tag;assert not (ROOT/'runtime/STOP').exists();out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/primaryP1_open9/summary.json';d=json.loads(src.read_text());inventory=[]
    for name in ('F0_SKIN','F0_RAIL_L','F0_RAIL_R','F0_TERMINAL_FRONT','F0_TERMINAL_BACK','F0_ROOT_BACK','F0_SWIVEL_AXLE'):
        q=d['part_references'][name];assert sha(REPO/q['path'])==q['SHA256'];s=read(REPO/q['path']);assert BRepCheck_Analyzer(s).IsValid();inventory.append(dict(part=name,source=q,bounds_mm=bounds(s),volume_mm3=volume(s)))
    deps=[Path(__file__),ROOT/'scripts/batch6_actual_finger_specimen.py',ROOT/'cad/exports/revAD_funnel1/summary.json',ROOT/'scripts/rod_point_jacobian.py',ROOT/'scripts/primary_finger_tangent_v7.py',ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py',src,ROOT/'models/materials/primary_material_contract1.json']
    dump(out/'inputs.json',dict(candidate=ref(src),inputs=[ref(p) for p in deps],inventory=inventory,rail_free_length_m=L,terminal_anchor_Z_m=-.084,criteria=dict(force_equivalent_N_max=1e-8,gap_m_min=-1e-9,mesh_relative_max=.01),assumptions=['P1 actual rest datum and cable circle/terminal port; two .2x3mm Rail free spans and original tapered PET','Root cut at-7mm; actual terminal upper envelope at-84mm gives77mm free Rail then rigid cuff; PET86.2mm free axial tip; sampled unilateral frictionless surfaces','Separate finite circular-arc rotations and engineering strain; conditional typical moduli','No closest-point surface guarantee: dense witness rejection required; no contact/friction/mesh/strength release'],object='Optional unilateral fixed spatial X stop at actual terminal bottom; no100g weight mislabeled tendon force',terminal_funnel='Historical wall model with candidate geometry checked below; applicability requires independent actual BRep audit'))
    rows=[]
    operating=len(sys.argv)>2 and sys.argv[2]=='operating'
    for n in tuple(map(int,sys.argv[3:] if operating else sys.argv[2:])) or (8,16,32):
        seed=None
        for T,delta in (((.2,.020),(.5,.020),(1.,.020),(2.,.020)) if operating else ((.00001,None),(.001,None),(.01,.005),(.05,.010),(.2,.020))):
            assert not (ROOT/'runtime/STOP').exists();row=solve(n,T,delta,seed);rows.append(row);dump(out/'cases.json',rows)
            if row['optimizer_success']:seed=np.array(row['state'])
    result=dict(status='ACTUAL_P1_CONDITIONAL_STATIC_RESULTS_NOT_RELEASE',candidate=ref(src),task_id='goal_primary_terminal_feature_contact',inputs=ref(out/'inputs.json'),cases=ref(out/'cases.json'),rows=len(rows),conditional_equilibria=sum(r['status']=='CONDITIONAL_EQUILIBRIUM' for r in rows),failed_rows=sum(r['status']=='FAIL' for r in rows),whole_system_release=False,newly_qualified_system_gate_ids=[],remaining_system_gate_ids=json.loads((ROOT/'PRIMARY_PRODUCT.json').read_text())['remaining_gates'],next_mechanism='Independent actual deformed terminal/PET BRep and continuum-contact force certificate before using reactions; retain all failed rows and no system gate promotion',SOFA_runs=0)
    dump(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
