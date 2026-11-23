"""Small-shear tetra patch: Native corotation vs Native NeoHookean.
Equal initial E/nu;finite-strain laws differ. No hardware material selection.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded,add,flat

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    old=ET.parse(BASE/'results/b3_high_force_isolation1105/scene.scn').getroot()
    binary=next(Path(n.get('pluginName')) for n in old.iter('RequiredPlugin') if 'libReGripProductSequence.so' in n.get('pluginName',''))
    E=250e6;nu=.3;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));length=.01;mass=.001;dt=.001;force=.001
    q0=np.array([[0,0,0],[length,0,0],[0,length,0],[0,0,length]])
    records=[]
    for material in ('corotational','NeoHookean'):
        d=out/material;d.mkdir();root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
        for n in ('AnimationLoop','Constraint.Projective','LinearSolver.Direct','Mass','MechanicalLoad','ODESolver.Backward','StateContainer','Topology.Container.Constant','SolidMechanics.FEM.Elastic','SolidMechanics.FEM.HyperElastic'):
            add(root,'RequiredPlugin',pluginName='Sofa.Component.'+n)
        add(root,'RequiredPlugin',pluginName=str(binary));add(root,'DefaultAnimationLoop');add(root,'EulerImplicitSolver',rayleighMass=0,rayleighStiffness=0);add(root,'SparseLDLSolver',template='CompressedRowSparseMatrixd')
        node=add(root,'Node',name='patch');add(node,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q0));add(node,'MeshTopology',tetrahedra='0 1 2 3',position=flat(q0))
        add(node,'UniformMass',totalMass=mass);add(node,'FixedProjectiveConstraint',indices='0 1 2')
        if material=='corotational':add(node,'TetrahedronFEMForceField',name='elastic',method='large',youngModulus=E,poissonRatio=nu,rayleighStiffness=0)
        else:add(node,'TetrahedronHyperelasticityFEMForceField',name='elastic',materialName='NeoHookean',ParameterSet=f'{mu:.17g} {lam:.17g}',rayleighStiffness=0)
        add(node,'ConstantForceField',indices='3',forces=f'{force} 0 0');add(node,'NativePointJournal',body='@dofs',filename=str(d/'states.csv'))
        ET.ElementTree(root).write(d/'scene.scn');cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',str(d/'scene.scn')]
        proc=guarded(cmd,d/'process',60);logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'));rec=dict(material=material,process=proc,status='FAIL_EXECUTION',command=cmd)
        if proc['exit_code']==0 and '[ERROR]' not in logs:
            rows=list(csv.DictReader((d/'states.csv').open()));expected=[];u=0.;v=0.;K=mu*length/6;m=mass/4
            for i in range(4):v=(m*v+dt*force-dt*K*u)/(m+dt*dt*K);u+=dt*v;expected.append([u,v])
            actual=np.array([[np.fromstring(r['q'],sep=' ').reshape(-1,3)[3,0],np.fromstring(r['v'],sep=' ').reshape(-1,3)[3,0]] for r in rows]);expected=np.array(expected)
            errors=np.max(abs(actual-expected)/abs(expected),axis=0) if len(rows)==4 else [float('inf')]*2
            rec.update(status='PASS_SMALL_SHEAR_PATCH_ONLY' if len(rows)==4 and max(errors)<=.001 else 'FAIL_SMALL_SHEAR_PATCH',outputs=len(rows),all_output_displacement_relative_error=float(errors[0]),all_output_velocity_relative_error=float(errors[1]),tip_shear_displacement_m=actual[-1,0],linear_reference=expected.tolist())
        records.append(rec)
    result=dict(status='PASS_SMALL_SHEAR_COMPARISON_ONLY' if all(r['status']=='PASS_SMALL_SHEAR_PATCH_ONLY' for r in records) else 'FAIL_PATCH_COMPARISON',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),binary_sha256=sha(binary),SDK='/home/ubuntu/SOFA/v26.06.00',records=records,E_Pa=E,nu=nu,NeoHookean_parameters_mu_lambda_Pa=[mu,lam],force_N=force,mass_kg=mass,dt_s=dt,relative_gate=.001,estimated_runtime_s=1,child_limit_s=60,memory_GiB=4,physical_validation='NOT QUALIFIED',scope='Native component/parameter-order check against independent linear backward Euler patch;not finite-strain or B3 qualification')
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

if __name__=='__main__':main()
