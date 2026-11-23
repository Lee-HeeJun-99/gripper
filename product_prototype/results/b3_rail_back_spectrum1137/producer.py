"""Frozen mapped material-block spectrum,NOT Native assembled dynamics.
Input-derived point mass + public Guide mass. Omitted geometric/inertia tangent
terms prevent interpreting these eigenpairs as certified nonlinear modes.
"""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import eigh
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/b3_rail_back_hold1129';probe=BASE/'results/b3_rail_back_initial_probe1136';root=ET.parse(src/'scene.scn').getroot()
    snapshot=next(csv.DictReader((probe/'probe.state.csv').open()));q=np.fromstring(snapshot['q'],sep=' ').reshape(-1,3);nv=len(q)*3
    pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);nf=int(pairs[pairs[:,0]==0,1].max())+1
    guides=list(csv.DictReader((src/'guide_frames0.csv').open()));frame=np.fromstring(guides[0]['rigid_q'],sep=' ').reshape(-1,7);nm=len(frame);G=np.zeros((nv,3*nf+6*nm))
    def skew(v):return np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    for i,(owner,j) in enumerate(pairs):
        if owner==0:G[3*i:3*i+3,3*j:3*j+3]=np.eye(3)
        else:
            body=j//3;col=3*nf+6*body;G[3*i:3*i+3,col:col+3]=np.eye(3);G[3*i:3*i+3,col+3:col+6]=-skew(q[i]-frame[body,:3])
    fixed=np.fromstring(root.find("./Node[@name='free0']/FixedProjectiveConstraint").get('indices'),sep=' ',dtype=int);free=np.ones(G.shape[1],dtype=bool)
    for i in fixed:free[3*i:3*i+3]=False
    K=np.zeros((nv,nv))
    for r in csv.DictReader((probe/'probe.matrix.csv').open()):K[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    point_mass=float(root.find("./Node[@name='finger0']/UniformMass").get('totalMass'))/len(q)
    M=point_mass*(G.T@G);api=json.loads((src/'guide_frames0.csv.mass.json').read_text())['elements']
    for i,record in enumerate(api):M[3*nf+6*i:3*nf+6*i+6,3*nf+6*i:3*nf+6*i+6]+=np.array(record['matrix'])
    k=(G.T@K@G)[np.ix_(free,free)];m=M[np.ix_(free,free)];asym=float(np.linalg.norm(k-k.T)/np.linalg.norm(k));values,vectors=eigh((k+k.T)/2,m)
    omega=np.sqrt(np.maximum(values,0));frequency=omega/(2*np.pi)
    load=np.zeros(G.shape[1]);wrench=np.array(json.loads((BASE/'results/b3_reference_deadload1116/preflight.json').read_text())['reference_unit_tension_wrenches']);load[3*nf:]=wrench.ravel();modal_load=vectors.T@load[free];weights=modal_load**2
    with (out/'spectrum.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['mode','eigenvalue_s_minus2','frozen_frequency_Hz','unit_reference_load_projection_squared']);w.writerows(zip(range(len(values)),values,frequency,weights))
    vv=np.fromstring(snapshot['v'],sep=' ').reshape(-1,3);gv=np.fromstring(guides[0]['rigid_v'],sep=' ').reshape(-1,6);x=np.zeros(G.shape[1])
    for i,(owner,j) in enumerate(pairs):
        if owner==0:x[3*j:3*j+3]=vv[i]
    x[3*nf:]=gv.ravel();map_error=float(abs((G@x).reshape(-1,3)-vv).max())
    result=dict(status='FROZEN_INPUT_DERIVED_SPECTRUM_ONLY',source_commit=__import__('subprocess').check_output(['git','rev-parse','HEAD'],text=True).strip(),sample_time_s=float(snapshot['time_s']),free_dofs=int(free.sum()),input_derived_point_mass_kg=point_mass,point_mass_assembly_verified=False,Guide_mass_source='Native public element mass matrices',native_assembled_mass_tangent_verified=False,projected_material_K_antisymmetry_relative=asym,minimum_eigenvalue=float(values.min()),nonpositive_eigenvalues=int((values<=0).sum()),frequency_quantiles_Hz={str(p):float(np.quantile(frequency,p)) for p in (0,.25,.5,.75,1)},first_sample_velocity_mapping_error_m_s=map_error,resolution_diagnostics={str(dt):dict(modes_above_Nyquist=int((frequency>1/(2*dt)).sum()),reference_load_squared_fraction_above_Nyquist=float(weights[frequency>1/(2*dt)].sum()/weights.sum()),max_omega_dt=float((omega*dt).max())) for dt in (.0025,.00125)},physical_validation='NOT QUALIFIED',conclusion='Frozen high-frequency content is a hypothesis for resolution sensitivity,not actual dominant modes,not proof of unique cause or predicted grasp time. No dt/force/stiffness change prescribed.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'scene.scn',src/'guide_frames0.csv',src/'guide_frames0.csv.mass.json',probe/'probe.matrix.csv',probe/'probe.state.csv',Path(__file__))})
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

if __name__=='__main__':main()
