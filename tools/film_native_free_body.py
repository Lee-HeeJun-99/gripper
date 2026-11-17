"""Separate actual Native mixed Film/Rigid3 dynamics CONTROL,not event-owner certification."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mixed-be',action='store_true');p.add_argument('--generic-correction',action='store_true');p.add_argument('--reuse');p.add_argument('--c2-closing',action='store_true');p.add_argument('--steps',type=int,default=40);p.add_argument('--duration',type=float,default=.1);p.add_argument('--profile');a=p.parse_args()
    if a.c2_closing and (not a.mixed_be or not a.generic_correction or not 1<=a.steps<=1024 or not 0<a.duration<=1):raise ValueError('C2 control requires guarded mixed BE/GenericCorrection,<=1s/1024steps')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    source=out/'sources/models/rigid_impact_reference';shutil.copytree(ROOT/'models/rigid_impact_reference',source)
    for directory in ('film_impact','film_native_contact','film_rail_tendon','film_shell','film_sphere_contact'):
        target=out/'sources/models'/directory;target.mkdir()
        for f in (ROOT/'models'/directory).glob('*.h'):shutil.copy2(f,target/f.name)
    build=ROOT/'build'/('native_rigid_'+a.tag);stages={}
    if a.reuse:stages['build']=dict(exit_code=0,reused=a.reuse,source_and_binary_guard='checked below before launch')
    else:
        build.mkdir(exist_ok=False)
        stages['configure']=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
        stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if stages['configure']['exit_code']==0 else dict(exit_code=-1)
    identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sdk=str(SDK),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},contact_model='Native FrictionContactConstraint mu0,BE;NOT custom whole-surface plastic event/CandidateClosure',material_status='research-only values;not measured object/material/actuator',object_mass=.0001,object_radius=8.,object_inertia_per_mass=25.6,gravity=[0,0,0],rayleigh_mass=2.,initial_film_tip_velocity=-3.,initial_body_omega=[.1,.2,.3],actuation='zero tension;NOT actual C2 grasp')
    identity['actual_solver']='ReGripRigidBE' if a.mixed_be else 'preserved ReGripBDFSolver order1'
    result=dict(status='FAIL',scope='actual Native mixed-state dynamics control;NOT custom event-owner/free grasp qualification',stages=stages,cases={})
    identity['generic_correction']=a.generic_correction
    if stages['build']['exit_code']==0:
        binary=build/'libReGripRigidImpactReference.so'
        if a.reuse:
            prior=ROOT/'results'/('autonomous_film_'+a.reuse);oldmeta=json.loads((prior/'identity.json').read_text());original_binary=ROOT/'build'/('native_rigid_'+a.reuse)/'libReGripRigidImpactReference.so'
            compiled=lambda data:{k:v for k,v in data.items() if k.endswith(('.cpp','.h','/CMakeLists.txt'))}
            if compiled(oldmeta['source_hashes'])!=compiled(identity['source_hashes']) or sha(original_binary)!=oldmeta['binary_sha256']:raise ValueError('Native probe/solver compiled source or binary drift')
            identity['reuse_guard']='all archived .cpp/.h/CMakeLists.txt and binary exact;README tracked but not compiled'
            binary=original_binary
        identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
        if 'not found' in deps or any('libSofa.' in l and '=> /' in l and str(SDK) not in l for l in deps.splitlines()):raise ValueError('Native free-body SDK ABI mismatch')
        origin=ROOT/'results/autonomous_film_20261117_c2_bounded_short401';old=json.loads((origin/'identity.json').read_text())
        duration=a.duration if a.c2_closing else .002;limit=60
        if a.c2_closing and (duration>.1 or a.steps>64):
            if not a.profile:raise ValueError('longer C2 run requires measured same-binary profile')
            prior=ROOT/'results'/('autonomous_film_'+a.profile);meta=json.loads((prior/'identity.json').read_text());summary=json.loads((prior/'summary.json').read_text());samples=list(summary['cases'].values())
            if meta['binary_sha256']!=identity['binary_sha256'] or summary['status']!='EXPERIMENTAL' or not meta.get('c2_closing'):raise ValueError('invalid C2 same-binary cost profile')
            estimate=2*max(s['process']['runtime_s']/int(k) for k,s in summary['cases'].items())*a.steps
            if estimate>480:raise ValueError('profiled C2 cost exceeds480s;shorten/improve first')
            identity['runtime_prediction_s']=estimate;limit=480
        identity.update(c2_closing=a.c2_closing,duration=duration)
        if a.c2_closing:identity.update(initial_film_tip_velocity=0.,initial_body_omega=[0,0,0],actuation='original C2 maximum .001 per rail;ramp4/release6..8',object_initial_position=[75,12,-8.2])
        for steps in ((a.steps,) if a.c2_closing else (8,16,32)):
            case=out/str(steps);case.mkdir();tree=ET.parse(origin/'1/scene.scn');scene=tree.getroot();scene.set('dt',str(duration/steps))
            for element in scene.iter():
                for key,value in list(element.attrib.items()):
                    if str(origin/'1') in value:element.set(key,value.replace(str(origin/'1'),str(case)))
            for element in list(scene):
                if element.tag in ('FilmNativeCoupledCorrection','FilmNativeObserver') or (element.tag=='Node' and element.get('name')=='fixed') or (element.tag=='RequiredPlugin' and 'libReGripFilmNativeObserver.so' in element.get('pluginName','')):scene.remove(element)
            for plugin in scene.findall('RequiredPlugin'):
                path=ROOT.__class__(plugin.get('pluginName',''));key={'libReGripFilmShell.so':'core_sha256','libReGripFilmRailTendon.so':'assembly_sha256'}.get(path.name)
                if key:
                    if sha(path)!=old[key]:raise ValueError('qualified film/core binary drift')
                    identity[path.name]=dict(path=str(path),sha256=old[key])
            ode=scene.find('ReGripBDFSolver');ode.set('nativeCoupledPredictor','0');ode.set('nativeConstraintBE','1');ode.set('order','1')
            if a.generic_correction:
                correction=scene.find('LinearSolverConstraintCorrection');correction.tag='GenericConstraintCorrection';correction.set('complianceFactor','1');correction.set('regularizationTerm','0')
            if a.mixed_be:
                scene.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ode.tag='ReGripRigidBE'
            velocity=np.zeros(231*3);velocity[3*102+2]=0 if a.c2_closing else -3;scene.find("MechanicalObject[@name='dofs']").set('velocity',' '.join(map(str,velocity)))
            field=scene.find("Node[@name='assembly']/FilmRailTendon");field.set('maximumTension','0');field.set('filename',str(case/'film.csv'));field.set('displacementFilename',str(case/'displacement.csv'))
            if a.c2_closing:field.set('maximumTension','.001')
            ET.SubElement(scene,'RequiredPlugin',pluginName='Sofa.Component.Mapping.NonLinear');obj=ET.SubElement(scene,'Node',name='free_object');ET.SubElement(obj,'MechanicalObject',name='body',template='Rigid3d',position='100 12 -8.011 0 0 0 1',velocity='0 0 0 .1 .2 .3');ET.SubElement(obj,'UniformMass',template='Rigid3d',vertexMass='.0001 1 25.6 0 0 0 25.6 0 0 0 25.6')
            collision=ET.SubElement(obj,'Node',name='collision');ET.SubElement(collision,'MechanicalObject',name='center',template='Vec3d',position='0 0 0');ET.SubElement(collision,'RigidMapping',template='Rigid3d,Vec3d',input='@../body',output='@center',globalToLocalCoords='0',mapMasses='0');ET.SubElement(collision,'SphereCollisionModel',radius='8',group='2',simulated='1',moving='1')
            if a.c2_closing:obj.find('MechanicalObject').set('position','75 12 -8.2 0 0 0 1');obj.find('MechanicalObject').set('velocity','0 0 0 0 0 0')
            ET.SubElement(scene,'RequiredPlugin',pluginName=str(binary));ET.SubElement(scene,'NativeFreeBodyProbe',body='@free_object/body',surface='@assembly/actual/world',sphere='@free_object/collision/center',radius='8.01',maxSteps=str(steps),filename=str(case/'body.csv'));tree.write(case/'scene.scn')
            process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',case/'scene.scn'],case/'process',limit);record=dict(status='FAIL',process=process)
            log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
            if process['exit_code']==0 and '[ERROR]' not in log:
                rows=list(csv.DictReader((case/'body.csv').open()));finite=len(rows)==steps and all(value=='null' or math.isfinite(float(value)) for row in rows for value in row.values());complete=finite and abs(float(rows[-1]['time'])-duration)<1e-12
                if complete:
                    movement=max(abs(float(r['z'])+(8.2 if a.c2_closing else 8.011)) for r in rows);minimum=min(float(r['minimum_buffer_gap']) for r in rows);position=max(float(r['BE_position_residual']) for r in rows);mapped=max(float(r['mapped_center_error']) for r in rows);observed=all(r['impulse_balance_residual']!='null' and int(r['unmatched_rows'])==0 for r in rows);balance=max(float(r['impulse_balance_residual']) for r in rows) if observed else None
                    for key in ('contact_action_reaction_residual','contact_moment_begin_residual','contact_moment_end_residual'):
                        record['maximum_'+key]=max(float(r[key]) for r in rows) if observed else None
                    record.update(execution_status='PASS',status='EXPERIMENTAL' if minimum>=-1e-10 and position<=1e-10 and mapped<=1e-12 and observed and balance<=1e-12 else 'FAIL',object_motion_observed=movement>0,maximum_body_displacement_z=movement,minimum_buffer_gap=minimum,maximum_BE_position_residual=position,mapped_center_error=mapped,actual_native_impulse_observed=observed,maximum_native_impulse_balance_residual=balance,physical_qualification='NOT QUALIFIED:separate Native law;whole-surface event/time/energy/friction/grasp absent')
            result['cases'][str(steps)]=record
        result['status']='EXPERIMENTAL' if all(c['status']=='EXPERIMENTAL' for c in result['cases'].values()) else 'FAIL'
    write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],cases={k:v['status'] for k,v in result['cases'].items()})))
if __name__=='__main__':main()
