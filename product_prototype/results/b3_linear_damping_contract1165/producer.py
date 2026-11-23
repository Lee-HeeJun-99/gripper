"""Read-only discriminate implicit field-Rayleigh RHS contracts;no solver change."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import lu_factor,lu_solve
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_linear_gravity_coupon1162';root=ET.parse(src/'scene.scn').getroot();node=root.find('Node');q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ');N=len(q0);free=np.ones(N,bool)
    for i in np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int):free[3*i:3*i+3]=False
    K0=np.zeros((N,N))
    for r in csv.DictReader((src/'rest.matrix.csv').open()):K0[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    K=K0[np.ix_(free,free)];n=len(K);mass=node.find('UniformMass');m=float(mass.get('totalMass'))/(N//3);M=m*np.eye(n);Cm=float(mass.get('rayleighMass'))*M;Ck=float(node.find('TetrahedronFEMForceField').get('rayleighStiffness'))*K;dt=float(root.get('dt'));f=np.tile(m*np.fromstring(root.get('gravity'),sep=' '),N//3)[free];lu=lu_factor(M+dt*(Cm+Ck)+dt*dt*K);rows=list(csv.DictReader((src/'states.csv').open()));no=BASE/'results/b3_linear_gravity_unobserved1164/states.csv';nr=list(csv.DictReader(no.open()));purity=max(float(abs(np.fromstring(r[k],sep=' ')-np.fromstring(s[k],sep=' ')).max()) for r,s in zip(rows,nr) for k in ('q','v'));assert len(rows)==len(nr)==40
    variants={}
    for name,extra in [('physical_velocity_damping',np.zeros_like(M)),('mass_A_only',Cm),('stiffness_A_only',Ck),('both_A_only',Cm+Ck)]:
        x=np.zeros(n);v=np.zeros(n);errors=[]
        for r in rows:
            v=lu_solve(lu,(M+dt*extra)@v+dt*(f-K@x));x+=dt*v;actual=(np.fromstring(r['q'],sep=' ')-q0)[free];av=np.fromstring(r['v'],sep=' ')[free]
            err=lambda u,w:float(np.linalg.norm(u-w)/max(np.linalg.norm(u),np.linalg.norm(w)))
            errors.append([err(actual,x),err(av,v)])
        variants[name]=dict(max_q_relative=max(x[0] for x in errors),max_v_relative=max(x[1] for x in errors),last_q_relative=errors[-1][0],last_v_relative=errors[-1][1])
    d=dict(status='READ_ONLY_DAMPING_CONTRACT_DISCRIMINATION',observer_q_v_max_error=purity,variants=variants,physical_validation='NOT QUALIFIED',time_convergence='FAIL_PRESERVED',energy_work=None,scope='Candidate discrete recurrences,not fitted coefficients,not a physics repair. Actual Native field-Rayleigh coefficients fixed.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'states.csv',src/'rest.matrix.csv',no,Path(__file__))});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))

if __name__=='__main__':main()
