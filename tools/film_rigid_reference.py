"""Actual free Rigid3 supplied-point impulse/flight API;NOT film/object grasp."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
SDK=ROOT.__class__('/home/ubuntu/SOFA/v26.06.00')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    source=out/'sources/models/rigid_impact_reference';shutil.copytree(ROOT/'models/rigid_impact_reference',source)
    for name in ('film_impact','film_native_contact','film_rail_tendon','film_shell','film_sphere_contact'):
        target=out/'sources/models'/name;target.mkdir()
        for f in (ROOT/'models'/name).glob('*.h'):shutil.copy2(f,target/f.name)
    build=ROOT/'build'/('rigid_impact_'+a.tag);build.mkdir(exist_ok=False)
    stages={};stages['configure']=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
    stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'compile',120) if stages['configure']['exit_code']==0 else dict(exit_code=-1)
    identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sdk=str(SDK),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},physical_assumption='one supplied body-fixed contact point;isotropic inertia,force-free exact postflight;NOT whole collider/CCD/sustained contact')
    result=dict(status='FAIL',scope='limited actual free Rigid3 point-impact/flight reference;NOT film coupling/grasp',stages=stages,cases={});write_json(out/'identity.json',identity)
    if stages['build']['exit_code']==0:
        binary=build/'libReGripRigidImpactReference.so';identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
        if 'not found' in deps or any('libSofa.' in l and '=> /' in l and str(SDK) not in l for l in deps.splitlines()):raise ValueError('rigid reference SDK ABI mismatch')
        for name,dt,e,angle,anisotropic in [('plastic',.001,0.,0.,False),('plastic_half',.0005,0.,0.,False),('plastic_quarter',.00025,0.,0.,False),('restitution',.001,.5,0.,False),('rotated',.001,0.,.6,False),('anisotropy_guard',.001,0.,0.,True)]:
            case=out/name;case.mkdir();c,s=math.cos(angle),math.sin(angle);R=np.array([[c,-s,0],[s,c,0],[0,0,1.]])
            shift=np.array([2.,-3.,4.]) if angle else np.zeros(3);center=R@np.array([1.,0,0])+shift;normal=R@np.array([1.,0,0]);linear=R@np.array([-1.,.3,.4]);omega=R@np.array([0.,.2,-.1]);arm=R@np.array([-1.,1.,0]);quaternion=np.array([0.,0.,math.sin(angle/2),math.cos(angle/2)])
            fmt=lambda x:' '.join(format(float(v),'.17g') for v in x)
            scene=ET.Element('Node',name='actual_free_rigid_reference',dt=str(dt),gravity='0 0 0')
            ET.SubElement(scene,'RequiredPlugin',pluginName='Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass')
            ET.SubElement(scene,'RequiredPlugin',pluginName=str(binary));ET.SubElement(scene,'DefaultAnimationLoop')
            ET.SubElement(scene,'MechanicalObject',name='body',template='Rigid3d',position=fmt(np.r_[center,quaternion]),velocity=fmt(np.r_[linear,omega]))
            ET.SubElement(scene,'UniformMass',template='Rigid3d',vertexMass='2 1 1 0 0 0 '+('2' if anisotropic else '1')+' 0 0 0 '+('3' if anisotropic else '1'))
            ET.SubElement(scene,'RigidSuppliedPlaneFlight',name='ode',body='@body',planeNormal=fmt(normal),planeOffset=str(float(normal@shift)),restitution=str(e),contactArm='-1 1 0',filename=str(case/'state.csv'))
            ET.ElementTree(scene).write(case/'scene.scn');process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',case/'scene.scn'],case/'process',30);record=dict(status='FAIL',process=process)
            log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
            if anisotropic:
                record.update(status='PASS' if process['exit_code']!=0 and 'requires isotropic actual inertia' in log else 'FAIL',scope='expected unsupported-inertia rejection,NOT anisotropic dynamics PASS')
            elif process['exit_code']==0 and '[ERROR]' not in log:
                row=list(csv.DictReader((case/'state.csv').open()))[0];M=np.loadtxt(case/'state.csv.mass.csv',delimiter=',');v0=np.r_[linear,omega];J=np.r_[normal,np.cross(arm,normal)];inverse=np.linalg.solve(M,J);p_expected=-(1+e)*float(J@v0)/float(J@inverse);v_expected=v0+inverse*p_expected;v_actual=np.array(list(map(float,row['final_velocity'].split())));center_expected=center+dt*v_expected[:3];center_actual=np.array(list(map(float,row['final_center'].split())))
                w=v_expected[3:];speed=np.linalg.norm(w);delta=np.r_[w*(math.sin(dt*speed/2)/speed),math.cos(dt*speed/2)] if speed else np.array([0,0,0,1.]);qv=delta[3]*quaternion[:3]+quaternion[3]*delta[:3]+np.cross(delta[:3],quaternion[:3]);qw=delta[3]*quaternion[3]-delta[:3]@quaternion[:3];q_expected=np.r_[qv,qw];q_actual=np.array(list(map(float,row['final_quaternion'].split())))
                errors=dict(velocity=float(np.max(np.abs(v_actual-v_expected))),center=float(np.max(np.abs(center_actual-center_expected))),quaternion=float(min(np.linalg.norm(q_actual-q_expected),np.linalg.norm(q_actual+q_expected))),impulse=abs(float(row['impulse'])-p_expected))
                good=all(value<=1e-11 for value in errors.values()) and float(row['momentum_residual'])<=1e-11 and float(row['angular_impulse_residual'])<=1e-11 and float(row['end_gap'])>=-1e-10 and float(row['impact_loss'])>=0
                record.update(status='PASS' if good else 'FAIL',reference_errors=errors,actual=row,actual_mass=M.tolist(),scope='actual unconstrained Rigid3;supplied point event plus isolated isotropic freeflight;NOT general collision/grasp')
            result['cases'][name]=record
        result['status']='PASS' if all(c['status']=='PASS' for c in result['cases'].values()) else 'FAIL'
    write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],cases={k:v['status'] for k,v in result['cases'].items()})))
if __name__=='__main__':main()
