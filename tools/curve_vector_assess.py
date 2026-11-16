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
    for name in ('UniformMass','ConstantForceField','LinearForceField','MechanicalObject','VectorPatchBenchmark'):
        node=scene.find(name)
        signature[name]=None if node is None else{k:v for k,v in node.attrib.items()if k not in ('filename','compressionEvery','snapshotTolerance','velocityDirectedTangent','normalizedRepresentation','outwardCertificates')}
    return signature


def numerical_signature(scene):
    signature={}
    for name in ('EulerImplicitSolver','NewmarkImplicitSolver','SparseLDLSolver'):
        node=scene.find(name);signature[name]=None if node is None else dict(node.attrib)
    signature['directed']=int(scene.find('VectorPatchBenchmark').attrib.get('velocityDirectedTangent','0'))
    return signature


def representation(scene):
    attrs=scene.find('VectorPatchBenchmark').attrib;period=int(attrs.get('compressionEvery','0'))
    return (period,float(attrs.get('snapshotTolerance','1e-9'))if period else None,int(attrs.get('normalizedRepresentation','0')),int(attrs.get('outwardCertificates','0')))


def compiled_sources(path):
    sources=json.loads((path/'compiled.json').read_text())['sources']
    return {k:v for k,v in sources.items()if k.startswith('models/')and(k.endswith(('.h','.cpp'))or k.endswith('CMakeLists.txt'))}


def applied_force(scene,time):
    constant=scene.find('ConstantForceField')
    if constant is not None:return np.array(list(map(float,constant.attrib['forces'].split())))
    field=scene.find('LinearForceField');times=np.array(list(map(float,field.attrib['times'].split())));forces=np.array(list(map(float,field.attrib['forces'].split()))).reshape(-1,3)
    if len(times)!=len(forces)or np.any(np.diff(times)<=0):raise ValueError('ordered force keys')
    return np.array([np.interp(time,times,forces[:,j],left=0.)for j in range(3)])


