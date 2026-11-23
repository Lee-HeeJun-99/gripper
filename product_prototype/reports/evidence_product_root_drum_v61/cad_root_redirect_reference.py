"""Analytic ideal pulley contact reference, not mesh-intersection override."""
import argparse,json,math,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,sha
from root_redirect_candidate import corner_frame

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 src=BASE/'results/product_root_redirect778/summary.json';d=json.loads(src.read_text());checks=[]
 for r in d['records']:
  route=np.array(r['route_mm']);centre=np.array(r['centre_mm']);radial=np.linalg.norm(route-centre,axis=1)
  # Circular arc samples only;straight tangent legs have larger radii.
  arc=radial[radial<2.000000001]
  checks.append(dict(part=r['part'],arc_radius_max_abs_error_mm=float(abs(arc-2).max()),ideal_barrel_radial_clearance_mm=2.-.25-1.75,ideal_flange_side_clearance_mm=.4-.25,conditional_equal_tension_resultant_N=3*math.sin(math.radians(r['turn_angle_deg'])/2),retained_nonempty_mesh_contacts=len(r['wire_intersections']),mount_reaction_N=None))
 # Independent right-angle reference and explicit degeneracy rejection.
 M,theta,trim=corner_frame(np.array([0.,0,0]),np.array([10.,0,0]),np.array([10.,10,0]),2.)
 assert np.allclose(M[:3,3],[8,2,0],rtol=0,atol=1e-14) and abs(trim-2)<1e-14
 rejected=0
 for points in (([0,0,0],[0,0,0],[1,0,0]),([0,0,0],[1,0,0],[2,0,0])):
  try:corner_frame(*map(lambda x:np.array(x,dtype=float),points),2.)
  except ValueError:rejected+=1
 assert rejected==2
 result=dict(status='ANALYTIC_IDEAL_CONTACT_REFERENCE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x.relative_to(BASE)):sha(x) for x in (src,Path(__file__),BASE/'cad/root_redirect_candidate.py')},records=checks,right_angle_reference=True,degenerate_cases_rejected=rejected,scope='Nominal ideal circular barrel tangency (zero radial clearance) and0.15mm flange side clearance. Inflated circumscribed probes necessarily overlap intended bearing contact;778 FAIL/review status unchanged. No tolerance/friction/rotation/retention/mount or physical PASS;no SOFA execution.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
