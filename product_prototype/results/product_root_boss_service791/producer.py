"""Exact translated-cylinder sweep and nominal access for new retained root pins."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,cyl,union,transform,evaluate,sha
from bridge_assembly_audit import hits

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);p.add_argument('--threaded-boss',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic()
 src=BASE/'meshes'/a.candidate/'full_assembly_recipe.json';assembly=json.loads(src.read_text());parts=assembly['parts'];shapes=[evaluate(p['shape']) for p in parts];records=[]
 for p in parts:
  if p['group']!='root_headed_pin_proxy':continue
  M=np.array(p['shape']['matrix']);nut=p['name'].replace('_headed_pin','_axle_nut');distance=10.
  # Each component is a convex coaxial cylinder. Its positive-axis extrusion
  # is exactly a longer cylinder;union distributes over the swept components.
  sweep=evaluate(transform(union(cyl(.5,-3.7,2.45+distance),cyl(1.25,2.45,3.45+distance)),M))
  if a.threaded_boss:
   if any(q['name']==nut for q in parts):raise ValueError('boss audit cannot ignore existing loose nut')
   tool=evaluate(transform(cyl(1.,3.55,13.55),M));role='outward_driver_nominal';removed=None
  else:tool=evaluate(transform(cyl(2.,-13.35,-3.35),M));role='inner_nut_tool_nominal';removed=nut
  records.append(dict(pin=p['name'],removed_nut=removed,outward_sweep_mm=distance,swept_intersections=hits(sweep,parts,shapes,[p['name'],nut]),tool_model=role,tool_radius_mm=1. if a.threaded_boss else 2.,tool_length_mm=10.,tool_intersections=hits(tool,parts,shapes,[p['name'],nut])))
 result=dict(status='RETAINED_ROOT_SERVICE_REQUIRES_REVIEW' if any(r['swept_intersections'] or r['tool_intersections'] for r in records) else 'NOMINAL_RETAINED_ROOT_SERVICE_CLEAR_NOT_PRODUCT_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,BASE/'cad/bridge_assembly_audit.py',BASE/'cad/manufacturing_assembly.py')},records=records,runtime_s=time.monotonic()-start,threaded_boss=a.threaded_boss,fabrication_ready=False,scope='Outward10mm full swept finite stepped pins after nut removed,or within nominal threaded-boss throughbore. Inner R2 nut-tool OR outer R1 driver10mm excludes own pin/nut only. No actual thread form,head drive slot,supplier wrench,hand access/thread engagement/preload/actualassembly/tolerances/strength qualification. Existing obstacles retained. Tool blockage is distinct from pin extraction clearance.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],pins=len(records),blocked_sweeps=sum(bool(r['swept_intersections']) for r in records),blocked_tools=sum(bool(r['tool_intersections']) for r in records),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
