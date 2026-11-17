"""New assessment of preserved SOFA Raw against public-mass-matched FEM.

Never modifies prior FAIL summaries. Absolute API gate remains1e-12.
"""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--actual',required=True);p.add_argument('--reference',required=True);p.add_argument('--mass-case',required=True);a=p.parse_args();actual,reference,mass=[ROOT/'results'/('autonomous_film_'+x) for x in (a.actual,a.reference,a.mass_case)];am=json.loads((actual/'identity.json').read_text());ass=json.loads((actual/'summary.json').read_text());rm=json.loads((reference/'summary.json').read_text());mm=json.loads((mass/'identity.json').read_text())
 if rm['status']!='PASS' or json.loads((mass/'summary.json').read_text())['status']!='PASS' or not mm.get('mass_journal') or rm.get('public_mass_identity',{}).get('sha256')!=sha(mass/'public_mass.txt'):raise ValueError('completed reference must use actual API mass file exactly')
 if ass['process']['exit_code']!=0 or ass['sofa_error_count'] or ass['minimum_gap']< -1e-10:raise ValueError('cannot override actual runtime/physical failure')
 if am['steps']!=rm['steps'] or am['duration']!=rm['duration'] or am['tension_per_rail_N']!=rm['maximum_tension_N'] or rm['initial']!='REST,already touching,externalFz=-.001N' or am['sdk_library_paths']!=mm['sdk_library_paths']:raise ValueError('physical/reference/SDK mismatch')
 for k,v in am['sources'].items():
  if k.endswith('.h') and (rm['sources'].get(k)!=v or mm['sources'].get(k)!=v):raise ValueError('compiled physics kernel mismatch:'+k)
 def mass_values(path):
  root=ET.parse(path/'scene.scn');arrays=[np.fromstring(root.find('Node[@name="finger'+str(f)+'"]//DiagonalMass').get('vertexMass'),sep=' ') for f in range(3)];arrays.append(np.fromstring(root.find('Node[@name="free_object"]//UniformMass').get('vertexMass'),sep=' '));return arrays
 if any(not np.array_equal(x,y) for x,y in zip(mass_values(actual),mass_values(mass))):raise ValueError('recorded mass source XML differs from actual subject')
 rows=list(csv.DictReader((actual/'three.states.csv').open()));ref=list(csv.DictReader((reference/'states.csv').open()))
 if len(rows)!=am['steps'] or len(ref)!=am['steps'] or max(abs(float(x['time'])-float(y['time'])) for x,y in zip(rows,ref))>1e-12:raise ValueError('incomplete or misaligned physical times')
 errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,ref)) for k in ('q','v')}
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if max(errors.values())<=1e-12 else 'FAIL',scope='preserved actual Raw vs exact-public-mass independent FEM;NOT full time/energy/grasp certification',actual=a.actual,reference=a.reference,mass_case=a.mass_case,absolute_api_gate=1e-12,errors=errors,prior_status=ass['status'],prior_errors=ass.get('independent_state_errors'),prior_fail_is_preserved=True,source_commit=am['source_commit'],raw_hashes={a.actual:{f:sha(actual/f) for f in ('identity.json','summary.json','three.states.csv','three.rows.csv')},a.reference:{f:sha(reference/f) for f in ('summary.json','states.csv','public_mass.txt')},a.mass_case:{f:sha(mass/f) for f in ('identity.json','summary.json','public_mass.txt')}},note='reference inputs corrected to actual public masses,not a SOFA force/state modification or tolerance relaxation')
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
