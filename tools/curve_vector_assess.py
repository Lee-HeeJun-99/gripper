"""Read-only assessment of actual fixed-patch SDK journals; fresh output only."""
import argparse
import csv
import json
import math
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json


def case(tag):
    if not tag.replace('_','').isalnum():raise ValueError('simple case tag')
    path=ROOT/'results'/('vector_history_sdk_'+tag)
    summary=json.loads((path/'summary.json').read_text())
    if summary['status']!='PASS':raise ValueError('actual benchmark failed: '+tag)
    scene=ET.parse(path/'dynamic/scene.scn').getroot()
    with (path/'dynamic/journal.csv').open()as stream:rows=[{k:float(v)for k,v in row.items()}for row in csv.DictReader(stream)]
    return path,summary,scene,rows


def closed_loss(a,C,k,d):
    ratio=k*d/C
    if ratio>=1:return d*4*a*C/3-16*a*C*C/(15*k)
    y=ratio/(1+math.sqrt(1-ratio))
    first=y*y-y*y*y/3
    second=4*y*y*y/3-y**4+y**5/5
    return 2*a*(C*d*first-C*C*second/k)


def physical_signature(scene):
    signature=dict(gravity=scene.attrib['gravity'])
    for name in ('UniformMass','ConstantForceField','MechanicalObject','EulerImplicitSolver','NewmarkImplicitSolver','SparseLDLSolver','VectorPatchBenchmark'):
        node=scene.find(name)
        signature[name]=None if node is None else{k:v for k,v in node.attrib.items()if k!='filename'}
    return signature


