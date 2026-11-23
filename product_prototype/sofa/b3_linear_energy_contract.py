"""Model-derived linear energy ledger from actual Native q/v; NOT heat/NativePE.
Backward Euler identity separates declared viscous work from numerical loss.
Old global energy NULL and FAIL verdicts are never changed.
"""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records={};inputs=[Path(__file__)]
    for case,contract in [('b3_linear_gravity_coupon1162','field_A_only'),('b3_linear_gravity_ode1166','ODE_velocity_damping')]:
        src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();node=root.find('Node');q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ');N=len(q0);free=np.ones(N,bool)
        for i in np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int):free[3*i:3*i+3]=False
        K0=np.zeros((N,N))
        for r in csv.DictReader((src/'rest.matrix.csv').open()):K0[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
        K=K0[np.ix_(free,free)];m=float(node.find('UniformMass').get('totalMass'))/(N//3);C=m*np.eye(len(K))+1e-4*K;f=np.tile(m*np.fromstring(root.get('gravity'),sep=' '),N//3)[free];dt=float(root.get('dt'));x0=np.zeros(len(K));v0=x0.copy();work=viscous=numerical=algorithmic=0.;trace=[]
        for r in csv.DictReader((src/'states.csv').open()):
            x=(np.fromstring(r['q'],sep=' ')-q0)[free];v=np.fromstring(r['v'],sep=' ')[free];dx=x-x0;dv=v-v0;E=.5*m*(v@v)+.5*x@K@x;work+=dt*(f@v);viscous+=dt*(v@C@v);numerical+=.5*m*(dv@dv)+.5*dx@K@dx;algorithmic+=dt*(v@C@dv);selected=viscous if contract=='ODE_velocity_damping' else algorithmic;residual=E-work+selected+numerical;den=max(abs(E),abs(work),abs(selected),abs(numerical));trace.append(dict(time_s=float(r['time_s']),reference_stored_plus_kinetic_J=float(E),gravity_work_J=float(work),reference_velocity_damping_work_J=float(viscous),A_only_algorithmic_term_J=float(algorithmic),backward_Euler_numerical_loss_J=float(numerical),selected_contract_residual_J=float(residual),selected_contract_residual_relative=float(abs(residual)/den) if den else None));x0=x;v0=v
        records[case]=dict(contract=contract,final=trace[-1],maximum_residual_relative=max(r['selected_contract_residual_relative'] for r in trace));(out/(case+'.json')).write_text(json.dumps(trace,indent=2));inputs.extend([src/'scene.scn',src/'rest.matrix.csv',src/'states.csv'])
    d=dict(status='LINEAR_REFERENCE_ENERGY_ACCOUNTING_ONLY',records=records,physical_validation='NOT QUALIFIED',Native_potential_energy_API=None,global_B3_energy_work=None,scope='Quadratic reference energy using saved Native K/q/v,not measured material heat or actual full nonlinear Native energy. Field A-only term is signed algorithmic work,not viscous loss.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in inputs});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
