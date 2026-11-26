"""Finite AK bore/D-shaft conditional unilateral wrench feasibility.
No elastic closure, bolt preload, friction assignment or safe capacity claim.
"""
import argparse, ast, json, math, shutil, sys
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,S1,REPO,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from fastener_joint_contract import cylinders,project_interval
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN
from OCP.gp import gp_Pnt

def solve(points,r,rwire,axial,k):
    # Inscribed Coulomb disk: each nonnegative ray carries one unit normal.
    cols=[]
    for theta,y in points:
        er=np.array([math.cos(theta),0,math.sin(theta)])
        et=np.array([-math.sin(theta),0,math.cos(theta)])
        pos=np.array([r*er[0],y,r*er[2]])
        for phi in np.arange(k)*2*math.pi/k:
            f=-er+math.cos(phi)*et+np.array([0,math.sin(phi),0])
            cols.append(np.r_[f,np.cross(pos,f)/rwire,1.])
    A=np.array(cols).T
    load=np.array([0,axial,0,0,1,0,0.])
    eq=np.column_stack([A,load]);target=np.array([0,0,0,0,0,0,1.])
    opt=linprog(np.r_[np.zeros(A.shape[1]),-1],A_eq=eq,b_eq=target,bounds=(0,None),method='highs')
    if not opt.success:return dict(success=False,message=opt.message),None
    x=opt.x;res=eq@x-target
    # Save sparse tractions for independent reconstruction, not just solver exit.
    active=[dict(column=int(j),weight=float(x[j])) for j in np.flatnonzero(x[:-1]>1e-12)]
    row=dict(success=True,message=opt.message,T_per_unit_normal=float(x[-1]),max_equilibrium_residual=float(abs(res).max()),minimum_weight=float(x.min()),active=active,points=len(points),rays=k)
    return row,dict(matrix=A,solution=x)

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    assert not (ROOT/'runtime/STOP').exists(),'STOP'
    out=ROOT/'validation/transmission'/a.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(src.read_text())
    motor=S1/'scripts/sourced_motor_stage1.py';tree=ast.parse(motor.read_text())
    expr=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MOTOR_SPEC' for t in n.targets))
    spec={k.arg:ast.literal_eval(k.value) for k in expr.keywords}
    hubref=d['part_references']['F0_CLUTCH_INPUT_HUB'];hubfile=REPO/hubref['path'];assert sha(hubfile)==hubref['SHA256']
    inputs=[ref(src),ref(hubfile),ref(motor),ref(out/'producer.py')];dump(out/'inputs_before_analysis.json',inputs)
    # Predeclared bounded numerical acceptance; no system tolerance changed.
    criteria=dict(equilibrium_absolute=1e-8,finest_relative_change=.01,analytic_upper_slack=1e-8,normalization=1.,shaft_mu_control=1.,face_mu_control=1.)
    dump(out/'acceptance.json',criteria)
    hub=read(hubfile);bores=[c for c in cylinders(hub) if abs(c['r']-2.52)<1e-7 and abs(c['axis'][1])>1-1e-8]
    lo=min(project_interval(c,[0,1,0])[0] for c in bores);hi=max(project_interval(c,[0,1,0])[1] for c in bores)
    R=bores[0]['r'];r=spec['shaft_diameter_mm'][0]/2
    tip=d['motor_flange_Y_mm']+spec['shaft_length_mm'][0];end=min(hi,tip);mid=(lo+end)/2
    flat=spec['D_flat_across_mm'][0]-r
    flat_start_max=d['motor_flange_Y_mm']+max(spec['shaft_length_mm'])-min(spec['D_flat_length_mm'])
    assert flat_start_max<lo
    wire=d['torque_model']['nominal_drum_wire_radius_mm']/1000
    axial=wire/(d['torque_model']['annulus_inner_mm']/1000)
    upper=1/math.hypot(wire/(r/1000),axial)
    rows=[];states=[]
    for n,k in ((48,16),(96,32),(192,64)):
        assert not (ROOT/'runtime/STOP').exists(),'STOP'
        points=[]
        for theta in (np.arange(n)+.5)*2*math.pi/n:
            if r*math.cos(theta)>flat:continue # D-flat has no circular first-touch patch.
            for y in (lo+(end-lo)/6,mid,end-(end-lo)/6):
                q=gp_Pnt(110+(R+.001)*math.cos(theta),y,20+(R+.001)*math.sin(theta))
                if BRepClass3d_SolidClassifier(hub,q,1e-8).State()==TopAbs_IN:
                    points.append((float(theta),(y-mid)/1000))
        row,state=solve(points,r/1000,wire,axial,k);row.update(angles=n,contact_points=points)
        rows.append(row)
        if state is not None:
            np.savez_compressed(out/f'state_{n}.npz',**state)
        dump(out/f'case_{n}.json',row)
    good=all(x['success'] and x['max_equilibrium_residual']<criteria['equilibrium_absolute'] and x['T_per_unit_normal']<=upper+1e-8 for x in rows)
    change=abs(rows[-1]['T_per_unit_normal']/rows[-2]['T_per_unit_normal']-1) if all(x['success'] for x in rows) else None
    good=good and change is not None and change<.01
    result=dict(status='CONDITIONAL_CONTACT_WRENCH_PASS' if good else 'CONDITIONAL_CONTACT_WRENCH_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inputs=inputs,criteria=criteria,
        scope='Actual AK finite bore, minimum supplier D-shaft; prescribed circular first-touch closure and unit normal budget, dimensionless unit friction controls ONLY',
        geometry=dict(bore_Y_mm=[lo,hi],minimum_engagement_Y_mm=[lo,end],bore_radius_mm=R,shaft_radius_mm=r,D_flat_X_from_axis_mm=flat,latest_flat_start_Y_mm=flat_start_max,radial_first_touch_closure_mm=R-r,flat_center_gap_at_first_touch_mm=r-flat,nominal_unclosed_radial_gap_mm=R-r),
        axial_force_per_unit_tendon=axial,analytic_coulomb_upper_T_per_unit_normal=upper,finest_relative_change=change,
        cases=[{key:v for key,v in row.items() if key not in ('active','contact_points')} for row in rows],
        frictionless_circular_normal_torque_capacity=0,nominal_unclosed_contact_capacity=0,
        limits=['First-touch radial closure is prescribed, NOT a solved deformation or bolt-preload/contact law','D-flat is not a mating torque key in circular bore; flat contact after deformation is unmodeled','No pressure distribution, elastic hub strain, bolt proof or available normal force qualified','Unit friction is a dimensionless control, not a material estimate; no N or Nm safe capacity assigned','Motor axial bearing rating, spring/friction bounds and transient maximum remain missing'],actual_capacity_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2));return 0 if good else 2
if __name__=='__main__':raise SystemExit(main())