def analyze(tag):
    path,summary,scene,rows=case(tag)
    params=scene.find('VectorPatchBenchmark').attrib
    a,C,k=map(float,(params['halfLength'],params['capacity'],params['stiffness']))
    mass=float(scene.find('UniformMass').attrib['totalMass'])
    external=np.array(list(map(float,scene.find('ConstantForceField').attrib['forces'].split())))
    h=float(scene.attrib['dt'])
    result=dict(case=str(path.relative_to(ROOT)),journal_sha256=sha(path/'dynamic/journal.csv'),
                actual_runtime_s=summary['stages']['dynamic']['runtime_s'],steps=len(rows),dt=h,
                final={key:rows[-1][key]for key in ('x','y','energy','cumulative_loss')},
                full_grasp='NOT RUN',global_gripper_energy='BLOCKED')
    dense=[]
    for n in (1024,4096,16384,65536):
        material=-1+2*(np.arange(n)+.5)/n
        cap=C*(1-material*material)
        plastic=np.zeros((n,2));D=0.
        for row in rows:
            trial=np.array([row['x'],row['y']])-plastic
            length=np.linalg.norm(trial,axis=1)
            ratio=np.ones(n);moving=length>0
            ratio[moving]=np.minimum(1,cap[moving]/(k*length[moving]))
            returned=trial*ratio[:,None]
            next_plastic=np.array([row['x'],row['y']])-returned
            D+=2*a/n*float(np.dot(cap,np.linalg.norm(next_plastic-plastic,axis=1)))
            plastic=next_plastic
        exact=rows[-1]['cumulative_loss']
        dense.append(dict(points=n,loss=D,relative_to_function=abs(D-exact)/abs(exact)if exact else None))
    result['independent_dense_plastic_vectors']=dense
    if all(abs(r['x']-2*r['y'])<=1e-15*max(abs(r['x']),1e-300)for r in rows)and all(
        rows[i]['x']>=rows[i-1]['x']for i in range(1,len(rows))):
        errors=[];previous=0.
        for row in rows:
            analytic=closed_loss(a,C,k,math.hypot(row['x'],row['y']))
            increment=analytic-previous;previous=analytic
            errors.append(abs(row['loss']-increment)/abs(increment)if increment else (0. if row['loss']==0 else math.inf))
        result['independent_monotone_closed_reference']=dict(max_step_loss_relative=max(errors),
            cumulative_loss=previous,final_relative=abs(rows[-1]['cumulative_loss']-previous)/abs(previous),
            per_step_1percent='PASS'if max(errors)<.01 else'FAIL')
    if 'begin_J0'in rows[0]and scene.find('EulerImplicitSolver')is not None:
        maxForce=0.;kineticResidual=0.;localEnergy=0.;sequenceResidual=0.;inventoryGap=0.
        sums=dict(external_work=0.,mapped_contact_work=0.,material_endpoint_work=0.,plastic=0.,
                  endpoint_projection=0.,velocity_projection=0.,signed_contact_linearization_remainder=0.)
        initialV=np.array([rows[0]['begin_v'+j]for j in 'xyz']);initialK=.5*mass*float(initialV@initialV)
        initialU=rows[0]['old_energy'];priorU=initialU
        for row in rows:
            x=np.array([row[j]for j in 'xyz']);x0=np.array([row['begin_'+j]for j in 'xyz'])
            v=np.array([row['v'+j]for j in 'xyz']);v0=np.array([row['begin_v'+j]for j in 'xyz'])
            f=np.array([row['begin_f'+j]for j in 'xyz']);J=np.array([row['begin_J'+str(j)]for j in range(9)]).reshape(3,3)
            dx=x-x0;dv=v-v0;linear=f+J@dx
            force=mass*dv/h-external-linear
            maxForce=max(maxForce,float(np.linalg.norm(force)/np.linalg.norm(external)))
            dk=.5*mass*float(v@v-v0@v0);projection=.5*mass*float(dv@dv)
            Wext=float(external@dx);Wcontact=float(linear@dx)
            kineticResidual=max(kineticResidual,abs(dk-Wext-Wcontact+projection))
            localEnergy=max(localEnergy,abs(row['energy_residual']))
            inventoryGap=max(inventoryGap,abs(row['old_energy']-priorU));priorU=row['energy']
            sums['external_work']+=Wext;sums['mapped_contact_work']+=Wcontact
            sums['material_endpoint_work']+=row['endpoint_work'];sums['plastic']+=row['loss']
            sums['endpoint_projection']+=row['endpoint_projection'];sums['velocity_projection']+=projection
            # Derived independently from the actual linearized force and the
            # endpoint material return,NOT fitted from a total-energy defect.
            sums['signed_contact_linearization_remainder']+=Wcontact+row['endpoint_work']
            total=.5*mass*float(v@v)-initialK+row['energy']-initialU
            rhs=sums['external_work']+sums['signed_contact_linearization_remainder']-sums['plastic']-sums['endpoint_projection']-sums['velocity_projection']
            sequenceResidual=max(sequenceResidual,abs(total-rhs))
        result['discrete_fixed_patch_audit']=dict(max_relative_force_residual=maxForce,
            force_1e3='PASS'if maxForce<1e-3 else'FAIL',max_kinetic_identity_residual=kineticResidual,
            max_local_material_identity_residual=localEnergy,max_pre_post_inventory_quadrature_gap=inventoryGap,
            max_sequential_energy_identity_residual=sequenceResidual,sums=sums,
            scope='constant capacity/noRayleigh/fixed-normal benchmark ONLY. Signed linearization remainder is not heat;inventory quadrature gaps retained.')
    elif 'begin_J0'in rows[0]:
        result['discrete_fixed_patch_audit']=dict(status='NOT RUN',reason='Euler discrete identity is not applied to a different Newmark integrator')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('cases',nargs='+');args=p.parse_args()
    if not args.tag.replace('_','').isalnum():raise ValueError('simple output tag')
    out=ROOT/'results'/('vector_history_assessment_'+args.tag);out.mkdir(exist_ok=False)
    results=[analyze(t)for t in args.cases]
    comparisons=[]
    for left,right in zip(args.cases,args.cases[1:]):
        lp,_,ls,lr=case(left);rp,_,rs,rr=case(right)
        if abs(lr[-1]['time']-rr[-1]['time'])>1e-12:continue
        shared=set(lr[0])&set(rr[0]);comparison=dict(left=left,right=right)
        if physical_signature(ls)!=physical_signature(rs):
            comparisons.append(dict(left=left,right=right,status='NOT APPLICABLE',reason='different actual physical/initial/solver conditions'));continue
        if len(lr)==len(rr):comparison['max_common_journal_difference']=max(abs(a[k]-b[k])for a,b in zip(lr,rr)for k in shared)
        keys=['x','y','cumulative_loss','energy']
        comparison['endpoint_relative']={k:abs(lr[-1][k]-rr[-1][k])/abs(rr[-1][k])if rr[-1][k]else(None if lr[-1][k]else 0.)for k in keys}
        comparison['contrast_type']='repetition/query-equivalence'if ls.attrib['dt']==rs.attrib['dt']else'time convergence'
        comparison['diagnostic_0p1percent']={k:'PASS'if v is not None and v<.001 else'FAIL'for k,v in comparison['endpoint_relative'].items()}
        comparisons.append(comparison)
    write_json(out/'assessment.json',dict(scope='independent mathematical reference and actual fixed-patch SDK audit,not3Dgrasp',
        assessor_sha256=sha(ROOT/'tools/curve_vector_assess.py'),cases=results,comparisons=comparisons))
    print(json.dumps(dict(out=str(out),comparisons=comparisons)))


if __name__=='__main__':main()
