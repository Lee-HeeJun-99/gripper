"""Same-binary sparse/dense A/B:physical outputs AND measured child wall time."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--dense',required=True);p.add_argument('--sparse',required=True);a=p.parse_args();folders=[ROOT/'results'/('autonomous_film_'+n) for n in (a.dense,a.sparse)];meta=[json.loads((f/'identity.json').read_text()) for f in folders];state=[json.loads((f/'summary.json').read_text()) for f in folders]
 if any(s['status']!='PASS' for s in state) or meta[0]['sparse_stage'] or not meta[1]['sparse_stage']:raise ValueError('completed explicit dense0/sparse1 trials required')
 for k in ('binary_sha256','sources','duration','steps','start_time','initial_displacement','initial_velocity','initial_body_center','initial_body_velocity','initial_body_quaternion','body_mass','inertia_per_mass','rayleigh_mass','source_case'):
  if meta[0][k]!=meta[1][k]:raise ValueError('backend contrast physical/binary input differs:'+k)
 def canonical(folder):
  tree=ET.parse(folder/'scene.scn');tree.find('CoupledEventLobattoODE').attrib.pop('sparseStage')
  return [(node.tag,sorted((k,v.replace(str(folder),'$OUT')) for k,v in node.attrib.items())) for node in tree.iter()]
 if canonical(folders[0])!=canonical(folders[1]):raise ValueError('XML differs beyond solver flag/output directory')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records={};physical=True
 files=('coupled.states.csv','coupled.events.csv','coupled.rows.csv','coupled.event_states.csv','coupled.stages.csv','coupled.work.csv','film.csv','displacement.csv')
 for name in files:
  left,right=[list(csv.DictReader((f/name).open())) for f in folders];checks={};valid=len(left)==len(right)
  if valid:
   for key in left[0] if left else []:
    maximum=0.;exact=True
    for x,y in zip(left,right):
     if x[key] in ('pre','post','null') or y[key] in ('pre','post','null'):exact=exact and x[key]==y[key];continue
     u=np.fromstring(x[key],sep=' ');v=np.fromstring(y[key],sep=' ')
     if u.shape!=v.shape or not u.size or not np.isfinite(u).all() or not np.isfinite(v).all():exact=False;continue
     maximum=max(maximum,float(np.max(abs(u-v))))
    tolerance=1e-18 if any(s in key.lower() for s in ('impulse','energy','loss','u_shell','u_attachment','k_film','k_linear','k_rotation','work')) or key in ('U_shell','U_attachment','K') else 1e-12
    if key in ('step','stage','row','triangle','feature','event','sustained'):tolerance=0.
    checks[key]=dict(maximum_absolute_error=maximum,tolerance=tolerance,status='PASS' if exact and maximum<=tolerance else 'FAIL');valid=valid and checks[key]['status']=='PASS'
  records[name]=dict(status='PASS' if valid else 'FAIL',row_counts=[len(left),len(right)],columns=checks);physical=physical and valid
 dense,sparse=[s['process']['runtime_s'] for s in state];improved=sparse<dense;result=dict(status='PASS' if physical and improved else 'FAIL',scope='same-binary explicit solver-only accuracy and measured wall-time pair;NOT statistical benchmark/full physics qualification',dense=a.dense,sparse=a.sparse,physical_equivalence=physical,runtime_improved=improved,dense_s=dense,sparse_s=sparse,observed_speedup=dense/sparse,checks=records,source_hashes={str(f.relative_to(ROOT)):sha(f) for folder in folders for f in (folder/'identity.json',folder/'summary.json',folder/'scene.scn')});write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('checks','source_hashes')}))
if __name__=='__main__':main()
