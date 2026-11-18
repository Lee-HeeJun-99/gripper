"""Actual single-coupon rail-aspect comparison;no object/contact/grasp claims."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_rail_aspect_response import CPP
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build-provider',required=True);p.add_argument('--steps',type=int,choices=(8,50,100,200),default=8);p.add_argument('--dt-us',type=int,choices=(50,100,200),default=200);p.add_argument('--profile');a=p.parse_args();nominal={50:.00005,100:.0001,200:.0002}[a.dt_us];provider=ROOT/'results'/('autonomous_film_'+a.build_provider);pm=json.loads((provider/'summary.json').read_text());scene_provider=ROOT/'results/autonomous_film_20261118_lateral_six_smoke1359';sm=json.loads((scene_provider/'summary.json').read_text());mass_provider=ROOT/'results/autonomous_film_20261119_rail_aspect_peak1652';mm=json.loads((mass_provider/'summary.json').read_text())
 if pm['status']!='PASS' or sm['status']!='PASS' or mm['status']!='EXPERIMENTAL':raise ValueError('actual API,scene and measured same-core screen required')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('compiled physical model source changed')
 binary=ROOT/pm['build_relative']/'libReGripFilmRailAspect.so'
 if sha(binary)!=pm['binary_sha256'] or sha(scene_provider/'scene.scn')!=sm['scene_sha256']:raise ValueError('qualified actual binary/scene changed')
 forecast=60.
 if a.steps>8:
  if not a.profile:raise ValueError('measured eight-step actual profile required')
  prior=ROOT/'results'/('autonomous_film_'+a.profile);profile=json.loads((prior/'summary.json').read_text())
  if profile['status']!='PASS' or profile['steps']!=8 or profile['binary_sha256']!=pm['binary_sha256']:raise ValueError('same-binary actual physical profile required')
  forecast=2*max(max(x['process']['runtime_s'],x['reference_process']['runtime_s']) for x in profile['trials'].values())*a.steps/8+30
 if forecast>480:raise ValueError('actual measured forecast>480;NOT OS exhaustion')
 mass=mass_provider/'public_mass.txt'
 if sha(mass)!=mm['public_mass_sha256']:raise ValueError('exact same actual public mass required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True)
 code=CPP.replace('std::ofstream out(argv[3]);','std::ofstream out(argv[3]);std::ofstream stages(std::string(argv[3])+".stages.csv");stages<<std::setprecision(17)<<"macro,stage,time,weight,T,q,v\\n";').replace('double time=0,h=.0002;',f'double time=0,h={nominal:.17g},used={nominal:.17g},endpoint={nominal:.17g}*std::stoul(argv[4]);').replace('++k){auto map=','++k){h=(time+used)-time;auto map=')
 anchor='time+=h;q=map.expand(r.q);';stage='for(unsigned j=0;j<2;++j){double t=time+h*(.5+(j?1:-1)*std::sqrt(3.)/6);stages<<k+1<<\',\'<<j<<\',\'<<t<<\',\'<<h/2<<\',\'<<c.sample(t).tension;quote(stages,map.expand(r.stageQ[j]));quote(stages,map.expand(r.stageV[j]));stages<<\'\\n\';}stages.flush();time+=used;q=map.expand(r.q);'
 if code.count(anchor)!=1:raise ValueError('exact qualified reference clock anchor required')
 code=code.replace(anchor,stage).replace('out.flush();}}catch','out.flush();if(k+2==std::stoul(argv[4]))used=endpoint-time;}}catch');cpp=diag/'RailAspectActualReference.cpp';cpp.write_text(code);shutil.copy2(mass,out/'public_mass.txt');rc=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120);r=dict(status='FAIL',scope='actual SOFA single free Film/Rails/Tendon rail-aspect response ONLY;NO object/contact/wrapping/grasp or time certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),compiled_plugin_source_commit=pm['source_commit'],source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compiled_plugin_source_hashes=pm['source_hashes'],build_provider_summary_sha256=sha(provider/'summary.json'),scene_provider_summary_sha256=sha(scene_provider/'summary.json'),binary_sha256=sha(binary),build_relative=pm['build_relative'],sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),steps=a.steps,nominal_dt_s=.0002,duration_s=.0002*a.steps,predicted_child_runtime_s=forecast,reference_compile=rc,public_mass_sha256=sha(out/'public_mass.txt'),matched_core_volume=True,matched_material=True,matched_nodal_mass=True,matched_tension_profile=True,matched_actuation_work=False,guide_solid_mass=None,root_work=None,holding_load=None,selected_design=None,trials={})
 r.update(nominal_dt_s=nominal,duration_s=nominal*a.steps)
 ledger=json.loads((ROOT/'reports/FILM_CONTACT_EVIDENCE_20261118_three_film_recovery_v12.json').read_text())
 if rc['exit_code']==0:
  r['reference_binary_sha256']=sha(out/'reference')
  for thickness in (.075,.1,.125):
   folder=out/('rail'+str(thickness));folder.mkdir();ref=guarded([out/'reference',str(thickness),out/'public_mass.txt',folder/'reference.csv',str(a.steps)],folder/'reference_process',480);trial=dict(reference_process=ref);r['trials'][str(thickness)]=trial
   if ref['exit_code']!=0:continue
   r['nominal_dt_s']=nominal;r['duration_s']=nominal*a.steps
   tree=ET.parse(scene_provider/'scene.scn');scene=tree.getroot();scene.set('dt',format(nominal,'.17g'));scene.set('time','0');owner=scene.find('FilmLateralPlanODE');owner.tag='FilmRailAspectODE';owner.attrib.pop('planFilename');owner.set('maxSteps',str(a.steps));owner.set('endTime',format(nominal*a.steps,'.17g'));owner.set('filename',str(folder/'actual.csv'));owner.set('massFilename',str(out/'public_mass.txt'));field=scene.find('.//FilmLateralTendon');field.tag='FilmAspectTendon';field.set('railThickness',str(thickness));field.set('maximumTension','.0001');field.set('rampTime','.01');field.set('releaseBegin','.02');field.set('releaseEnd','.03');field.set('c2Control','1');field.set('filename',str(folder/'film.csv'));field.set('displacementFilename',str(folder/'displacement.csv'))
   # Old world mapping assumes100um rails. It is visualization-only,not mass.
   # Keep its existing child context but remove that inapplicable geometry.
   visual=scene.find('.//Node[@name="visual"]')
   if visual is None:
    candidates=[node for node in scene.iter('Node') if node.find('FilmAssemblyWorldMapping') is not None]
    if len(candidates)!=1:raise ValueError('one original visualization context required')
    visual=candidates[0]
   # DiagonalMass references this topology even with explicit vertex masses.
   # Retain its connectivity/reference coordinates,not the old world mapping.
   for child in list(visual):
    if child.tag not in ('TriangleSetTopologyContainer','MechanicalObject'):visual.remove(child)
   topology=visual.find('TriangleSetTopologyContainer')
   if topology is None:raise ValueError('mass-linked reference topology required')
   old_width=(439.3397917746089/3-100*24*.05)/(2*100*.1);width=old_width if thickness==.1 else old_width*.1/thickness;rest=[]
   for ny,w,y,z in ((5,24.,0.,0.),(3,width,0.,-(.05+thickness)/2),(3,width,24-width,-(.05+thickness)/2)):
    for i in range(21):
     for j in range(ny):rest.extend((100.*i/20,y+w*j/(ny-1),z))
   topology.set('position',' '.join(format(x,'.17g') for x in rest))
   geometry=visual.find('MechanicalObject')
   if geometry is None:raise ValueError('DiagonalMass geometryState reference must remain valid')
   geometry.set('position',' '.join(format(x,'.17g') for x in rest))
   geometry.set('velocity',' '.join('0' for _ in rest))
   trial['mass_reference_geometry']='static new-design rest coordinates for DiagonalMass initialization ONLY;actual deformed geometry comes from Field x=rest+u;no old world mapping'
   for node in scene.findall('RequiredPlugin'):
    path=node.get('pluginName','')
    if path.endswith('/libReGripFilmLateralTransmission.so'):
     if sha(path)!=sm['binary_sha256']:raise ValueError('old primary component changed')
     node.set('pluginName',str(binary))
    elif path.startswith('/'):
     from pathlib import Path
     key=str(Path(path).relative_to(ROOT))
     if sha(path)!=ledger['files'].get(key):raise ValueError('immutable native/root provider changed')
   tree.write(folder/'scene.scn');trial['scene_sha256']=sha(folder/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',folder/'scene.scn'],folder/'process',480);errors=sum((folder/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));trial.update(process=run,sofa_errors=errors)
   if run['exit_code'] or errors:
    trial['status']='FAIL';r['failure_reason']='actual initialization/runtime failed;remaining candidates NOT RUN';break
   actual=list(csv.DictReader((folder/'actual.csv').open()));expected=list(csv.DictReader((folder/'reference.csv').open()));fields=list(csv.DictReader((folder/'film.csv').open()));delta={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};stages=list(csv.DictReader((folder/'actual.csv.stages.csv').open()))==list(csv.DictReader((folder/'reference.csv.stages.csv').open()));energy=max(max(abs(float(x['U_shell'])-float(y['U_skin'])-float(y['U_rails'])),abs(float(x['U_attachment'])-float(y['U_attachment'])),abs(float(x['K'])-float(y['K']))) for x,y in zip(fields,expected));clocks=[x['time'] for x in actual]==[x['time'] for x in expected];tension=all(float(x['T_per_rail'])==float(y['T_per_rail_N']) for x,y in zip(fields,expected));trial.update(status='PASS' if len(actual)==len(expected)==len(fields)==a.steps and max(delta.values())<=1e-12 and stages and clocks and tension and energy<=1e-12 else 'FAIL',reference_max_abs=delta,ALL_Gauss_stages_EXACT=stages,accumulated_clocks_EXACT=clocks,actual_tension_EXACT=tension,field_energy_max_abs_Nmm=energy,endpoint_shape=shape(np.fromstring(actual[-1]['q'],sep=' ')),stage_tendon_work_Nmm=float(expected[-1]['stage_tendon_work_Nmm']),raw_hashes={f.name:sha(f) for f in folder.iterdir() if f.suffix in ('.txt','.csv')})
  if len(r['trials'])==3 and all(x.get('status')=='PASS' for x in r['trials'].values()):r['status']='PASS'
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compiled_plugin_source_hashes','trials','reference_compile')}))
if __name__=='__main__':main()
