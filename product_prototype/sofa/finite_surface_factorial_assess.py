"""Compare completed 2x2 actual Native static cells; no reruns or geometry edits."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def compare(a,b):
 x=read(a/'states.csv');y=read(b/'states.csv');assert [r['time_s'] for r in x]==[r['time_s'] for r in y];errors=dict(position_m=0.,orientation_rad=0.,linear_velocity_m_s=0.,angular_velocity_rad_s=0.,linear_impulse_Ns=0.,angular_impulse_Nms=0.)
 for r,s in zip(x,y):
  q,p=[np.fromstring(v['rigid_q'],sep=' ').reshape(-1,7) for v in (r,s)];v,w=[np.fromstring(u['rigid_v'],sep=' ').reshape(-1,6) for u in (r,s)];f,g=[np.fromstring(u['object_impulse_Ns_Nms'],sep=' ') for u in (r,s)];values=[float(abs(q[:,:3]-p[:,:3]).max()),float((Rotation.from_quat(q[:,3:]).inv()*Rotation.from_quat(p[:,3:])).magnitude().max()),float(abs(v[:,:3]-w[:,:3]).max()),float(abs(v[:,3:]-w[:,3:]).max()),float(abs(f[:3]-g[:3]).max()),float(abs(f[3:]-g[3:]).max())]
  for k,value in zip(errors,values):errors[k]=max(errors[k],value)
 return errors
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);b=BASE/'results';cases=dict(open_partition=b/'finite_surface_capability1665/control',closed_partition=b/'finite_surface_factorial1671/closed_partition',open_aggregate=b/'finite_surface_factorial1671/open_aggregate',closed_aggregate=b/'raytrace_finite_surface1668/closed_control');cap1=compare(cases['open_partition'],cases['closed_partition']);cap2=compare(cases['open_aggregate'],cases['closed_aggregate']);owner=compare(cases['open_partition'],cases['open_aggregate']);d=dict(status='STATIC_CAP_EFFECT_ZERO_OWNERSHIP_RESPONSE_NOT_INVARIANT',cap_effect_partition=cap1,cap_effect_aggregate=cap2,ownership_effect_open=owner,saved_facet_intersection_outputs=dict(open_partition=2,closed_partition=2,open_aggregate=0,closed_aggregate=0),scope='Actual2stepstaticinitialcoupon ONLY. Alloriginalphysicalsurfaces/Line/Pointfeatures preserved andsameassumedrigidmass/inertia. Modelownership affectscontactreduction/order,not a mechanicalimprovement ornewmaterialproperty. Cap-only q/v/impulse identity isreproducibility,notphysical/timeconvergence. NeeddynamicBeam contrastbeforeanyintegration. No originalRaw/verdict edits.',source_sha256=sha(Path(__file__)),input_sha256={k:sha(v/'states.csv') for k,v in cases.items()});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
