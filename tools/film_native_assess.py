"""Fixed sphere actual impulse, stage and time checks, not a grasp certificate."""
import argparse,csv,json
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);data={};inputs={};cases={}
 for name in a.cases:
  directory=ROOT/'results'/('autonomous_film_'+name)
  if json.loads((directory/'summary.json').read_text())['status']!='PASS':raise RuntimeError('execution failed')
  for file in ('contact.csv','journal.csv'):inputs[str((directory/'1'/file).relative_to(ROOT))]=sha(directory/'1'/file)
  c=list(csv.DictReader((directory/'1/contact.csv').open()));j=list(csv.DictReader((directory/'1/journal.csv').open()));t=np.array([float(s['time']) for s in c]);F=np.array([np.fromstring(s['body_force'],sep=' ') for s in c]);normal=np.linalg.norm(F,axis=1);nonzero=np.flatnonzero(normal>0)
  if any(int(s['unmatched_jacobian_rows']) for s in c):raise RuntimeError('incomplete constraint pullback')
  moments={key:float(max(np.linalg.norm(np.fromstring(s[key],sep=' ')-np.cross([95,12,-8.2],f)) for s,f in zip(c,F))) for key in ('body_moment_begin','body_moment_free','body_moment_accepted')}
  cases[name]=dict(first_nonzero_force_time=float(t[nonzero[0]]) if len(nonzero) else None,peak_force=float(max(normal)),begin_geometry_radial_moment_defect=moments,minimum_vertex_gap_mm=min(float(s['min_vertex_gap']) for s in c),fixed_sphere_reaction=None,fixed_reaction_reason='FixedProjectiveConstraint removes sphere Jacobian;zero projected column is NOT a measured zero reaction',active_points=None,contact_area=None)
  dt=np.array([float(s['dt']) for s in c]);impulse=np.cumsum(F*dt[:,None],axis=0)
  cases[name]['total_vector_impulse']=impulse[-1].tolist()
  data[name]={'time':t,'normal_force':normal,'scalar_normal_impulse':np.cumsum(normal*dt),'vertical_vector_impulse':impulse[:,2],**{key:np.array([float(s[key]) for s in j]) for key in ('skin_tip_z','U_shell','U_attachment','K','tendon_work')}}
 comparisons={};phases={}
 for i,name in enumerate(a.cases):
  for other in a.cases[i+1:]:
   x,y=data[name],data[other];metrics={}
   for key in x:
    if key=='time':continue
    fine=np.interp(x['time'],y['time'],y[key]);absolute=float(max(abs(x[key]-fine)));scale=float(max(abs(fine)));relative=absolute/scale if scale else (0 if not absolute else None);metrics[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
   comparisons[name+':'+other]=metrics
   phases[name+':'+other]={}
   for lo,hi in ((0,.23),(.23,.27),(.27,.5)):
    mask=(x['time']>=lo-1e-12)&(x['time']<=hi+1e-12);m={}
    for key in ('normal_force','skin_tip_z','U_attachment','vertical_vector_impulse'):
     first=x[key][mask];second=np.interp(x['time'][mask],y['time'],y[key]);absolute=float(max(abs(first-second)));scale=float(max(abs(second)));m[key]=dict(absolute=absolute,relative=absolute/scale if scale else (0 if absolute==0 else None))
    phases[name+':'+other][f'{lo}:{hi}']=m
 status='PASS' if all(v['status']=='PASS' for d in comparisons.values() for v in d.values()) else 'FAIL'
 write_json(out/'summary.json',dict(time_status=status,scope='installed SOFA frictionless fixed-sphere native contact;not SDF compliance or free-object grasp',inputs=inputs,cases=cases,comparisons=comparisons,phases=phases,force_balance='BLOCKED:fixed reaction unavailable',global_energy='BLOCKED',wrapping='NOT QUALIFIED',free_object_grasp='NOT RUN'))
 print(json.dumps(dict(time_status=status,cases=cases),indent=2))
if __name__=='__main__':main()
