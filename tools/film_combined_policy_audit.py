"""Actual parsed Data and passive policy-journal purity across binary versions."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--dense',required=True);p.add_argument('--sparse',required=True);p.add_argument('--dense-before',required=True);p.add_argument('--sparse-before',required=True);a=p.parse_args();records=[];binary=None
 names=('coupled.states.csv','coupled.events.csv','coupled.rows.csv','coupled.event_states.csv','coupled.stages.csv','coupled.work.csv','coupled.cost.csv','film.csv','displacement.csv')
 for after,before,flag in ((a.dense,a.dense_before,False),(a.sparse,a.sparse_before,True)):
  left=ROOT/'results'/('autonomous_film_'+before);right=ROOT/'results'/('autonomous_film_'+after);meta=json.loads((right/'identity.json').read_text());prior=json.loads((left/'identity.json').read_text())
  if any(json.loads((d/'summary.json').read_text())['status']!='PASS' for d in (left,right)):raise ValueError('completed actual policy on/off observations required')
  if binary is None:binary=meta['binary_sha256']
  if binary!=meta['binary_sha256']:raise ValueError('actual dense/sparse policy must share binary')
  for key in ('start_time','duration','steps','initial_displacement','initial_velocity','initial_body_center','initial_body_velocity','source_case'):
   if meta[key]!=prior[key]:raise ValueError('passive experiment input differs:'+key)
  for name,digest in prior['sources'].items():
   if name.endswith('.h') and meta['sources'].get(name)!=digest:raise ValueError('policy changed physical header:'+name)
  policy=next(csv.DictReader((right/'coupled.policy.csv').open()));scene=ET.parse(right/'scene.scn');owner=scene.find('CoupledEventLobattoODE');checks={name:sha(left/name)==sha(right/name) for name in names};parsed=policy['component']=='CoupledEventLobattoODE' and bool(int(policy['sparse_stage']))==flag==meta['sparse_stage'] and float(policy['start_time'])==meta['start_time'] and float(policy['maximum_duration'])==meta['duration'] and int(owner.get('sparseStage'))==int(flag)
  records.append(dict(case=after,before=before,parsed_runtime=policy,parsed_matches=parsed,physical_csv_exact=checks,policy_sha256=sha(right/'coupled.policy.csv')))
 status='PASS' if all(r['parsed_matches'] and all(r['physical_csv_exact'].values()) for r in records) else 'FAIL';out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');write_json(out/'summary.json',dict(status=status,scope='actual SOFA Data parsing and passive journal exactness;NOT physical/time certification',binary=binary,records=records));print(json.dumps(dict(status=status,all_nine_csv_exact=all(all(r['physical_csv_exact'].values()) for r in records))))
if __name__=='__main__':main()
