"""Independent P1 saved-state kinematics/virtual work and actual terminal BRep audit."""
import sys,json,math,shutil,copy
from pathlib import Path
import numpy as np
from scipy.optimize._numdiff import approx_derivative
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,box,volume
from primary_module_design import tr,Ry
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir,gp_Circ,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopoDS import TopoDS
sys.path.insert(0,str(ROOT.parent/'stage2_load_transfer/scripts'))
from finger_structure import E_RAIL,E_PET,width

def independent(v,n):
    result=[]
    for j,length,offset in [(0,.088,.0504),(2*n,.0862,.05015)]:
        a=np.r_[0,v[j:j+n]];e=v[j+n:j+2*n]*1e-4;h=length/n;mid=(a[:-1]+a[1:])/2;d=np.diff(a)
        dr=-h*(1+e)*np.sinc(d/(2*np.pi))*np.array([np.sin(mid),np.cos(mid)])
        nodes=np.column_stack((np.r_[offset,offset+np.cumsum(dr[0])],np.r_[-.007,-.007+np.cumsum(dr[1])]))
        EA=2*E_RAIL*.003*.0002 if j==0 else E_PET*width((np.arange(n)+.5)*h)*.0003
        EI=2*E_RAIL*.003*.0002**3/12 if j==0 else E_PET*width((np.arange(n)+.5)*h)*.0003**3/12
        U=np.sum(h*(EA*e**2+EI*(d/h)**2)/2);result.append((nodes,a,e,U))
    a=result[0][1][-1];R=np.array([[np.cos(a),np.sin(a)],[-np.sin(a),np.cos(a)]])
    P=result[0][0][-1]+R@[-.0074,.003];tip=result[0][0][-1]+R@[-.0004,-.005]
    return result,P,tip

def inspect(row):
    n=row['n'];v=np.array(row['state']);data,P,tip=independent(v,n);kin=max(np.max(abs(data[0][0]-row['rail_nodes_m'])),np.max(abs(data[1][0]-row['PET_nodes_m'])),np.max(abs(P-row['cable_port_m'])))
    def U(x):return sum(t[3] for t in independent(x,n)[0])
    grad=np.empty(len(v));JP=np.zeros((2,len(v)));JT=np.zeros_like(JP)
    for i in range(len(v)):
        q=v.astype(complex);q[i]+=1e-25j;d,p,t=independent(q,n);grad[i]=sum(z[3] for z in d).imag/1e-25;JP[:,i]=p.imag/1e-25;JT[:,i]=t.imag/1e-25
    import primary_finger_tangent as analytic
    import primary_finger_equilibrium as model
    J=analytic.constraints_jac(v,n,row['object_inward_stop_m']);Jnum=approx_derivative(lambda x:model.constraints(x,n,row['object_inward_stop_m'])[0],v,method='3-point');jacerr=float(np.max(abs(J-Jnum)));lam=np.array(row['multipliers_N']);g=grad-row['T_N']*(np.array(row['cable_direction'])@JP)-J.T@lam
    scale=np.r_[np.full(n,.088),np.full(n,.088e-4),np.full(n,.0862),np.full(n,.0862e-4)]
    residual=np.linalg.norm(g/scale)
    # Direct cable straight+arc length evaluated independently under port perturbation.
    def length(P):
        D=P-[0,.020];dist=np.linalg.norm(D);alpha=np.arctan2(D[1],D[0]);phi=alpha+np.arccos(.01125/dist)
        return .01125*(np.pi/2-phi)+np.sqrt(dist**2-.01125**2)-.016
    direction=np.array([.37,-.81]);eps=1e-7;numeric=(length(P+eps*direction)-length(P-eps*direction))/(2*eps);expected=-np.array(row['cable_direction'])@direction
    vw=abs(numeric-expected)
    return dict(n=n,T_N=row['T_N'],kinematic_max_m=float(kin),energy_error_J=float(abs(U(v)-row['stored_energy_J'])),independent_force_equivalent_N=float(residual),cable_virtual_work_absolute_error=float(vw),constraint_jacobian_absolute_error_m=jacerr,stored_status=row['status'],passed=bool(kin<1e-13 and abs(U(v)-row['stored_energy_J'])<1e-13 and residual<1e-8 and vw<1e-8 and jacerr<1e-9))

