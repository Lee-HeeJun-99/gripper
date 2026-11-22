"""Matched actual scenes plus Native outcomes;not a new contact/time certification."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def normalized_scene(file,strip_solver_policy=False):
 root=ET.parse(file).getroot()
 for item in root.iter():
  if item.get('filename'):item.set('filename',Path(item.get('filename')).name)
  if item.tag in ('LocalMinDistance','MinProximityIntersection'):item.tag='INTERSECTOR_COMPARISON_SLOT'
  if strip_solver_policy and item.tag=='BlockGaussSeidelConstraintSolver':
   for k in ('scaleTolerance','allVerified'):item.attrib.pop(k,None)
 return ET.tostring(root)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cases=['product_root_native810','product_root_native_strict815','product_root_intersection817'];folders=[BASE/'results'/c for c in cases];inputs=[Path(__file__)];records=[]
 same_physical=all(normalized_scene(folders[0]/'scene.scn',True)==normalized_scene(f/'scene.scn',True) for f in folders[1:]);only_intersector=normalized_scene(folders[1]/'scene.scn')==normalized_scene(folders[2]/'scene.scn')
 if not same_physical or not only_intersector:raise ValueError('scene contract mismatch;cannot claim isolatedpolicyintervention')
 for case,folder in zip(cases,folders):
  summary=json.loads((folder/'summary.json').read_text());rows=list(csv.DictReader((folder/'wheel.csv').open()));finite=[np.isfinite(np.fromstring(r['rigid_q']+' '+r['rigid_v'],sep=' ')).all() for r in rows];inputs.extend([folder/'summary.json',folder/'scene.scn',folder/'wheel.csv']);records.append(dict(case=case,rows=len(rows),nonfinite_rows=int(len(rows)-sum(finite)),final_angular_speed_rad_s=float(np.linalg.norm(np.fromstring(rows[-1]['rigid_v'],sep=' ')[3:])) if finite[-1] else None,recorded_runtime_s=summary.get('runtime_s'),status=summary['status']))
 ratio=records[2]['recorded_runtime_s']/records[0]['recorded_runtime_s'];d=dict(status='MATCHED_NATIVE_POLICY_COUPON_COMPARISON_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x):sha(x) for x in inputs},same_physical_scene_after_explicit_policy_normalization=same_physical,strict_to_alternative_only_intersector_class_changed=only_intersector,records=records,alternative_vs_default_actual_runtime_ratio=ratio,scope='ExactXMLphysicalinputidentity afteronlyfilename/solverpolicy/intersector normalization. Allfinitecollisionmodelsretained. MinProximityiscontact-policyalternativewithmorecandidates/runtime,notprovedsamecontinuouscontactsolution. No dt/time/energy/mesh/productPASS;strictNaNFAILpreserved.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
