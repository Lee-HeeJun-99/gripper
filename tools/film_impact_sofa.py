"""Actual SOFA point-plane impact qualification; explicitly NOT film validation."""
import argparse,csv,json,subprocess,shutil,xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
SDK=Path('/home/ubuntu/SOFA/v26.06.00')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reuse',help='Explicit previously compiled plugin;source bytes must still match');p.add_argument('--midpoint-restart',action='store_true');p.add_argument('--fine-sequence',action='store_true');a=p.parse_args()
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    shutil.copy2(__file__,out/'runner.py')
    build=ROOT/'build'/('film_impact_sofa_'+a.tag);build.mkdir(exist_ok=False)
    archive=out/'sources';shutil.copytree(ROOT/'models/film_impact',archive/'models/film_impact')
    for name in ('film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
        target=archive/'models'/name;target.mkdir();
        for source in (ROOT/'models'/name).glob('*.h'):shutil.copy2(source,target/source.name)
    identity=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(s.relative_to(archive)):sha(s) for s in archive.rglob('*') if s.is_file()},sdk=str(SDK),script_sha256=sha(__file__),midpoint_restart=a.midpoint_restart,scope='point and isolated film impact API;NOT whole-surface/C2 full-cycle convergence')
    write_json(out/'identity.json',identity);stages={}
    if a.reuse:
        prior=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prior/'identity.json').read_text())
        if identity['sources']!=old['sources']:raise ValueError('reused compiled source differs')
        build=ROOT/'build'/('film_impact_sofa_'+a.reuse)
        if sha(build/'libReGripImpactReference.so')!=old['binary_sha256']:raise ValueError('reused binary drift')
        stages['build']=dict(exit_code=0,reused_from=a.reuse)
    else:
        stages['configure']=guarded(['cmake','-S',archive/'models/film_impact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
        stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if stages['configure']['exit_code']==0 else None
    result=dict(status='FAIL',scope=identity['scope'],stages=stages,cases={})
    binary=build/'libReGripImpactReference.so'
    if stages['build'] and stages['build']['exit_code']==0:
        identity['binary_sha256']=sha(binary)
        ldd=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(ldd)
        if 'not found' in ldd or any('=> /' in line and 'libSofa.' in line and str(SDK) not in line for line in ldd.splitlines()):raise ValueError('SDK identity/ABI mismatch')
        write_json(out/'identity.json',identity)
        for e in (0.,.5,1.):
            for steps in (20,40,80):
                case=out/('e'+str(e)+'_n'+str(steps));case.mkdir()
                scene=ET.Element('Node',name='force_free_impact_reference',dt=str(1/steps),gravity='0 0 0')
                ET.SubElement(scene,'RequiredPlugin',pluginName=str(binary))
                ET.SubElement(scene,'RequiredPlugin',pluginName='Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass')
                ET.SubElement(scene,'DefaultAnimationLoop')
                ET.SubElement(scene,'MechanicalObject',name='point',template='Vec3d',position='.371 0 0',velocity='-1 2 0')
                ET.SubElement(scene,'UniformMass',totalMass='2')
                ET.SubElement(scene,'BallisticPlaneImpact',body='@point',restitution=str(e),filename=str(case/'impact.csv'))
                path=case/'scene.scn';ET.ElementTree(scene).write(path)
                process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',path],case/'process',60)
                record=dict(status='FAIL',process=process)
                try:
                    log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
                    if process['exit_code'] or '[ERROR]' in log:raise ValueError('SOFA error')
                    rows=list(csv.DictReader((case/'impact.csv').open()));events=[r for r in rows if r['event_time']!='null']
                    if len(rows)!=steps or len(events)!=1:raise ValueError('incomplete records or incorrect event count')
                    event=events[0];last=rows[-1]
                    errors=dict(event_time=abs(float(event['event_time'])-.371),impulse=abs(float(event['impulse'])-2*(1+e)),post_velocity=abs(float(event['post_normal'])-e),loss=abs(float(event['impact_loss'])-(1-e*e)),position=abs(float(last['x'])-e*(1-.371)),tangent=abs(float(last['y'])-2),momentum=abs(float(event['momentum_residual'])))
                    record.update(status='PASS' if max(errors.values())<1e-12 else 'FAIL',absolute_errors=errors,event=event,last=last)
                except (ValueError,OSError) as error:record['failure_reason']=str(error)
                result['cases'][case.name]=record
        # Same installed SDK, actual existing film FF/mass/root mapping. Event
        # is deliberately supplied at t=0; no autonomous birth claim is made.
        prior=ROOT/'results/autonomous_film_20261117_c2_bounded_short401'
        parent=json.loads((prior/'identity.json').read_text())
        case=out/'supplied_film_event';case.mkdir()
        tree=ET.parse(prior/'1/scene.scn');scene=tree.getroot()
        for child in list(scene):
            if child.tag in ('FilmNativeCoupledCorrection','FilmNativeObserver') or (child.tag=='RequiredPlugin' and 'libReGripFilmNativeObserver.so' in child.get('pluginName','')):scene.remove(child)
        plugin_paths={Path(child.get('pluginName','')).name:Path(child.get('pluginName','')) for child in scene.findall('RequiredPlugin')}
        for name,key in (('libReGripFilmShell.so','core_sha256'),('libReGripFilmRailTendon.so','assembly_sha256')):
            if sha(plugin_paths[name])!=parent[key]:raise ValueError('archived film source/binary identity drift')
        for element in scene.iter():
            for key,value in list(element.attrib.items()):
                if str(prior/'1') in value:element.set(key,value.replace(str(prior/'1'),str(case)))
        ET.SubElement(scene,'RequiredPlugin',pluginName=str(binary))
        field=scene.find("Node[@name='assembly']/FilmRailTendon");field.set('maximumTension','0')
        # The supplied-event owner is NOT a full accepted-step correction.
        # Use the supported standalone Newton solver, never predictor-only mode.
        scene.find('ReGripBDFSolver').set('nativeCoupledPredictor','0')
        root=scene.find("MechanicalObject[@name='dofs']");velocity=[0.]*(231*3);velocity[3*102+2]=-3
        root.set('velocity',' '.join(map(str,velocity)))
        scene.find("Node[@name='fixed']/MechanicalObject").set('position','100 12 -8.01')
        ET.SubElement(scene,'FilmSuppliedEventImpulse',root='@dofs',field='@assembly/filmField',node='102',radius='8.01',center='100 12 -8.01',filename=str(case/'event.csv'))
        path=case/'scene.scn';tree.write(path)
        process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',path],case/'process',60)
        record=dict(status='FAIL',process=process,scope='supplied initial event on mapped actual film;NOT detected first contact or time convergence')
        try:
            log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
            if process['exit_code'] or '[ERROR]' in log:raise ValueError('actual film event API error')
            rows=list(csv.DictReader((case/'event.csv').open()))
            if len(rows)!=1:raise ValueError('exactly one event commit required')
            event=rows[0];checks=dict(pre_velocity=abs(float(event['pre_normal'])+3)<1e-12,post_velocity=abs(float(event['post_normal']))<1e-12,momentum=float(event['momentum_residual'])<1e-20,energy=float(event['impact_loss'])>0,nonnegative_impulse=float(event['impulse'])>0,restart=float(event['history_beta'])==1,purity=event['query_pure']=='1')
            record.update(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,event=event,film_binaries={name:sha(plugin_paths[name]) for name in ('libReGripFilmShell.so','libReGripFilmRailTendon.so')})
        except (OSError,ValueError) as error:record['failure_reason']=str(error)
        result['cases']['supplied_film_event']=record
        isolated=out/'isolated_film_birth';isolated.mkdir()
        isolated_scene=ET.fromstring(ET.tostring(scene))
        for element in isolated_scene.iter():
            for key,value in list(element.attrib.items()):
                if str(case) in value:element.set(key,value.replace(str(case),str(isolated)))
        supplied=isolated_scene.find('FilmSuppliedEventImpulse');isolated_scene.remove(supplied)
        isolated_scene.set('dt','.001')
        isolated_scene.find("Node[@name='fixed']/MechanicalObject").set('position','100 12 -8.011')
        ET.SubElement(isolated_scene,'FilmIsolatedEventStep',root='@dofs',field='@assembly/filmField',node='102',radius='8.01',center='100 12 -8.011',filename=str(isolated/'event.csv'))
        isolated_scene.find('FilmIsolatedEventStep').set('midpointRestart',str(int(a.midpoint_restart)))
        isolated_path=isolated/'scene.scn';ET.ElementTree(isolated_scene).write(isolated_path)
        process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',isolated_path],isolated/'process',120)
        record=dict(status='FAIL',process=process,scope='ONE isolated point birth on subintegrated actual film + plastic impulse + BE remainder;NOT whole-triangle CCD, sustained contact, C2 onset or time convergence')
        try:
            log=(isolated/'process/stdout.log').read_text()+(isolated/'process/stderr.log').read_text()
            if process['exit_code'] or '[ERROR]' in log:raise ValueError('isolated film impact execution error')
            rows=list(csv.DictReader((isolated/'event.csv').open()));end=list(csv.DictReader((isolated/'event.csv.endpoint.csv').open()))
            if len(rows)!=1 or len(end)!=1:raise ValueError('incomplete isolated event/endpoint')
            event=rows[0];endpoint=end[0]
            checks=dict(event_time=0<float(event['event_time'])<.001,gap=abs(float(event['gap']))<=1e-10,closing=float(event['pre_normal'])<0,post_velocity=abs(float(event['post_normal']))<1e-12,impulse=float(event['impulse'])>0,loss=float(event['impact_loss'])>=0,momentum=float(event['momentum_residual'])<1e-20,remainder=float(endpoint['gap'])>=0,restart=event['history_beta']=='1')
            record.update(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,event=event,endpoint=endpoint)
        except (OSError,ValueError) as error:record['failure_reason']=str(error)
        result['cases']['isolated_film_birth']=record
        sequences={};counts=(40,80,160) if a.fine_sequence else (20,40,80)
        if a.fine_sequence:
            measured=json.loads((ROOT/'results/autonomous_film_20261117_impact_midpoint464/summary.json').read_text())['cases']['film_sequence_80']['process']['runtime_s']
            forecast=measured*2*2
            write_json(out/'sequence_budget.json',dict(measured_80_s=measured,predicted_160_s_with_margin2=forecast,child_limit_s=120,scope='same1ms geometry/control,additional event tangent outputs only;no3200step C2 launch'))
            if forecast>120:raise ValueError('fine sequence profile exceeds120s')
        for steps in counts:
            target=out/('film_sequence_'+str(steps));target.mkdir()
            node=ET.fromstring(ET.tostring(isolated_scene));node.set('dt',str(.001/steps))
            for element in node.iter():
                for key,value in list(element.attrib.items()):
                    if str(isolated) in value:element.set(key,value.replace(str(isolated),str(target)))
            node.find('FilmIsolatedEventStep').set('isolatedSequence','1')
            node.find('FilmIsolatedEventStep').set('maximumSequenceSteps',str(max(counts)))
            path=target/'scene.scn';ET.ElementTree(node).write(path)
            process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',path],target/'process',120)
            record=dict(status='FAIL',process=process,scope='1ms zero-tension single-point impact cold start;NOT C2 old434/437, whole-surface contact or full energy')
            try:
                log=(target/'process/stdout.log').read_text()+(target/'process/stderr.log').read_text()
                if process['exit_code'] or '[ERROR]' in log:raise ValueError('film sequence execution error')
                events=list(csv.DictReader((target/'event.csv').open()));rows=list(csv.DictReader((target/'event.csv.endpoint.csv').open()))
                if len(events)!=1 or len(rows)!=steps:raise ValueError('incomplete sequence or impact count')
                if any(float(row['gap'])<0 for row in rows):raise ValueError('point remainder penetration')
                record.update(status='PASS',event=events[0],endpoint=rows[-1]);sequences[steps]=(events[0],rows)
            except (OSError,ValueError) as error:record['failure_reason']=str(error)
            result['cases']['film_sequence_'+str(steps)]=record
            if process['runtime_s']/steps*max(counts)*2>120:
                result['sequence_policy_block']='measured sequence forecast exceeds120s;no finer physics launched';break
        pairs={}
        for coarse,fine in ((counts[0],counts[1]),(counts[1],counts[2]),(counts[0],counts[2])):
            if coarse not in sequences or fine not in sequences:continue
            ae,ar=sequences[coarse];be,br=sequences[fine];errors={}
            for key in ('event_time','pre_normal','impulse','impact_loss'):
                av,bv=float(ae[key]),float(be[key]);absolute=abs(av-bv);relative=absolute/abs(bv) if bv else (0 if absolute==0 else None)
                errors[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
            ratio=fine//coarse
            for key in ('local_displacement','local_velocity','shell_energy','attachment_energy','kinetic_energy'):
                absolute=0.;scale=0.
                for i,row in enumerate(ar):
                    other=br[ratio*(i+1)-1]
                    if abs(float(row['time'])-float(other['time']))>1e-12:raise ValueError('physical-time alignment')
                    x=np.fromstring(row[key],sep=' ');y=np.fromstring(other[key],sep=' ')
                    if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('nonfinite sequence metric')
                    absolute=max(absolute,float(np.linalg.norm(x-y)));scale=max(scale,float(np.linalg.norm(y)))
                relative=absolute/scale if scale else (0 if absolute==0 else None)
                errors[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
            pairs[str(coarse)+':'+str(fine)]=errors
        result['sequence_time']=dict(status='PASS' if len(pairs)==3 and all(e['status']=='PASS' for pair in pairs.values() for e in pair.values()) else 'FAIL',gate=.001,pairs=pairs,scope='separate1ms initial-velocity/zero-tension single-point model;original C2 contact-time FAILs UNCHANGED')
        result['execution_status']='PASS' if all(c['status']=='PASS' for c in result['cases'].values()) else 'FAIL'
        result['status']='PASS' if result['execution_status']=='PASS' and result['sequence_time']['status']=='PASS' else 'FAIL'
        result['qualification_scope_only']=identity['scope']
        result['original_C2_contact_time']='FAIL:unchanged434/437'
        result['whole_surface_CCD']='NOT RUN';result['whole_physical_energy']='BLOCKED';result['free_grasp']='NOT RUN'
    write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],cases={k:v['status'] for k,v in result['cases'].items()})))
if __name__=='__main__':main()
