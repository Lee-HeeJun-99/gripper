"""Full prescribed-tension cycle observables at matching physical times."""
import argparse,csv,json,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);data={};info={};inputs={};config=None
 for tag in a.cases:
  directory=ROOT/'results'/('autonomous_film_'+tag);summary=json.loads((directory/'summary.json').read_text())
  if summary['status']!='PASS':raise RuntimeError('partial/failed physical trial')
  source=directory/'1';tree=ET.parse(source/'scene.scn');root=tree.getroot();center=np.fromstring(root.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ');field=root.find("Node[@name='assembly']/FilmRailTendon");physical=dict(numerical_owner={k:(root.find('FilmNativeCoupledCorrection').get(k,'0') if root.find('FilmNativeCoupledCorrection') is not None else '0') for k in ('completeFreeStage','previousVelocityGuess','potentialMerit','currentSphereNormal','closestSpherePrimitive','sqpMerit')},predictor_only=root.find('ReGripBDFSolver').get('nativeCoupledPredictor','0'),accepted_integrator=root.find('FilmNativeCoupledCorrection').get('integrationOrder','1') if root.find('FilmNativeCoupledCorrection') is not None else '1',object_mesh=json.loads((directory/'identity.json').read_text()).get('cylinder_segments'),coupled=root.find('FilmSphereCoupledCorrection') is not None,general_coupled=root.find('FilmNativeCoupledCorrection') is not None,object_shape=root.find('FilmNativeObserver').get('objectShape','sphere'),mesh=field.get('nx'),bond=field.get('bondStiffness'),guide_intervals=field.get('guideIntervals','4'),center=center.tolist(),control={k:field.get(k) for k in ('maximumTension','guideOffset','rampTime','releaseBegin','releaseEnd')})
  if config is not None and config!=physical:raise RuntimeError('different physics; cannot compare as dt convergence')
  config=physical;j=list(csv.DictReader((source/'journal.csv').open()));c=list(csv.DictReader((source/'contact.csv').open()));t=np.array([float(r['time']) for r in c]);dt=np.array([float(r['dt']) for r in c]);F=np.array([np.fromstring(r['body_force'],sep=' ') for r in c]);norm=np.linalg.norm(F,axis=1)
  if len(j)!=len(c) or any(abs(float(x['time'])-float(y['time']))>1e-12 for x,y in zip(j,c)):raise RuntimeError('unsynchronized journals')
  if any(int(r['unmatched_jacobian_rows']) for r in c):raise RuntimeError('unmatched actual Jacobian')
  nonzero=np.flatnonzero(norm>0);data[tag]=dict(time=t,normal_force=norm,scalar_impulse=np.cumsum(norm*dt),**{k:np.array([float(r[k]) for r in j]) for k in ('skin_tip_z','U_shell','U_attachment','K','tendon_work')})
  info[tag]=dict(first_load_time=float(t[nonzero[0]]) if len(nonzero) else None,peak_load_F=float(max(norm)),maximum_begin_radial_moment_defect=float(max(np.linalg.norm(np.fromstring(r['body_moment_begin'],sep=' ')-np.cross(center,f)) for r,f in zip(c,F))),fixed_reaction=None,force_supported_area=None,unique_contact_points=None)
  rows=source/'contact_rows.csv'
  if rows.exists():
   records=list(csv.DictReader(rows.open()));valid=all(None not in r and r.get('nodal_support') is not None for r in records)
   info[tag]['row_journal_status']='PASS_FORMAT' if valid else 'FAIL_FORMAT'
   info[tag]['load_bearing_rows']=len(records) if valid else None
  for file in ('journal.csv','contact.csv','scene.scn'):inputs[str((source/file).relative_to(ROOT))]=sha(source/file)
 comparisons={};ramp=float(config['control']['rampTime']);release=float(config['control']['releaseBegin'])
 for i,tag in enumerate(a.cases):
  for other in a.cases[i+1:]:
   x,y=data[tag],data[other];phases={}
   end=min(x['time'][-1],y['time'][-1]);windows=[('all',0,end),('ramp',0,ramp),('hold',ramp,release),('release',release,end)] if end>.2+1e-10 else [('all',0,end),('pre_contact',0,.09),('onset',.09,.12),('sustained',.12,end)]
   for label,lo,hi in windows:
    hi=min(hi,end)
    if hi<=lo:continue # A single boundary output is not a hold/release interval.
    mask=(x['time']>=lo-1e-10)&(x['time']<=hi+1e-10);metrics={}
    if np.count_nonzero(mask)<2:continue
    for key in x:
     if key=='time':continue
     fine=np.interp(x['time'][mask],y['time'],y[key]);error=float(max(abs(x[key][mask]-fine)));scale=float(max(abs(fine)));relative=error/scale if scale else (0 if error==0 else None);metrics[key]=dict(absolute=error,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
    phases[label]=metrics
   comparisons[tag+':'+other]=phases
 status='NOT RUN' if len(a.cases)<2 else 'PASS' if all(m['status']=='PASS' for phases in comparisons.values() for metrics in phases.values() for m in metrics.values()) else 'FAIL'
 write_json(out/'summary.json',dict(time_status=status,threshold=.001,script_sha256=sha(__file__),scope='frictionless fixed-object cycle;NOT free-object grasp or complete energy',physical=config,inputs=inputs,cases=info,comparisons=comparisons,force_balance='BLOCKED:fixed reaction not measured',energy='BLOCKED',grasp='NOT RUN'));print(json.dumps(dict(time_status=status,cases=info)))
if __name__=='__main__':main()
