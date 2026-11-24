"""Read-only preservation/queue/library audit, never regenerates physics."""
import argparse,collections,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE.parent/'tools'))
from film_guarded_process import guarded
from current_wire_manifest import digest

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);old=json.loads(subprocess.check_output(['git','show','05252d7:product_prototype/config/research_queue.json'],cwd=BASE.parent));current=json.loads((BASE/'config/research_queue.json').read_text());byid={t['id']:t for t in current['tasks']};changed=[t['id'] for t in old['tasks'] if byid.get(t['id'])!=t];assert not changed
 manifests=['overnight_integrity1709','overnight_final_index1713','clutch_integrity1716','clutch_active_integrity1719','yoke_pilot_integrity1727','yoke_union_integrity1735','yoke_prefix_integrity1744','yoke_full_integrity1755','prismatic_integrity1759'];verified=0;bad=[];sdk_changes=[]
 for case in manifests:
  d=json.loads((BASE/'results'/case/'summary.json').read_text())
  for r in d['records']:
   f=BASE.parent/r['path'];verified+=1
   if not f.is_file() or f.stat().st_size!=r['bytes'] or digest(f)!=r['sha256']:bad.append(r['path'])
  for f,h in d.get('installed_reference_sha256',{}).items():
   if digest(Path(f))!=h:sdk_changes.append(f)
 oldchanges=subprocess.check_output(['git','diff','--name-status','05252d7','--','product_prototype/results'],cwd=BASE.parent,text=True).splitlines();modified_old=[x for x in oldchanges if not x.startswith('A\t')];assert not modified_old
 actual_libraries={}
 for f in (BASE/'results').glob('*/scene.scn'):
  if not any(f.parent.name.endswith(str(n)) for n in range(1714,1769)):continue
  for node in ET.parse(f).getroot().iter('RequiredPlugin'):
   path=node.get('pluginName','')
   if path.startswith('/'):actual_libraries[path]=digest(Path(path))
 baseline=json.loads((BASE/'results/capillary_hold1700/preflight.json').read_text())['binary_hashes'];baseline_binary_changes=[f for f,h in baseline.items() if digest(Path(f))!=h]
 tests=guarded(['/home/ubuntu/miniconda3/envs/robot_ws/bin/python',BASE/'sofa/test_sector_yoke_contracts.py'],out/'regression',60);assert tests['exit_code']==0
 upstream='refs/remotes/origin/development/regrip-autonomous-research';cached=subprocess.check_output(['git','rev-parse',upstream],cwd=BASE.parent,text=True).strip();ancestor=subprocess.run(['git','merge-base','--is-ancestor',upstream,'HEAD'],cwd=BASE.parent).returncode==0
 mass_source=BASE/'results/yoke_hold_diagnostic1741';scene=ET.parse(mass_source/'scene.scn').getroot();queried=json.loads((mass_source/'guide_frames0.csv.mass.json').read_text())['elements'][5]['mass_kg'];configured=float(scene.find("Node[@name='guides0']/UniformMass[@name='yokeMass']").get('vertexMass').split()[0]);mass_warning=dict(case=mass_source.name,public_first_component_mass_query_at_index5_kg=queried,configured_composite_body5_mass_kg=configured,scope='Frozen NativeRigidJournal calls context getMass() (ONE component). Stock UniformMass.getElementMass ignores index; this public API file is NOT the sum of indexed components. Preserve Raw; use independent actual acceleration/tensor1720/1729 contracts, not this first-component query, for assembly evidence. No claimed full deformed-system mass validation.')
 d=dict(status='PASS_SESSION_PRESERVATION_AND_HELPER_TESTS_ONLY' if not bad and not baseline_binary_changes and not sdk_changes and ancestor else 'FAIL_SESSION_AUDIT',source_commit_before_save=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),cached_remote_commit=cached,network_remote_contacted=False,cached_remote_is_ancestor=ancestor,original_queue_tasks=len(old['tasks']),original_queue_entries_changed=changed,queue_state_counts=dict(collections.Counter(t['status'] for t in current['tasks'])),running_tasks=[t['id'] for t in current['tasks'] if t['status']=='RUNNING'],manifest_records_verified=verified,manifest_files_changed=bad,original_tracked_result_changes=modified_old,original_compiled_plugin_changes=baseline_binary_changes,installed_SDK_reference_changes=sorted(set(sdk_changes)),public_mass_query_scope_warning=mass_warning,current_actual_plugin_sha256=actual_libraries,helper_regression=tests,source_sha256=digest(Path(__file__)),scope='Read-only cryptographic preservation and seven helper tests. Original102queue entries byte-equivalent as JSON; old manifests/Raw hashes rechecked without regenerating them. Installed libraries hashed at audit time, baseline compiled identities crosschecked; not an external backup or physical PASS. Cached upstream only, no fetch/push/rewrite. Current1768seed remains NOT_NATIVE_READY; final grasp goal FAIL.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('current_actual_plugin_sha256','helper_regression')},indent=2))
if __name__=='__main__':main()