def newmark_audit(rows,scene,mass,external,h):
    ode=scene.find('NewmarkImplicitSolver').attrib
    if any(float(ode.get(k,v))!=float(v)for k,v in dict(gamma='.5',beta='.25',rayleighMass='0',rayleighStiffness='0').items()):
        return dict(status='NOT RUN',reason='derived identity requires beta1/4,gamma1/2,noRayleigh')
    vi=np.array([rows[0]['begin_v'+j]for j in 'xyz']);Ki=.5*mass*float(vi@vi)
    Ui=rows[0]['old_energy'];prior=Ui;maxF=0.;maxRaw=0.;maxKinematic=0.;maxKinetic=0.;maxTotal=0.
    cached_acceleration=(external+np.array([rows[0]['begin_f'+j]for j in 'xyz']))/mass
    sums=dict(external_work=0.,plastic=0.,signed_return_linearization_remainder=0.,paired_representation_change=0.,
              begin_inventory_quadrature_gap=0.,post_inventory_quadrature_gap=0.,cached_acceleration_work=0.)
    for row in rows:
        external=applied_force(scene,row['time']-h)
        x=np.array([row[j]for j in 'xyz']);x0=np.array([row['begin_'+j]for j in 'xyz'])
        v=np.array([row['v'+j]for j in 'xyz']);v0=np.array([row['begin_v'+j]for j in 'xyz'])
        f=np.array([row['begin_f'+j]for j in 'xyz']);J=np.array([row['begin_J'+str(j)]for j in range(9)]).reshape(3,3)
        dx=x-x0;dv=v-v0;midforce=f+.5*J@dx
        maxRaw=max(maxRaw,float(np.linalg.norm(mass*dv/h-external-midforce)/np.linalg.norm(external)))
        next_acceleration=2*dv/h-cached_acceleration
        # Actual SDK source computes a0 only at cpt==0,then retains a1.
        # Reconstruct from the independent velocity recurrence and CHECK the
        # matrix equation;do not fit this term from a total-energy residual.
        load_scale=float(np.linalg.norm(external))
        if not load_scale:raise ValueError('zero load requires independently defined absolute-force audit;no denominator floor')
        maxF=max(maxF,float(np.linalg.norm(mass*next_acceleration-external-f-J@dx)/load_scale))
        cache_work=.5*float((mass*cached_acceleration-external-f)@dx)
        maxKinematic=max(maxKinematic,float(np.linalg.norm(dx-.5*h*(v0+v))))
        work=float(external@dx);contact_work=float(midforce@dx);dk=.5*mass*float(v@v-v0@v0)
        maxKinetic=max(maxKinetic,abs(dk-work-contact_work-cache_work))
        post=row.get('stored_energy_post',row['energy']);paired=row.get('representation_delta_16',0.)
        begin_gap=row['old_energy']-prior;post_gap=post-row['energy']-paired;prior=post
        # Independently derived Newmark force work + endpoint return identity.
        # Signed term is NOT heat and is NOT inferred from the total residual.
        remainder=contact_work+row['endpoint_work']-row['endpoint_projection']
        sums['external_work']+=work;sums['plastic']+=row['loss'];sums['signed_return_linearization_remainder']+=remainder
        sums['paired_representation_change']+=paired;sums['begin_inventory_quadrature_gap']+=begin_gap;sums['post_inventory_quadrature_gap']+=post_gap
        sums['cached_acceleration_work']+=cache_work
        rhs=sums['external_work']-sums['plastic']+sums['signed_return_linearization_remainder']+sums['paired_representation_change']+sums['begin_inventory_quadrature_gap']+sums['post_inventory_quadrature_gap']+sums['cached_acceleration_work']
        total=.5*mass*float(v@v)-Ki+post-Ui;maxTotal=max(maxTotal,abs(total-rhs))
        cached_acceleration=next_acceleration
    source=ROOT/'.runtime/sofa-source/Sofa/Component/ODESolver/Backward/src/sofa/component/odesolver/backward/NewmarkImplicitSolver.cpp'
    return dict(status='EXPERIMENTAL',max_relative_dynamic_force_residual=maxF,force_1e3='PASS'if maxF<1e-3 else'FAIL',
                max_midpoint_position_identity=maxKinematic,max_kinetic_identity_residual=maxKinetic,
                max_sequential_energy_identity_residual=maxTotal,sums=sums,
                sdk_source_file_sha256=sha(source),raw_uncorrected_force_mismatch_relative=maxRaw,
                acceleration_scope='reconstructed from actual velocities,initial force and SDK recurrence;validated against linearized matrix equation,not direct private pID access',
                scope='fixed-patch beta1/4 gamma1/2 only;observed representation and quadrature inventories kept,not heat;not pressure-device/global gripper energy')