def sectors(row):
    data,_,_=independent(np.array(row['state']),row['n']);p,a,e,U=data[1];n=row['n'];h=.0862/n;shapes=[]
    for i in range(n):
        w=12-.06*(7+i*h*1000);d=a[i+1]-a[i];length=h*(1+e[i]);curv=d/length
        if abs(d)<1e-9:
            shape=box(-.15,-w,-length*1000,.3,2*w,length*1000)
            shape=tr(shape,Ry(a[i]),np.array([p[i,0]*1000,0,p[i,1]*1000]))
        else:
            # Geometry in physical X/Z directly; radial direction is (+cos,-sin).
            centre=p[i]+np.array([-np.cos(a[i]),np.sin(a[i])])/curv
            radius=1000/curv;shift=math.pi if radius<0 else 0;lo,hi=sorted((a[i]+shift,a[i+1]+shift));ri,ro=sorted((abs(radius-.15),abs(radius+.15)))
            axis=gp_Ax2(gp_Pnt(centre[0]*1000,-w,centre[1]*1000),gp_Dir(0,1,0),gp_Dir(1,0,0))
            outer=BRepBuilderAPI_MakeEdge(gp_Circ(axis,ro),lo,hi).Edge();inner=BRepBuilderAPI_MakeEdge(gp_Circ(axis,ri),lo,hi).Edge()
            def end(r,t):return gp_Pnt(centre[0]*1000+r*math.cos(t),-w,centre[1]*1000-r*math.sin(t))
            wire=BRepBuilderAPI_MakeWire();wire.Add(outer);wire.Add(BRepBuilderAPI_MakeEdge(end(ro,hi),end(ri,hi)).Edge());wire.Add(TopoDS.Edge_s(inner.Reversed()));wire.Add(BRepBuilderAPI_MakeEdge(end(ri,lo),end(ro,lo)).Edge());face=BRepBuilderAPI_MakeFace(wire.Wire()).Face();shape=BRepPrimAPI_MakePrism(face,gp_Vec(0,2*w,0)).Shape()
        assert BRepCheck_Analyzer(shape).IsValid();shapes.append(shape)
    return shapes

def main():
    source=ROOT/'validation/finger'/sys.argv[1];out=ROOT/'validation/finger'/sys.argv[2];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');rows=json.loads((source/'cases.json').read_text());candidate=json.loads((ROOT/'PRIMARY_PRODUCT.json').read_text())['candidate_reference'];cad=json.loads((REPO/candidate['path']).read_text());parts={n:read(REPO/cad['part_references'][n]['path']) for n in ('F0_TERMINAL_FRONT','F0_TERMINAL_BACK')};audits=[];geometry=[]
    for row in rows:
        assert not(ROOT/'runtime/STOP').exists();audits.append(inspect(row))
        if row['T_N'] not in (.001,.2):continue
        a=row['rail_angles_rad'][-1];R=Ry(a);end=np.array([row['rail_tip_m'][0]*1000,0,row['rail_tip_m'][1]*1000]);shift=end-R@np.array([50.4,0,-95]);hits=[]
        for i,s in enumerate(sectors(row)):
            local=tr(s,R.T,-R.T@shift)
            for name,part in parts.items():
                v=common(local,part)
                if v>1e-8:hits.append(dict(segment=i,part=name,common_mm3=v))
        geometry.append(dict(n=row['n'],T_N=row['T_N'],hits=hits,status='FAIL' if hits else 'BOUNDED_ENVELOPE_CLEAR'))
    bad=copy.deepcopy(rows[-1]);bad['rail_nodes_m'][-1][0]+=.001;rejected=not inspect(bad)['passed']
    refinement=[]
    for T in sorted(set(r['T_N'] for r in rows)):
        group=sorted([r for r in rows if r['T_N']==T],key=lambda r:r['n']);fine=group[-1];errors=[]
        for r in group[:-1]:
            errors.append(dict(n=r['n'],motion_relative=abs((r['terminal_tip_m'][0]-.05)/(fine['terminal_tip_m'][0]-.05)-1),normal_relative=abs(r['normal_N']/fine['normal_N']-1) if fine['normal_N'] else None))
        refinement.append(dict(T_N=T,errors=errors,criterion_relative=.01,status='PASS' if errors and all(x['motion_relative']<.01 and (x['normal_relative'] is None or x['normal_relative']<.01) for x in errors) else 'FAIL'))
    result=dict(status='ACTUAL_P1_SAVED_STATE_PARTIAL_AUDIT_NOT_RELEASE',candidate=candidate,source=ref(source/'summary.json'),cases=ref(source/'cases.json'),audits=audits,actual_terminal_BRep=geometry,refinement=refinement,perturbed_kinematics_rejected=rejected,passed_state_checks=sum(a['passed'] for a in audits),failed_state_checks=sum(not a['passed'] for a in audits),whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Analytic contact Jacobian checked against independent finite differences, not a proof of surface completeness','Max-width envelope can conservatively reject taper','Material-pair normal witnesses are not full surface contact or friction','No100g grasp, certified strength, full energy, hardware or Stage3'])
    dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(2 if any(x['status']=='FAIL' for x in geometry+refinement) or not all(a['passed'] for a in audits) else 0)
if __name__=='__main__':main()
