"""Bounded same-binary variants of a COMPLETED native contact trial.

Default:halve dt. --extend-duration:post-release observation at unchanged dt.
--two-sided-contact:separate PHYSICAL collision-side contrast,not refinement.
No partial checkpoint restore,kernel rebuild or convergence approval.
"""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);mode=p.add_mutually_exclusive_group();mode.add_argument('--extend-cycle',action='store_true');mode.add_argument('--extend-duration',action='store_true');mode.add_argument('--two-sided-contact',action='store_true');p.add_argument('--displacement-journal',action='store_true');p.add_argument('--owner-case',help='Explicit separately built/tested replacement candidate owner;NOT a same-binary comparison');p.add_argument('--broad-phase',action='store_true');p.add_argument('--actuation-case',help='Explicit compatible assembly replacement;requires same owner-case and C2 input');a=p.parse_args()
    if not a.tag.replace('_','').isalnum() or not a.case.replace('_','').isalnum():raise ValueError('campaign name')
    source=ROOT/'results'/('autonomous_film_'+a.case);reference=json.loads((source/'summary.json').read_text())
    if reference.get('status')!='PASS' or not reference.get('finite'):raise ValueError('complete finite source required')
    command=json.loads((source/'1/process/command.json').read_text());previous_steps=int(command[command.index('-n')+1]);bound_only=a.broad_phase and not (a.extend_cycle or a.extend_duration);steps=previous_steps if a.two_sided_contact or bound_only else 2*previous_steps
    margin=2 if a.extend_cycle else 1.25 if a.extend_duration else 1.5
    estimate=reference['stages']['physics']['runtime_s']*(1 if a.two_sided_contact or bound_only else 2)*margin
    if steps>1600 or estimate>480:raise ValueError('measured refinement projection exceeds bounded1600-step/480s policy')
    identity=json.loads((source/'identity.json').read_text());tree=ET.parse(source/'1/scene.scn');root=tree.getroot()
    if identity.get('accepted_integrator') not in ('BE','uniform BDF2 after BE startup') or root.find('FilmNativeCoupledCorrection') is None:raise ValueError('completed coupled BE/uniform-BDF2 source only')
    field=root.find("Node[@name='assembly']/FilmRailTendon")
    if a.extend_cycle:
        duration=previous_steps*float(root.get('dt'))
        if identity['accepted_integrator']!='BE' or not identity.get('candidate_complete') or abs(duration-float(field.get('rampTime')))>1e-10 or abs(2*duration-float(field.get('releaseEnd')))>1e-10:raise ValueError('cycle extension needs candidate-complete measured closing profile through ramp;new duration exactly releaseEnd')
    if a.two_sided_contact and identity.get('object_shape')!='sphere':raise ValueError('two-sided thin-film contrast is sphere-only;do not change closed object-mesh sidedness')
    if a.extend_duration and (identity['accepted_integrator']!='BE' or previous_steps*float(root.get('dt'))<float(field.get('releaseEnd'))-1e-10):raise ValueError('extension needs a completed measured release window;BE only')
    if a.displacement_journal:
        declared=identity.get('assembly_source_case')
        proof=ROOT/'results'/('autonomous_film_'+str(declared))
        if declared!='20261117_local_probe293' or 'displacementFilename' not in (proof/'sources/film_rail_tendon/FilmRailTendon.cpp').read_text():raise ValueError('exact recorder requires the explicitly qualified293/296 assembly')
    expected={}
    for name,component in (('core','ReGripFilmShell'),('assembly','ReGripFilmRailTendon'),('observer','ReGripFilmNativeObserver')):
        matches=[Path(n.get('pluginName')) for n in root.findall('RequiredPlugin') if n.get('pluginName','').endswith('/lib'+component+'.so')]
        if len(matches)!=1 or sha(matches[0])!=identity[name+'_sha256']:raise RuntimeError('immutable binary identity drift:'+name)
        expected[str(matches[0])]=sha(matches[0])
    replacement=None;old_owner=None
    replacement_assembly=None;old_assembly=None
    if a.owner_case:
        if not a.extend_cycle or not a.owner_case.replace('_','').isalnum() or not identity.get('candidate_complete'):raise ValueError('owner replacement is a separately identified candidate-closing extension only')
        owner_source=ROOT/'results'/('autonomous_film_'+a.owner_case)
        own=json.loads((owner_source/'identity.json').read_text());qualified=json.loads((owner_source/'summary.json').read_text())
        if qualified.get('status')!='PASS' or not own.get('candidate_complete') or own['sdk']!=identity['sdk']:raise ValueError('completed source-compatible candidate-owner qualification and SAME SDK required')
        for relative in ('film_rail_tendon/Kernel.h','film_shell/Kernel.h','film_shell/AD.h','film_shell/PlaneContact.h','film_native_contact/CoupledPlaneStep.h','film_native_contact/CoupledContactStep.h','film_native_contact/CoupledBDFHistory.h','film_sphere_contact/ClosestPrimitive.h'):
            if sha(source/'sources'/relative)!=sha(owner_source/'sources'/relative):raise ValueError('replacement changes qualified mechanics:'+relative)
        candidate=ET.parse(owner_source/'1/scene.scn').getroot()
        replacement=next(Path(n.get('pluginName')) for n in candidate.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripFilmNativeObserver.so'))
        if sha(replacement)!=own['observer_sha256']:raise ValueError('replacement owner binary drift')
        old_owner=next(str(n.get('pluginName')) for n in root.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripFilmNativeObserver.so'))
        expected.pop(old_owner);expected[str(replacement)]=sha(replacement)
        identity.update(observer_sha256=sha(replacement),replacement_owner_case=a.owner_case,replacement_owner_identity_sha256=sha(owner_source/'identity.json'))
        if a.actuation_case:
            if a.actuation_case!=a.owner_case or field.get('c2Control','0')!='1' or not own.get('c2_control'):raise ValueError('C2 actuation replacement must come from SAME completed owner campaign')
            replacement_assembly=next(Path(n.get('pluginName')) for n in candidate.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripFilmRailTendon.so'))
            if sha(replacement_assembly)!=own['assembly_sha256']:raise ValueError('replacement assembly binary drift')
            old_assembly=next(str(n.get('pluginName')) for n in root.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripFilmRailTendon.so'))
            expected.pop(old_assembly);expected[str(replacement_assembly)]=sha(replacement_assembly)
            identity.update(assembly_sha256=sha(replacement_assembly),assembly_source_case=a.actuation_case,replacement_actuation_case=a.actuation_case)
        elif field.get('c2Control','0')=='1' and sha(source/'sources/film_rail_tendon/ControlProfile.h')!=sha(owner_source/'sources/film_rail_tendon/ControlProfile.h'):raise ValueError('C2 force/owner definitions differ;explicit compatible assembly replacement required')
    elif a.actuation_case:raise ValueError('actuation replacement requires an explicit compatible owner')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);case=out/'1';case.mkdir();shutil.copytree((owner_source if replacement else source)/'sources',out/'sources')
    for node in root.iter():
        for key,value in list(node.attrib.items()):node.set(key,value.replace(str(source/'1'),str(case)))
    if replacement:
        for node in root.findall('RequiredPlugin'):
            if node.get('pluginName')==old_owner:node.set('pluginName',str(replacement))
            if replacement_assembly and node.get('pluginName')==old_assembly:node.set('pluginName',str(replacement_assembly))
    if a.broad_phase:
        owner=root.find('FilmNativeCoupledCorrection')
        if owner.get('candidateComplete')!='1' or 'candidateBroadPhase' not in (out/'sources/film_native_contact/CoupledNativeCorrection.cpp').read_text() or owner.get('candidateBroadPhase','0')!='0':raise ValueError('qualified candidate owner with disabled broadphase required')
        owner.set('candidateBroadPhase','1')
    if not a.extend_duration and not a.extend_cycle and not a.two_sided_contact and not bound_only:root.set('dt',str(float(root.get('dt'))/2))
    if a.two_sided_contact:
        if any(node.get('bothSide','0') not in ('0','false') for node in root.iter() if node.tag in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel')):raise ValueError('two-sided contrast requires a one-sided source')
        for node in root.iter():
            if node.tag in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):node.set('bothSide','1')
    if a.displacement_journal:field.set('displacementFilename',str(case/'displacement.csv'))
    tree.write(case/'scene.scn')
    # Verify the only physical/numerical scene change is dt. Output addresses
    # are normalized back before byte comparison of the parsed XML tree.
    check=ET.parse(case/'scene.scn')
    for node in check.getroot().iter():
        for key,value in list(node.attrib.items()):node.set(key,value.replace(str(case),str(source/'1')))
    check.getroot().set('dt',ET.parse(source/'1/scene.scn').getroot().get('dt'))
    if replacement:
        for node in check.getroot().findall('RequiredPlugin'):
            if node.get('pluginName')==str(replacement):node.set('pluginName',old_owner)
            if replacement_assembly and node.get('pluginName')==str(replacement_assembly):node.set('pluginName',old_assembly)
    if a.broad_phase:
        old=ET.parse(source/'1/scene.scn').find('FilmNativeCoupledCorrection').get('candidateBroadPhase')
        if old is None:check.find('FilmNativeCoupledCorrection').attrib.pop('candidateBroadPhase')
        else:check.find('FilmNativeCoupledCorrection').set('candidateBroadPhase',old)
    if a.displacement_journal:
        previous_local=ET.parse(source/'1/scene.scn').find("Node[@name='assembly']/FilmRailTendon").get('displacementFilename')
        if previous_local is None:check.find("Node[@name='assembly']/FilmRailTendon").attrib.pop('displacementFilename')
        else:check.find("Node[@name='assembly']/FilmRailTendon").set('displacementFilename',previous_local)
    if a.two_sided_contact:
        original=list(ET.parse(source/'1/scene.scn').getroot().iter())
        for node,old in zip(check.getroot().iter(),original):
            if node.tag in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):
                if 'bothSide' in old.attrib:node.set('bothSide',old.get('bothSide'))
                else:node.attrib.pop('bothSide')
    if ET.tostring(check.getroot())!=ET.tostring(ET.parse(source/'1/scene.scn').getroot()):raise RuntimeError('unexpected scene change')
    command[command.index('-n')+1]=str(steps);command[-1]=str(case/'scene.scn')
    identity.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=__import__('sys').argv,
        scene_sha256=sha(case/'scene.scn'),reuse_binary_source_case=a.case,reuse_identity_sha256=sha(source/'identity.json'),
        same_binary_time_refinement=1 if a.extend_duration or a.extend_cycle or a.two_sided_contact or bound_only else 2,duration_extension=2 if a.extend_duration or a.extend_cycle else 1,contact_surface_sides='two-sided' if a.two_sided_contact else identity.get('contact_surface_sides','one-sided'),local_displacement_journal=a.displacement_journal or identity.get('local_displacement_journal',False),compiled_source_note='Copied immutable source archive;NO new compilation in THIS clone',
        refinement_script_sha256=sha(__file__),same_binary=not bool(replacement),broadphase=a.broad_phase or identity.get('broadphase',False),compiled_source_composition=('Owner sources from '+a.owner_case+';core reused from '+a.case+';assembly from '+(a.actuation_case or a.case)) if replacement else 'Unmodified copied archive',coupled_budget=dict(projected_seconds=estimate,profile=a.case,margin=margin,hard_seconds=480))
    write_json(out/'identity.json',identity)
    if any(sha(Path(path))!=value for path,value in expected.items()):raise RuntimeError('prelaunch binary drift')
    process=guarded(command,case/'process',480)
    rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else []
    finite=bool(rows) and all(math.isfinite(float(value)) for row in rows for key,value in row.items() if key!='x') and all(math.isfinite(float(value)) for row in rows for value in row['x'].split())
    log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
    ok=process['exit_code']==0 and len(rows)==steps and finite and not any(s in log for s in ('[ERROR]','Unused Attribute','Newton-Raphson method failed to converge'))
    variant='broadphase contrast' if bound_only else 'closing-through-release extension' if a.extend_cycle else 'two-sided-contact physical contrast' if a.two_sided_contact else 'post-release observation extension' if a.extend_duration else 'half-dt refinement'
    result=dict(status='PASS' if ok else 'FAIL',scope=('explicit replacement-owner ' if replacement else 'same-binary ')+variant+' execution only;time/grasp certification NOT approved',finite=finite,stages=dict(physics=process),rows=len(rows),last={k:v for k,v in rows[-1].items() if k!='x'} if rows else None)
    write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','finite','rows')}))

if __name__=='__main__':main()