def analyze(tag):
    path,summary,scene,rows=case(tag)
    params=scene.find('VectorPatchBenchmark').attrib
    a,C,k=map(float,(params['halfLength'],params['capacity'],params['stiffness']))
    mass=float(scene.find('UniformMass').attrib['totalMass'])
    h=float(scene.attrib['dt'])
    external=applied_force(scene,rows[0]['time']-h)
    result=dict(case=str(path.relative_to(ROOT)),journal_sha256=sha(path/'dynamic/journal.csv'),
                actual_runtime_s=summary['stages']['dynamic']['runtime_s'],steps=len(rows),dt=h,
                final={key:rows[-1][key]for key in ('x','y','energy','cumulative_loss')},
                full_grasp='NOT RUN',global_gripper_energy='BLOCKED')
    dense=[]
    for n in (1024,4096,16384,65536):
        material=-1+2*(np.arange(n)+.5)/n
        cap=C*(1-material*material)
        plastic=np.zeros((n,2));D=0.;max_step_loss=0.;max_step_loss_absolute=0.;max_force=0.;max_force_absolute=0.;max_energy=0.
        for row in rows:
            trial=np.array([row['x'],row['y']])-plastic
            length=np.linalg.norm(trial,axis=1)
            ratio=np.ones(n);moving=length>0
            ratio[moving]=np.minimum(1,cap[moving]/(k*length[moving]))
            returned=trial*ratio[:,None]
            next_plastic=np.array([row['x'],row['y']])-returned
            loss=2*a/n*float(np.dot(cap,np.linalg.norm(next_plastic-plastic,axis=1)));D+=loss
            step_error=abs(loss-row['loss']);max_step_loss_absolute=max(max_step_loss_absolute,step_error)
            max_step_loss=max(max_step_loss,step_error/abs(loss)if loss else(0. if not row['loss']else math.inf))
            force=-2*a*k/n*np.sum(returned,axis=0);force_error=float(np.linalg.norm(force-np.array([row['fx'],row['fy']])))
            max_force_absolute=max(max_force_absolute,force_error);max_force=max(max_force,force_error/float(np.linalg.norm(force))if np.linalg.norm(force)else(0. if force_error==0 else math.inf))
            energy=a*k/n*float(np.sum(returned*returned));max_energy=max(max_energy,abs(energy-row['energy']))
            plastic=next_plastic
        exact=rows[-1]['cumulative_loss']
        dense.append(dict(points=n,loss=D,relative_to_function=abs(D-exact)/abs(exact)if exact else None,
            max_step_loss_relative=max_step_loss if math.isfinite(max_step_loss)else'INFINITE:zero dense reference/nonzero candidate',max_step_loss_absolute=max_step_loss_absolute,
            max_force_relative=max_force if math.isfinite(max_force)else'INFINITE:zero dense reference/nonzero candidate',max_force_absolute=max_force_absolute,max_energy_absolute=max_energy,
            scope='independent finite-grid replay of SAME measured trajectory;not an exact tiny-event reference or dynamic rerun'))
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
    if 'stored_energy_post'in rows[0]:
        result['representation_inventory']=dict(
            final_stored_energy=rows[-1]['stored_energy_post'],
            paired_transfer_sum=sum(r['representation_delta_16']for r in rows),
            max_paired_quadrature_difference=max(abs(r['representation_quadrature_difference'])for r in rows),
            max_inventory_difference=max(abs(r['post_inventory_difference'])for r in rows),
            max_cells=max(int(r['snapshot_cells'])for r in rows),
            scope='numeric representation+quadrature inventory,NOT heat or physical actuator work')
    if 'begin_J0'in rows[0]and scene.find('EulerImplicitSolver')is not None and not representation(scene)[0]and scene.find('ConstantForceField')is not None:
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
    elif 'begin_J0'in rows[0]and scene.find('NewmarkImplicitSolver')is not None:
        result['discrete_fixed_patch_audit']=newmark_audit(rows,scene,mass,external,h)
    elif 'begin_J0'in rows[0]:
        result['discrete_fixed_patch_audit']=dict(status='NOT RUN',reason='uncompressed Euler identity not applied to compressed-state Euler')
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
        if 'stored_energy_post'in shared:keys.append('stored_energy_post')
        comparison['endpoint_relative']={k:abs(lr[-1][k]-rr[-1][k])/abs(rr[-1][k])if rr[-1][k]else(None if lr[-1][k]else 0.)for k in keys}
        same_code=compiled_sources(lp)==compiled_sources(rp);same_solver=numerical_signature(ls)==numerical_signature(rs);same_rep=representation(ls)==representation(rs)
        comparison.update(same_compiled_sources=same_code,same_solver_settings=same_solver,same_history_settings=same_rep)
        time_contrast=same_code and same_solver and same_rep and ls.attrib['dt']!=rs.attrib['dt']
        comparison['contrast_type']='time convergence'if time_contrast else('history/implementation contrast'if not same_rep else'repetition or numerical-implementation contrast')
        if time_contrast:comparison['diagnostic_0p1percent']={k:'PASS'if v is not None and v<.001 else'FAIL'for k,v in comparison['endpoint_relative'].items()}
        elif not same_rep and same_solver and ls.attrib['dt']==rs.attrib['dt']:
            comparison['research_fidelity_1percent']={k:'PASS'if v is not None and v<.01 else'FAIL'for k,v in comparison['endpoint_relative'].items()}
        else:comparison['time_gate']='NOT APPLICABLE:do not pool different implementations or unchanged dt as a time test'
        comparisons.append(comparison)
    write_json(out/'assessment.json',dict(scope='independent mathematical reference and actual fixed-patch SDK audit,not3Dgrasp',
        assessor_sha256=sha(ROOT/'tools/curve_vector_assess.py'),cases=results,comparisons=comparisons))
    print(json.dumps(dict(out=str(out),comparisons=comparisons)))


if __name__=='__main__':main()
