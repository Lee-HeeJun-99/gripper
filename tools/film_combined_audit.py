"""Independent observations of actual combined event/stage ownership and FEM."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_audit import gaps
from film_coupled_row_audit import closest
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--independent-clock-reference');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text())
 if json.loads((src/'summary.json').read_text())['status']!='PASS':raise ValueError('completed actual combined experiment required')
 tree=ET.parse(src/'scene.scn')
 if tree.find('CoupledEventLobattoODE') is None:raise ValueError('actual combined owner required,not changed labels')
 if not meta.get('combined_contact'):raise ValueError('combined numerical policy identity missing')
 ref=ROOT/'results'/('autonomous_film_'+meta['reference']);rs=json.loads((ref/'summary.json').read_text())
 if rs['status']!='PASS':raise ValueError('complete independent combined reference required')
 if meta['source_case']!=rs['actual_pre_source'] or meta['duration']!=rs['duration'] or meta['reference_input_sha256']!=rs['input_sha256']:raise ValueError('independent initial-state provenance/window mismatch')
 for name,digest in rs['sources'].items():
  if name.endswith('.h') and meta['sources'].get(name)!=digest:raise ValueError('compiled combined reference kernel drift:'+name)
 actual=list(csv.DictReader((src/'coupled.states.csv').open()));film=list(csv.DictReader((src/'film.csv').open()));stages=list(csv.DictReader((src/'coupled.stages.csv').open()));rows=list(csv.DictReader((src/'coupled.rows.csv').open()));snapshots=list(csv.DictReader((src/'coupled.event_states.csv').open()));events=list(csv.DictReader((src/'coupled.events.csv').open()));reference=next(r for r in csv.DictReader((ref/'states.csv').open()) if int(r['steps'])==meta['steps'])
 if a.independent_clock_reference:
  clock=ROOT/'results'/('autonomous_film_'+a.independent_clock_reference);cm=json.loads((clock/'summary.json').read_text())
  if cm['status']!='PASS' or cm['case']!=a.case or not cm.get('accumulated_clock') or cm.get('formula_clock'):raise ValueError('completed INDEPENDENT accumulated clock reference required;observed clocks not substituted')
  for name,digest in meta['sources'].items():
   if name.endswith('.h') and cm['sources'].get(name)!=digest:raise ValueError('independent archived-kernel clock reference drift:'+name)
  clock_states=list(csv.DictReader((clock/'states.csv').open()))
  if len(clock_states)!=len(actual):raise ValueError('independent clock reference incomplete')
  reference=clock_states[-1]
 topology=tree.find('.//TriangleSetTopologyContainer');rest=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3);nx=int(tree.find('.//FilmRailTendon').get('nx'));index=np.full(rest.size,-1,dtype=int);weight=np.ones(rest.size);nf=0
 for offset,ny in ((0,5),(5*nx,3),(8*nx,3)):
  for i in range(1,nx):
   for j in range(ny):
    for d in range(3):
     if i!=1 or d!=2:index[3*(offset+i*ny+j)+d]=nf;nf+=1
  for j in range(ny):index[3*(offset+ny+j)+2]=index[3*(offset+2*ny+j)+2];weight[3*(offset+ny+j)+2]=.25
 error=dict(world=0.,shell=0.,attachment=0.,K_film=0.,control=0.,row_J=0.,row_point=0.,row_normal=0.,stage_impulse=0.,stage_velocity=0.,stage_momentum=0.);minimum=float('inf');minimumStage=float('inf')
 for s,f in zip(actual,film):
  world=rest+np.fromstring(s['local_displacement'],sep=' ').reshape(-1,3);minimum=min(minimum,float(np.min(gaps(world[tri],np.fromstring(s['body_center'],sep=' '),meta['buffer_radius']))));error['world']=max(error['world'],float(np.max(abs(world-np.fromstring(f['x'],sep=' ').reshape(-1,3)))))
  for key,col in (('shell','U_shell'),('attachment','U_attachment'),('K_film','K')):error[key]=max(error[key],abs(float(s['K_film' if key=='K_film' else col])-float(f[col])))
  error['control']=max(error['control'],abs(float(s['end_tension'])-float(f['T_per_rail'])))
 seen=set()
 for row in rows:
  key=(row['step'],row['stage'],row['row'])
  if key in seen:raise ValueError('duplicate owned row')
  seen.add(key)
  if row['stage']=='0':
   event=next(s for s in snapshots if s['stage']=='pre' and s['time']==row['time']);q=np.fromstring(event['local_displacement'],sep=' ').reshape(-1,3);center=np.fromstring(event['body_center'],sep=' ')
  elif row['stage']=='1':
   macro_start=meta['start_time']+(int(row['step'])-1)*meta['duration']/meta['steps'];stage=next(s for s in stages if s['stage_time']==row['time'] and s['triangle']==row['triangle'] and abs(float(s['macro_start'])-macro_start)<1e-12);packed=np.fromstring(stage['q'],sep=' ');q=np.zeros_like(rest)
   for k,free in enumerate(index):
    if free>=0:q.flat[k]=weight[k]*packed[free]
   center=packed[nf:nf+3];expected=float(stage['normal_force'])*float(stage['weighted_time']);error['stage_impulse']=max(error['stage_impulse'],abs(expected-float(row['impulse'])));error['stage_velocity']=max(error['stage_velocity'],abs(float(stage['normal_velocity'])));error['stage_momentum']=max(error['stage_momentum'],abs(float(stage['momentum_residual'])))
   if float(stage['normal_force'])<0:raise ValueError('negative actual stage force')
   minimumStage=min(minimumStage,float(np.min(gaps((rest+q)[tri],center,meta['buffer_radius']))))
  else:raise ValueError('unused midpoint projection incorrectly applied to combined owner')
  ids=tri[int(row['triangle'])];point,bary,normal=closest((rest+q)[ids],center);full=np.zeros_like(rest)
  for k,node in enumerate(ids):full[node]+=bary[k]*normal
  expected=np.zeros(nf+6)
  for k,free in enumerate(index):
   if free>=0:expected[free]+=weight[k]*full.flat[k]
  expected[nf:nf+3]=-normal;error['row_J']=max(error['row_J'],float(np.max(abs(expected-np.fromstring(row['jacobian'],sep=' ')))));error['row_point']=max(error['row_point'],float(np.linalg.norm(point-np.array([float(row[k]) for k in ('px','py','pz')]))));error['row_normal']=max(error['row_normal'],float(np.linalg.norm(normal-np.array([float(row[k]) for k in ('nx','ny','nz')]))))
 last=actual[-1];fem_errors={k:float(np.max(abs(np.fromstring(last[k],sep=' ')-np.fromstring(reference[k],sep=' ')))) for k in ('local_displacement','local_velocity','body_center','body_velocity')};impacts={k:max(abs(float(r[k])) for r in events) if events else None for k in ('momentum_residual','linear_balance','angular_balance')}
 valid=len(actual)==len(film)==meta['steps'] and minimum>=-1e-10 and minimumStage>=-1e-10 and all(v<1e-10 for v in error.values()) and all(v<1e-12 for v in fem_errors.values()) and events and all(v is not None and v<1e-12 for v in impacts.values())
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,3,figsize=(13,4));axes[0].plot([float(s['time']) for s in actual],[float(s['minimum_gap']) for s in actual],'.-');axes[0].set_ylabel('Whole accepted gap [mm]');axes[1].plot([float(s['stage_time']) for s in stages],[float(s['normal_force']) for s in stages],'.-');axes[1].set_ylabel('Continuous stage force [N]');axes[2].bar(['pre','post'],[float(events[0]['normal_before']),float(events[0]['normal_after'])]);axes[2].set_ylabel('Actual event normal velocity [mm/s]')
 for ax in axes[:2]:ax.set_xlabel('Actual physical time [s]');ax.ticklabel_format(useOffset=False,axis='x');ax.tick_params(axis='x',rotation=25);ax.grid()
 fig.suptitle('Actual coupled C2 event+Lobatto;ISOLATED coupon,not full C2/grasp');fig.tight_layout();fig.savefig(out/'combined_actual.png',dpi=170);plt.close(fig)
 result=dict(status='PASS' if valid else 'FAIL',scope='independent actual combined state/whole endpoint/used-stage/FEM/instant momentum audit;NOT fulltime/energy/grasp',case=a.case,errors=error,fem_errors=fem_errors,minimum_independent_gap=minimum,impact_checks=impacts,atomic_impulse_Ns=sum(float(r['impulse']) for r in events),rows=len(rows),source_hashes={f:sha(src/f) for f in ('identity.json','scene.scn','coupled.states.csv','coupled.rows.csv','coupled.stages.csv','coupled.event_states.csv','coupled.events.csv')},not_measured=['synchronized full damping/external/tendon work','whole-step angular momentum','global earliest endpoint-family CCD','release/reimpact','friction/grasp'])
 result['minimum_whole_stage_gap']=minimumStage if stages else None
 result['independent_clock_reference']=a.independent_clock_reference
 result['reference_protocol']='independent start+=dt,archived same kernels' if a.independent_clock_reference else 'original reference protocol;inspect its clock declaration'
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],errors=error,fem_errors=fem_errors,minimum_gap=minimum,minimum_stage_gap=result['minimum_whole_stage_gap'])))
if __name__=='__main__':main()
