"""Bounded first-system observer of failed finite-layer graph;no purity claim.

Reuses frozen1242 binary;partial data is pre-solve diagnosis,not accepted state.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_contact_layer_pilot1337';meta=json.loads((BASE/'results/contact_provenance_build1242/summary.json').read_text());binary=BASE/'cad/contact_provenance_build1242/libReGripContactProvenance.so';assert sha(binary)==meta['binary_sha256'];tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(root,'ReGripContactProvenance',narrow='@nativeNarrow',filename=str(out/'provenance'),startTime='0',endTime='.00001')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',str(out/'scene.scn')];pre=dict(command=cmd,scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),observer_binary_sha256=sha(binary),observer_compiled_source_sha256=meta['compiled_source_sha256'],child_limit_s=15,memory_GiB=4,expected_scope='Read-only first BuildConstraintSystemEndEvent data;Native may be stopped before first accepted state. Not observer purity or successful run.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',15);f=out/'provenance.features.csv';rows=list(csv.DictReader(f.open())) if f.exists() else [];records=[]
 for r in rows:
  normal=np.fromstring(r['normal'],sep=' ');p0=np.fromstring(r['point0'],sep=' ');p1=np.fromstring(r['point1'],sep=' ');records.append(dict(model0=r['model0'],model1=r['model1'],finite=bool(np.isfinite(np.r_[normal,p0,p1]).all()),normal_norm=float(np.linalg.norm(normal)),point_distance_m=float(np.linalg.norm(p0-p1)),previous_time_s=float(r['previous_time_s'])))
 d=dict(status='FIRST_SYSTEM_PARTIAL_DIAGNOSTIC_ONLY' if rows else 'BLOCKED_NO_FIRST_SYSTEM_DATA',process=proc,features=len(rows),pairs=dict(Counter(r['model0']+' | '+r['model1'] for r in records)),nonfinite_feature_records=sum(not r['finite'] for r in records),zero_normal_records=sum(r['normal_norm']==0 for r in records),maximum_point_distance_m=max((r['point_distance_m'] for r in records),default=None),actual_accepted_state='NOT AVAILABLE',observer_purity='NOT MEASURED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
