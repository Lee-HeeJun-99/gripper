"""Actual separate routed Field/ODE; frozen qualified build, no object coupon."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_transmission_plan_run import make_plan
def parameter_value(meta):return meta.get('design_parameter_value',meta.get('amplitude_mm'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--design',choices=('quadratic','lateral','profiled','distributed'),default='quadratic');p.add_argument('--amplitude',type=float,choices=(0.,.5,2.,4.5,6.),required=True);p.add_argument('--duration',type=float,choices=(.0002,.0032,.05),default=.0002);p.add_argument('--refinement',type=int,choices=(1,2,4),default=1);p.add_argument('--provider',default='20261118_routed_math_api1240');p.add_argument('--profile');p.add_argument('--cost-pair',nargs=2);a=p.parse_args();ends,epochs=make_plan(a.duration,a.refinement,1,True);n=len(ends)
 if a.amplitude not in {'quadratic':(0.,4.5),'lateral':(0.,6.),'profiled':(0.,.5),'distributed':(0.,2.)}[a.design]:raise ValueError('frozen design parameter domain differs')
 module,field,owner,parameter={'quadratic':('ReGripFilmRoutedTransmission','FilmRoutedTendon','FilmRoutedPlanODE','routeAmplitude'),'lateral':('ReGripFilmLateralTransmission','FilmLateralTendon','FilmLateralPlanODE','lateralOffset'),'profiled':('ReGripFilmProfiledTransmission','FilmProfiledTendon','FilmProfiledPlanODE','profileAmplitude'),'distributed':('ReGripFilmDistributedTransmission','FilmDistributedTendon','FilmDistributedPlanODE','attachmentMode')}[a.design]
 provider=ROOT/'results'/('autonomous_film_'+a.provider);proof=json.loads((provider/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_transmission_hold50_1187';meta=json.loads((parent/'summary.json').read_text());binary=ROOT/proof['build_relative']/('lib'+module+'.so')
 if proof.get('design','quadratic')!=a.design:raise ValueError('source-bound compiled design differs')
 ramp=proof.get('control_ramp_s',.01)
 if ramp not in (.01,.04) or (a.design!='lateral' and ramp!=.01):raise ValueError('explicit source-bound C2 profile required')
 if proof['status']!='PASS' or meta['status']!='PASS':raise ValueError('qualified build and parent required')
 for path,digest in proof['source_hashes'].items():
  if sha(provider/'sources'/path)!=digest:raise ValueError('archived routed source changed')
 if sha(binary)!=proof['binary_sha256'] or sha(provider/'reference')!=proof['reference_binary_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=proof['sdk_runner_sha256']:raise ValueError('routed binary/SDK changed')
 for path,digest in meta['provider_hashes'].items():
  if sha(path)!=digest:raise ValueError('legacy mapping binary changed')
 for name,digest in meta['raw_hashes'].items():
  if sha(parent/name)!=digest:raise ValueError('parent input changed')
 forecast=None;cost_evidence=[]
 if n>8:
  if not a.profile:raise ValueError('actual same-amplitude cost profile required')
  previous=ROOT/'results'/('autonomous_film_'+a.profile);cost=json.loads((previous/'summary.json').read_text())
  if cost['status']!='PASS' or parameter_value(cost)!=a.amplitude or cost['binary_sha256']!=proof['binary_sha256']:raise ValueError('cost family differs')
  forecast=2*max(cost['process']['runtime_s'],cost['reference_process']['runtime_s'])*n/cost['steps']+30
  if a.cost_pair:
   sizes=[];rates=[]
   for name in a.cost_pair:
    path=ROOT/'results'/('autonomous_film_'+name)/'summary.json';c=json.loads(path.read_text())
    if c['status']!='PASS' or c['duration_s']!=.05 or parameter_value(c)!=a.amplitude or c['binary_sha256']!=proof['binary_sha256'] or c['reference_binary_sha256']!=proof['reference_binary_sha256']:raise ValueError('completed SAME-route cost family required')
    sizes.append(c['steps']);rates.append(max(c['process']['runtime_s'],c['reference_process']['runtime_s'])/c['steps']);cost_evidence.append(dict(case=name,summary_sha256=sha(path),steps=c['steps'],actual_s=c['process']['runtime_s'],reference_s=c['reference_process']['runtime_s']))
   if min(sizes)<250 or max(sizes)<500 or n>2*max(sizes):raise ValueError('bounded two-size extrapolation required')
   forecast=1.2*max(rates)*n+30
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(provider/'reference',out/'reference');shutil.copy2(parent/'public_mass.txt',out/'public_mass.txt');(out/'plan.txt').write_text(str(n)+'\n'+'\n'.join(format(t,'.17g') for t in ends)+'\n');r=dict(status='BLOCKED',scope='actual no-object routed coupon;NOT wrapping/contact/grasp certification',design=a.design,route_parameter_name=parameter,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_provider_case=a.provider,source_provider_commit=proof['source_commit'],source_provider_summary_sha256=sha(provider/'summary.json'),source_hashes=proof['source_hashes'],binary_sha256=proof['binary_sha256'],reference_binary_sha256=proof['reference_binary_sha256'],sdk=str(SDK),sdk_runner_sha256=proof['sdk_runner_sha256'],build_relative=proof['build_relative'],amplitude_mm=a.amplitude,control_ramp_s=ramp,steps=n,duration_s=a.duration,canonical_epochs=epochs,predicted_child_runtime_s=forecast,physical_input=('same core material/mass/root;C2 Hold Tmax .0001N/rail,ramp10ms,release50..60ms;route ONLY changed' if ramp==.01 else 'same core material/mass/root;C2 Hold Tmax .0001N/rail,ramp40ms,release50..60ms;separate source-bound control input'),full_wire_clearance='NOT QUALIFIED:finite wire/guide bodies absent',whole_energy='BLOCKED',root_reaction_work=None)
 r['cost_evidence']=cost_evidence
 r['design_parameter_value']=a.amplitude;r['design_parameter_units']='dimensionless' if a.design=='distributed' else 'mm'
 if a.design=='distributed':r['amplitude_mm']=None
 if a.design=='distributed':r['physical_input']='NEW attachment distribution ONLY;constant5mm normal/6mm outboard route;mode0 five clips,mode2 rootK.001/free sumK.004N/mm;SAME core/material/mass/root/C2 Hold .0001N/rail,10ms rise/50..60ms release;hardware/work NOT matched'
 if forecast and forecast>480:r['failure_reason']='measured policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 ref=guarded([out/'reference',out/'plan.txt',out/'public_mass.txt',out/'reference',str(a.amplitude)],out/'reference_process',480);r.update(status='FAIL',reference_process=ref);write_json(out/'summary.json',r)
 if ref['exit_code']==0:
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.remove(scene.find('FilmTransmissionHoldODE'));scene.set('time','0');scene.set('dt',format(ends[0],'.17g'))
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripFilmTransmission.so'):node.set('pluginName',str(binary))
   if node.tag=='FilmRailTendon':node.tag=field;node.set(parameter,str(a.amplitude));node.set('rampTime',str(ramp))
   for key,value in list(node.attrib.items()):
    if key in ('filename','displacementFilename') and value.startswith(str(parent)):node.set(key,str(out)+value[len(str(parent)):])
  ET.SubElement(scene,owner,dict(name='ode',root='@finger0/dofs',field='@finger0/assembly/filmField',filename=str(out/'actual.csv'),massFilename=str(out/'public_mass.txt'),maxSteps=str(n),planFilename=str(out/'plan.txt')));tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(n),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors,scene_sha256=sha(out/'scene.scn'))
  if run['exit_code']==0 and not errors:
   x=list(csv.DictReader((out/'actual.csv').open()));y=list(csv.DictReader((out/'reference.states.csv').open()));f=list(csv.DictReader((out/'film_0.csv').open()));c=list(csv.DictReader((out/'actual.csv.clock.csv').open()));lengths=len(x)==len(y)==len(f)==len(c)==n
   if not lengths:raise ValueError('incomplete actual/reference output')
   api={k:max(float(np.max(abs(np.fromstring(i[k],sep=' ')-np.fromstring(j[k],sep=' ')))) for i,j in zip(x,y)) for k in ('q','v')};clock=all(i['time']==j['time'] and float(i['time'])==t for i,j,t in zip(x,y,ends));stages=list(csv.DictReader((out/'actual.csv.stages.csv').open()))==list(csv.DictReader((out/'reference.stages.csv').open()));contexts=all(i['contexts']=='4' and i['exact_child_time']=='true' for i in c);T=max(abs(float(i['T_end'])-float(j['T_per_rail'])) for i,j in zip(x,f));momentum=max(float(i['momentum_residual']) for i in x);r.update(status='PASS' if max(api.values())<1e-12 and clock and stages and contexts and T==0 and momentum<=1e-17 else 'FAIL',reference_max_abs=api,api_gate=1e-12,accumulated_clock_exact=clock,all_contexts_exact=contexts,stage_rows_exact=stages,actual_control_error_N=T,momentum_residual_Ns=momentum)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','process','reference_process','canonical_epochs')}))
if __name__=='__main__':main()
