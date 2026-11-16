"""Faceted object collision mesh study only; film/time certification is separate."""
import argparse,csv,json
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);data={};inputs={};identities={};parameters=None
 for tag in a.cases:
  source=ROOT/'results'/('autonomous_film_'+tag);summary=json.loads((source/'summary.json').read_text());identity=json.loads((source/'identity.json').read_text())
  if summary['status']!='PASS':raise RuntimeError('incomplete physical trial')
  field=__import__('xml.etree.ElementTree',fromlist=['parse']).parse(source/'1/scene.scn').find("Node[@name='assembly']/FilmRailTendon");settings={k:v for k,v in field.attrib.items() if k not in ('filename','costProfileFilename')};settings.update(core=identity['core_sha256'],assembly=identity['assembly_sha256'],center=identity['sphere_center'])
  if parameters is not None and settings!=parameters:raise RuntimeError('different assembly/material/control')
  parameters=settings;r=list(csv.DictReader((source/'1/journal.csv').open()));c=list(csv.DictReader((source/'1/contact.csv').open()));t=np.array([float(x['time']) for x in r]);F=np.array([np.fromstring(x['body_force'],sep=' ') for x in c]);norm=np.linalg.norm(F,axis=1);dt=np.array([float(x['dt']) for x in c]);data[tag]=dict(time=t,contact_force=norm,normal_impulse=np.cumsum(norm*dt),**{k:np.array([float(x[k]) for x in r]) for k in ('skin_tip_z','U_shell','U_attachment','K','tendon_work')});identities[tag]=dict(segments=identity.get('cylinder_segments',64),rows=len(r))
  for f in ('journal.csv','contact.csv','scene.scn'):inputs[str((source/'1'/f).relative_to(ROOT))]=sha(source/'1'/f)
 pairs={}
 for i,tag in enumerate(a.cases):
  for other in a.cases[i+1:]:
   x,y=data[tag],data[other]
   if x['time'].shape!=y['time'].shape or not np.array_equal(x['time'],y['time']):raise RuntimeError('collision mesh must be isolated at identical physical time samples')
   metrics={}
   for key in x:
    if key=='time':continue
    absolute=float(max(abs(x[key]-y[key])));scale=float(max(abs(y[key])));relative=absolute/scale if scale else (0 if absolute==0 else None);metrics[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.01 else 'FAIL')
   pairs[tag+':'+other]=metrics
 status='PASS' if all(m['status']=='PASS' for metrics in pairs.values() for m in metrics.values()) else 'FAIL'
 write_json(out/'summary.json',dict(status=status,scope='object collision mesh only,not film mesh/time/contact-area or grasp certification',threshold=.01,cases=identities,pairs=pairs,inputs=inputs,physical=parameters,film_mesh='NOT RUN',time_convergence='NOT RUN',grasp='NOT RUN'));print(json.dumps(dict(status=status,pairs=pairs)))
if __name__=='__main__':main()
