"""Conditional assembly-misalignment beam frame. No motor material approval.
Actual output-shaft BRep sections, manufacturer motor shaft dimensions.
Rigid coupling links finite shaft contact centroids; bearing translations fixed.
"""
import argparse,json,math,sys,shutil
from pathlib import Path
import numpy as np
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from extract_geometry import load,properties,sha,S1
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Pnt
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);args=ap.parse_args()
    out=ROOT/'validation/coupling'/args.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    path=S1/'cad/parts/revAA_mbd1/F0_SHAFT.step';shaft=load(path)
    ys=np.array([-44.,-35.,-26.,-15.25,-12.5,-12.4,-12.1,-9.,-8.5,-6.,-3.5,1.75,3.25,9.,11.5])*.001
    inlet=2;outlet=3;supports=[int(np.flatnonzero(abs(ys-y)<1e-12)[0]) for y in (-.006,.0115)]
    gauss,weights=np.polynomial.legendre.leggauss(3)
    sections=[]
    for i in range(outlet,len(ys)-1):
        for xi,w in zip((gauss+1)/2,weights/2):
            y=1000*(ys[i]+xi*(ys[i+1]-ys[i]));h=.005
            slab=BRepPrimAPI_MakeBox(gp_Pnt(60,y-h/2,0),40,h,40).Shape()
            v,c,j=properties(BRepAlgoAPI_Common(shaft,slab).Shape())
            sections.append(dict(element=i,xi=float(xi),weight=float(w),Ixx_m4=float(j[0,0]/(h*.001)),Izz_m4=float(j[2,2]/(h*.001))))
    (out/'model_sections.json').write_text(json.dumps(sections,indent=2)+'\n')
    # D section x<=2 mm from nominal5 mm shaft, last15 mm of24 mm shaft.
    r=.0025;flat=.002
    area=quad(lambda x:2*math.sqrt(max(0,r*r-x*x)),-r,flat,epsabs=1e-14)[0]
    cx=quad(lambda x:2*x*math.sqrt(max(0,r*r-x*x)),-r,flat,epsabs=1e-14)[0]/area
    Iz=quad(lambda x:2*(x-cx)**2*math.sqrt(max(0,r*r-x*x)),-r,flat,epsabs=1e-16)[0]
    Ix=quad(lambda x:2/3*max(0,r*r-x*x)**1.5,-r,flat,epsabs=1e-16)[0]
    rows=[]
    for direction in ('X','Z'):
        for motor_E in (193e9,200e9,210e9):
            N=2*len(ys);K=np.zeros((N,N));patch_errors=[]
            for i in list(range(2))+list(range(outlet,len(ys)-1)):
                length=ys[i+1]-ys[i];ke=np.zeros((4,4))
                for xi,w in zip((gauss+1)/2,weights/2):
                    if i<2:
                        inertia=math.pi*r**4/4 if i==0 else (Iz if direction=='X' else Ix)
                        EI=motor_E*inertia
                    else:
                        entry=next(s for s in sections if s['element']==i and abs(s['xi']-xi)<1e-12)
                        EI=193e9*entry['Izz_m4' if direction=='X' else 'Ixx_m4']
                    B=np.array([(-6+12*xi)/length**2,(-4+6*xi)/length,(6-12*xi)/length**2,(-2+6*xi)/length])
                    ke+=w*length*EI*np.outer(B,B)
                if i==0:
                    exact=motor_E*(math.pi*r**4/4)/length**3*np.array([[12,6*length,-12,6*length],[6*length,4*length**2,-6*length,2*length**2],[-12,-6*length,12,-6*length],[6*length,2*length**2,-6*length,4*length**2]])
                    patch_errors.append(float(np.linalg.norm(ke-exact)/np.linalg.norm(exact)))
                ids=np.arange(2*i,2*i+4);K[np.ix_(ids,ids)]+=ke
            constrained={0,1,2*outlet,2*outlet+1,*[2*i for i in supports]}
            free=[i for i in range(N) if i not in constrained];T=np.zeros((N,len(free)))
            for j,i in enumerate(free):T[i,j]=1
            T[2*outlet]=T[2*inlet]+(ys[outlet]-ys[inlet])*T[2*inlet+1]
            T[2*outlet+1]=T[2*inlet+1]
            prescribed=np.zeros(N);prescribed[0]=1e-6
            q=np.linalg.solve(T.T@K@T,-T.T@K@prescribed);u=prescribed+T@q;reaction=K@u
            stiffness=abs(reaction[0])/1e-6
            energy=.5*float(u@K@u);work=.5*reaction[0]*1e-6
            residual=float(np.linalg.norm(T.T@reaction));balance_force=abs(float(reaction[0]+sum(reaction[2*i] for i in supports)))
            rows.append(dict(direction=direction,assumed_motor_E_Pa=motor_E,assumed_shaft_E_Pa=193e9,
                misalignment_radial_stiffness_N_m=float(stiffness),motor_radial_N_at_0_25mm=float(stiffness*.00025),
                conditional_offset_limit_m_at_10_5N=float(10.5/stiffness),unit_offset_motor_moment_Nm=float(reaction[1]),
                equilibrium_free_force_residual=residual,force_balance_N=balance_force,
                energy_relative_error=abs(energy-work)/max(abs(energy),1e-30),element_patch_error=max(patch_errors),
                status='PASS' if residual<1e-8 and balance_force<1e-8 and abs(energy-work)/abs(energy)<1e-8 and max(patch_errors)<1e-10 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
        scope='CONDITIONAL ALIGNMENT SENSITIVITY / MODEL VERIFICATION, NOT MOTOR LOAD APPROVAL',
        rows=rows,actual_shaft_sections=sections,source_SHA256=sha(Path(__file__)),STEP_SHA256=sha(path),
        manufacturer_reference='A0648 dynamic radial21N maximum at20mm shaft station; NOT general combined force/moment envelope',
        conclusion='Clearance fit/pilot play is NOT an alignment tolerance. Numerical offset limits are conditional; actual motor material, bearing compliance and housing flexibility require validation.',
        exclusions=['actual motor shaft alloy','housing/plate compliance','bearing clearance/stiffness','nonlinear coupling contact','thread helix root correction','complete angular misalignment'],
        command='PYTHONPATH=/tmp/regrip_stage1_ocp python scripts/shaft_alignment.py --tag '+args.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='actual_shaft_sections'},indent=2))
if __name__=='__main__':main()
