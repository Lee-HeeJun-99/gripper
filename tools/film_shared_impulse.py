"""Actual mapped-film/free-Rigid3 shared ZERO-TIME impulse API reference."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    source=out/'sources/models/rigid_impact_reference';shutil.copytree(ROOT/'models/rigid_impact_reference',source)
    for directory in ('film_impact','film_native_contact','film_rail_tendon','film_shell','film_sphere_contact'):
        target=out/'sources/models'/directory;target.mkdir()
        for f in (ROOT/'models'/directory).glob('*.h'):shutil.copy2(f,target/f.name)
    build=ROOT/'build'/('shared_impulse_'+a.tag);build.mkdir(exist_ok=False);stages={}
    stages['configure']=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
    stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if stages['configure']['exit_code']==0 else dict(exit_code=-1)
    identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sdk=str(SDK),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},scope='actual two-state shared instantaneous point impulse;NO joint dynamics/CCD/grasp')
    result=dict(status='FAIL',scope=identity['scope'],stages=stages,cases={})
    if stages['build']['exit_code']==0:
        binary=build/'libReGripRigidImpactReference.so';identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
        if 'not found' in deps or any('libSofa.' in l and '=> /' in l and str(SDK) not in l for l in deps.splitlines()):raise ValueError('shared impulse SDK ABI mismatch')
        origin=ROOT/'results/autonomous_film_20261117_c2_bounded_short401';origin_identity=json.loads((origin/'identity.json').read_text())
        for name,node,root_node,object_mass in [('tip_light',102,102,5e-8),('tip_heavy',102,102,.0001),('quarter_light',7,12,5e-8)]:
            case=out/name;case.mkdir();tree=ET.parse(origin/'1/scene.scn');scene=tree.getroot();scene.set('dt','.001')
            remove={'NewtonRaphsonSolver','ReGripBDFSolver','ReGripMatrixLinearSystem','EigenSparseLU','FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','LinearSolverConstraintCorrection','CollisionPipeline','BruteForceBroadPhase','BVHNarrowPhase','MinProximityIntersection','CollisionResponse','FilmNativeCoupledCorrection','FilmNativeObserver'}
            for e in list(scene):
                if e.tag in remove or (e.tag=='Node' and e.get('name')=='fixed') or (e.tag=='RequiredPlugin' and 'libReGripFilmNativeObserver.so' in e.get('pluginName','')):scene.remove(e)
            for parent in scene.iter():
                for child in list(parent):
                    if child.tag.endswith('CollisionModel'):parent.remove(child)
            for plugin in scene.findall('RequiredPlugin'):
                path=ROOT.__class__(plugin.get('pluginName',''));key={'libReGripFilmShell.so':'core_sha256','libReGripFilmRailTendon.so':'assembly_sha256'}.get(path.name)
                if key and sha(path)!=origin_identity[key]:raise ValueError('original film binary drift')
            field=scene.find("Node[@name='assembly']/FilmRailTendon");field.set('maximumTension','0');field.set('filename',str(case/'film.csv'));field.set('displacementFilename',str(case/'displacement.csv'))
            velocity=np.zeros(231*3);velocity[3*root_node+2]=-3;scene.find("MechanicalObject[@name='dofs']").set('velocity',' '.join(map(str,velocity)))
            x=(node//5)*5;y=(node%5)*6;obj=ET.SubElement(scene,'Node',name='object')
            ET.SubElement(obj,'MechanicalObject',name='body',template='Rigid3d',position=f'{x-1} {y-1} 1 0 0 0 1',velocity='0 0 0 0 0 0');ET.SubElement(obj,'UniformMass',template='Rigid3d',vertexMass=f'{object_mass} 1 1 0 0 0 1 0 0 0 1')
            ET.SubElement(scene,'RequiredPlugin',pluginName=str(binary));ET.SubElement(scene,'FilmRigidSharedImpulse',root='@dofs',body='@object/body',field='@assembly/filmField',node=str(node),normal='0 0 1',bodyArm='1 1 -1',filename=str(case/'shared.csv'));ET.SubElement(scene,'DefaultAnimationLoop');tree.write(case/'scene.scn')
            process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',case/'scene.scn'],case/'process',60);record=dict(status='FAIL',process=process)
            log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
            if process['exit_code']==0 and '[ERROR]' not in log:
                row=list(csv.DictReader((case/'shared.csv').open()))[0];M=np.loadtxt(case/'shared.csv.matrix.csv',delimiter=',');J=np.loadtxt(case/'shared.csv.jacobian.csv',delimiter=',');states=list(csv.DictReader((case/'shared.csv.states.csv').open()));before=np.array(list(map(float,states[0]['reduced_velocity'].split())));after=np.array(list(map(float,states[1]['reduced_velocity'].split())))
                diagonal=np.diag(M);inverse=J/diagonal if np.array_equal(M,np.diag(diagonal)) else np.linalg.solve(M,J);expected_p=-float(J@before)/float(J@inverse);expected=before+inverse*expected_p
                error=float(np.max(np.abs(after-expected)));momentum=max(float(row[k]) for k in ('momentum_residual','linear_balance_with_root','angular_balance_with_root'));good=error<=1e-11 and momentum<=1e-12 and float(row['post_normal'])>=-1e-12 and float(row['impact_loss'])>=0 and abs(float(row['body_wx']))+abs(float(row['body_wy']))>0
                if node==7:good &= float(row['root_impulse_norm'])>0
                record.update(status='PASS' if good else 'FAIL',actual=row,independent_velocity_error=error,independent_impulse_error=abs(float(row['impulse'])-expected_p),scope='actual film and free body share one impulse at supplied time0;NOT subsequent dynamics')
            result['cases'][name]=record
        result['status']='PASS' if all(c['status']=='PASS' for c in result['cases'].values()) else 'FAIL'
    write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],cases={k:v['status'] for k,v in result['cases'].items()})))
if __name__=='__main__':main()
