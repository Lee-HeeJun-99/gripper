"""Controlled SAME-BINARY event-state contrast,not a time convergence test."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--dense',required=True);p.add_argument('--reintegrated',required=True);p.add_argument('--dense-residual',required=True);p.add_argument('--reintegrated-residual',required=True);a=p.parse_args()
 folders=[ROOT/'results'/('autonomous_film_'+s) for s in (a.dense,a.reintegrated)];meta=[json.loads((s/'identity.json').read_text()) for s in folders]
 if any(json.loads((s/'summary.json').read_text())['status']!='PASS' for s in folders):raise ValueError('completed actual controlled pair required')
 if meta[0]['binary_sha256']!=meta[1]['binary_sha256'] or meta[0].get('reintegrated_birth') is not False or meta[1].get('reintegrated_birth') is not True:raise ValueError('same binary and one explicit event policy switch required')
 def canonical(node):return (node.tag,tuple(sorted((k,v) for k,v in node.attrib.items() if k not in ('filename','displacementFilename','reintegratedEvent'))),tuple(canonical(c) for c in node))
 if canonical(ET.parse(folders[0]/'scene.scn').getroot())!=canonical(ET.parse(folders[1]/'scene.scn').getroot()):raise ValueError('more than event-policy/output paths changed')
 records=[];evidence={}
 for case,name in zip((a.dense,a.reintegrated),(a.dense_residual,a.reintegrated_residual)):
  folder=ROOT/'results'/('autonomous_film_'+name);result=json.loads((folder/'summary.json').read_text())
  if result['status']!='PASS' or result['case']!=case:raise ValueError('completed matched residual measurement required')
  records.append({k:float(v) if v!='null' else None for k,v in result['metrics'].items()});evidence[name]=sha(folder/'summary.json')
 residual0=records[0]['partial_midpoint_momentum_residual'];residual1=records[1]['partial_midpoint_momentum_residual']
 pre=[min((r for r in csv.DictReader((folder/'coupled.event_states.csv').open()) if r['stage']=='pre'),key=lambda r:float(r['time'])) for folder in folders]
 differences={key:float(np.linalg.norm(np.fromstring(pre[0][key],sep=' ')-np.fromstring(pre[1][key],sep=' '))) for key in ('local_velocity','body_velocity','body_omega','local_displacement','body_center')}
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 record=dict(status='PASS' if residual1<residual0 else 'FAIL',scope='same-binary ONE numerical event policy changed;partial midpoint consistency improvement only;NOT global momentum/time/energy/grasp certificate',cases=[a.dense,a.reintegrated],only_changed_input='reintegratedEvent',scene_inputs_identical_except_policy_and_output=True,residual_records=records,observed_residual_ratio=residual0/residual1 if residual1 else None,pre_state_differences=differences,residual_evidence=evidence,actual_evidence={str(folder.name):{name:sha(folder/name) for name in ('identity.json','scene.scn','coupled.event_states.csv')} for folder in folders},interpretation='old dense extension is not designed to solve the partial midpoint equation;this is not a claim that its instantaneous impact momentum balance fails')
 write_json(out/'summary.json',record)
 print(json.dumps(dict(status='PASS' if residual1<residual0 else 'FAIL',dense_residual=residual0,reintegrated_residual=residual1,observed_ratio=residual0/residual1 if residual1 else None)))
if __name__=='__main__':main()
