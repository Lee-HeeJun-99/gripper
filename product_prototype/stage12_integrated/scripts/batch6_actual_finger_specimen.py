"""AO imported-STEP rail pair under an actual REST tendon wrench.

Conditional planar, small-deflection reference. No PET/contact load sharing,
terminal fastener connector or Root/Ground stiffness is certified here.
"""
import json, math, shutil, sys
import numpy as np
from pathlib import Path
from baseline_registry import ROOT, REPO, S1, S2, ref, sha, dump
sys.path.insert(0, str(S1/'scripts'))
from incremental_stage1 import read, box, bounds
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer

def section(shape, z, h):
    slab=BRepAlgoAPI_Common(shape,box(40,-30,z-h/2,20,60,h)).Shape()
    g=GProp_GProps();BRepGProp.VolumeProperties_s(slab,g,1e-10)
    a=g.Mass()/h;c=g.CentreOfMass()
    # Volume Iyy includes finite slab z variance; remove it analytically.
    iy=g.MatrixOfInertia().Value(2,2)/h-a*h*h/12
    return dict(z_mm=z,h_mm=h,area_mm2=a,Iyy_mm4=iy,centroid_x_mm=c.X())

def fem(n, EA, EI, F, M, N, L=88.):
    h=L/n;K=np.zeros((3*(n+1),)*2)
    for j in range(n):
        ids=[3*j,3*j+1,3*j+3,3*j+4]
        k=EI/h**3*np.array([[12,6*h,-12,6*h],[6*h,4*h*h,-6*h,2*h*h],[-12,-6*h,12,-6*h],[6*h,2*h*h,-6*h,4*h*h]])
        K[np.ix_(ids,ids)]+=k
        ids=[3*j+2,3*j+5];K[np.ix_(ids,ids)]+=EA/h*np.array([[1,-1],[-1,1]])
    f=np.zeros(len(K));f[-3:]=[F,M,N];u=np.zeros(len(K));u[3:]=np.linalg.solve(K[3:,3:],f[3:]);r=K@u-f
    U=float(.5*u@K@u)
    return dict(n=n,tip_x_mm=float(u[-3]),tip_rotation_rad=float(u[-2]),tip_s_mm=float(u[-1]),root_reaction=[float(x) for x in r[:3]],energy_Nmm=U,work_Nmm=float(.5*f@u),free_residual=float(max(abs(r[3:]))))

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/finger/batch6_actual_specimen3';out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAO_root2/summary.json';d=json.loads(source.read_text());refs=d['part_references']
    names=['F0_RAIL_L','F0_RAIL_R','F0_SKIN','F0_TERMINAL_FRONT','F0_TERMINAL_BACK','F0_ROOT_FRONT','F0_ROOT_BACK','PALM','F0_IDLER','F0_DRUM','F0_TENDON_WIRE']
    assert all(sha(REPO/refs[n]['path'])==refs[n]['SHA256'] for n in names)
    dump(out/'inputs.json',dict(candidate=ref(source),parts={n:refs[n] for n in names},producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/baseline_registry.py'),ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(S2/'scripts/finger_structure.py'),ref(S2/'models/materials/evidence.json')],checks=dict(section_relative_max=1e-6,mesh_relative_max=.01,balance_absolute_max=1e-8,energy_relative_max=1e-8),contract='AO only, not AV/AX/AY. REST prescribed tangent to AO Idler radius11.25mm. Two projected Rail beams between actual Root lower and Terminal upper envelope cuts; rigid terminal offsets to swivel43,0,-92; ideal clamped Rail cut at z=-7. PET freely slips and carries no load in this deliberate reference. No actual joint/load-sharing or Ground certification. E=193000N/mm2 typical conditional, not minimum.',loading='0.001N diagnostic tension;1N extrapolation reported with linear-domain rejection, neither actual demand nor allowable. No powered motion.'))
    shapes={n:read(REPO/refs[n]['path']) for n in names}
    root_z=bounds(shapes['F0_ROOT_FRONT'])[2];tip_z=bounds(shapes['F0_TERMINAL_BACK'])[5]
    sections=[]
    for n in ('F0_RAIL_L','F0_RAIL_R'):
        for z in np.linspace(root_z-1,tip_z+1,5):
            assert not (ROOT/'runtime/STOP').exists()
            for h in (.02,.01):sections.append(dict(part=n,**section(shapes[n],z,h)))
    A=sum(np.mean([r['area_mm2'] for r in sections if r['part']==n]) for n in ('F0_RAIL_L','F0_RAIL_R'))
    I=sum(np.mean([r['Iyy_mm4'] for r in sections if r['part']==n]) for n in ('F0_RAIL_L','F0_RAIL_R'))
    cx=float(np.mean([r['centroid_x_mm'] for r in sections]));E=193000.;L=root_z-tip_z
    P=np.array([43.,0.,-92.]);C=np.array([44.,0.,25.]);v=P-C;D=np.linalg.norm(v);u=v/D
    # Tangency: (P-Q).(Q-C)=0, Q on circle; choose left contact branch.
    normal=11.25/D*u+math.sqrt(1-(11.25/D)**2)*np.array([u[2],0,-u[0]])
    Q=C+11.25*normal;t=(Q-P)/np.linalg.norm(Q-P)
    # s=-z, positive beam rotation moves tip towards +x.
    tension=.001;F=float(t[0]*tension);N=float(-t[2]*tension);e=43-cx;offset=tip_z-P[2];M=offset*F-e*N
    cases=[fem(n,E*A,E*I,F,M,N,L) for n in (8,16,32,64)]
    exact=dict(tip_x_mm=(F*L**3/3+M*L**2/2)/(E*I),tip_rotation_rad=(F*L**2/2+M*L)/(E*I),tip_s_mm=N*L/(E*A),energy_Nmm=.5*((F*F*L**3/3+F*M*L*L+M*M*L)/(E*I)+N*N*L/(E*A)))
    section_error=max(max(abs(r['area_mm2']/.6-1),abs(r['Iyy_mm4']/.002-1)) for r in sections)
    reference_error=max(abs(c[k]/exact[k]-1) for c in cases for k in exact)
    balance=max(max(abs(c['root_reaction'][0]+F),abs(c['root_reaction'][1]+F*L+M),abs(c['root_reaction'][2]+N),c['free_residual']) for c in cases)
    checks=dict(imported_solids=all(BRepCheck_Analyzer(s).IsValid() for s in shapes.values()),CAD_section_vs_rectangle=section_error<1e-6,FEM_vs_Castigliano=reference_error<.01,force_moment_balance=balance<1e-8,energy_work=all(abs(c['energy_Nmm']/c['work_Nmm']-1)<1e-8 for c in cases),tangent=abs(float((P-Q)@(Q-C)))<1e-8)
    checks={k:bool(v) for k,v in checks.items()}
    rotation_per_N=exact['tip_rotation_rad']/tension
    result=dict(status='ACTUAL_AO_CONDITIONAL_RAIL_REFERENCE_VERIFIED' if all(checks.values()) else 'ACTUAL_AO_REFERENCE_FAIL',scope='ACTUAL_AO_REST_LINEAR_RAIL_LOAD_SPECIMEN_PARTIAL',revision='revAO_root2',inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm={n:list(bounds(s)) for n,s in shapes.items()},sections=sections,checks=checks,section_relative_error=section_error,FEM_reference_relative_error=reference_error,balance_absolute_error=balance,E_N_mm2=E,combined_A_mm2=float(A),combined_Iyy_mm4=float(I),rail_axis_x_mm=cx,cut_root_z_mm=root_z,cut_tip_z_mm=tip_z,L_mm=L,terminal_offset_s_mm=float(offset),tendon=dict(P_mm=P.tolist(),Q_mm=Q.tolist(),direction=t.tolist(),tension_N=tension),equivalent_tip_wrench_N_Nmm=[F,M,N],exact=exact,refinements=cases,extrapolation_1N=dict(rotation_rad=rotation_per_N,small_rotation_005rad=bool(abs(rotation_per_N)<=.005),meaning='Diagnostic extrapolation only; .005rad local reference domain, not a replacement for FrameLayer or release tolerances'),conditional_005rad_tension_N=.005/abs(rotation_per_N),actual_capacity_qualified=False,actual_demand_N=None,whole_system_release=False,changed_part_IDs=[],custom_parts_removed=0,custom_processes_removed=0,limitations=['Rail-only projected linear reference; PET contact, oblique Rail torsion and terminal fastener stiffness/load sharing omitted','Root/Terminal envelope cuts idealize grip; no verified connector to Palm/Ground or proof of grip stiffness','Compression geometric stiffness/buckling, finite deformation, notch/pin bearing and certified material absent','Motor/protection/anchor/Idler ratings absent; no complete Motor-to-Ground specimen or energy certificate','Historical AO full assembly FAIL and contact/time convergence FAIL remain unchanged'])
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,rotation_per_N=rotation_per_N,reference_error=reference_error)))
    raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
