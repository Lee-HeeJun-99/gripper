"""Reuse crossing classifier on actual NEW Native mapped finite ring surfaces."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from finite_guide_surface_audit import crossings
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in ('b3_inertia_input_contact600','b3_inertia_input_contact_half601','b3_inertia_input_contact_quarter602'):
  src=BASE/'results'/case;root=ET.parse(src/'0/scene.scn').getroot();faces=np.fromstring(root.find("./Node[@name='guide0']/Node[@name='collision']/MeshTopology").get('triangles'),sep=' ').astype(int).reshape(-1,3);rows=[list(csv.DictReader((src/f'0/mapped{i}_eyelet.csv').open())) for i in (0,1)]
  if len(rows[0])!=len(rows[1]):raise ValueError('incomplete actual mapped surface')
  for k,r in enumerate(rows[0]):
   vertices=[np.fromstring(rows[i][k]['q'],sep=' ').reshape(-1,3) for i in (0,1)];count,unknown=crossings(vertices,faces);records.append(dict(case=case,time_s=float(r['time_s']),strict_interior_edge_face_crossings=count,parallel_or_boundary_uncertain_tests=unknown,status='FAIL_SAVED_SURFACE_CROSSING' if count else 'UNCERTAIN_BOUNDARY' if unknown else 'NO_DETECTED_CROSSING_NOT_CONTAINMENT_OR_SWEPT_CLEARANCE'))
 result=dict(status='FAIL_SAVED_SURFACE_CROSSING' if any(r['strict_interior_edge_face_crossings'] for r in records) else 'SAVED_SURFACE_AUDIT_ONLY',scope='Actual accepted mapped finite-facet positions. Reuses prior independent edge-triangle classifier. No centre-sphere proxies,mesh-mass substitution or continuous/swept/containment/wholeassembly certificate.',producer_sha256=sha(Path(__file__)),classifier_sha256=sha(BASE/'sofa/finite_guide_surface_audit.py'),records=records,strict_crossings=sum(r['strict_interior_edge_face_crossings'] for r in records),uncertain_tests=sum(r['parallel_or_boundary_uncertain_tests'] for r in records))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
