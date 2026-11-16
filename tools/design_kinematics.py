"""Constant-curvature geometric screening and explicitly prescribed sequence."""
import argparse,math,json
from design_regrip import ROOT,put,js
def point(s,theta):
 k=theta/100
 return (50-(1-math.cos(k*s))/k,-math.sin(k*s)/k)if k else(50,-s)
def gap(theta):return min(math.hypot(point(i/20,theta)[0],point(i/20,theta)[1]+75)-20 for i in range(2001))
def main():
 p=argparse.ArgumentParser();p.add_argument('--version',required=True);a=p.parse_args();folder=ROOT/'designs/visualizations'/a.version
 lo=0;hi=1.2
 for _ in range(48):
  mid=(lo+hi)/2
  if gap(mid)>0:lo=mid
  else:hi=mid
 touch=(lo+hi)/2
 js(folder/'kinematics.json',dict(source='independent constant-curvature geometry,NOT SOFA or compliant contact',sampling_mm=.05,object_radius_mm=20,first_intersection_curl_rad=touch,geometric_tendon_draw_mm=1.5*touch,prescribed_curl_rad=.77,prescribed_min_signed_gap_mm=gap(.77),wrap_contact_angle=None,cable_force=None,mechanical_interference='all-pairs surface/hose still NOT RUN'))
 out=['<svg xmlns="http://www.w3.org/2000/svg" width="1250" height="370"><rect width="1250" height="370" fill="white"/><text x="15" y="25" font-size="18">CONCEPT prescribed sequence, not SOFA motion. Circle is research sphere R20 mm.</text>']
 for i,(label,theta,color)in enumerate([('1 OPEN',0,'#14858c'),('2 APPROACH',.4,'#14858c'),('3 FIRST TOUCH',touch,'#d26a35'),('4 JAM / HOLD',touch,'#69589a'),('5 VENT / RESTORE',0,'#14858c')]):
  pts=[point(j,theta)for j in range(101)];coords=' '.join(f'{i*250+40+2*x:.3f},{65-2*y:.3f}'for x,y in pts)
  out.append(f'<text x="{i*250+15}" y="50" font-size="14">{label}</text><circle cx="{i*250+40}" cy="215" r="40" fill="#eee" stroke="#999"/><polyline points="{coords}" fill="none" stroke="{color}" stroke-width="5"/><text x="{i*250+15}" y="300" font-size="12">curl {theta:.3f} rad / draw {1.5*theta:.3f} mm</text>')
 out.append('<text x="15" y="337" font-size="13">JAM and TOUCH intentionally share geometry: no unverified stiffness/holding advantage is animated.</text></svg>');put(folder/'sequence.svg',''.join(out));print(json.dumps(dict(first_touch_rad=touch,draw_mm=1.5*touch,prescribed_gap_mm=gap(.77))))
if __name__=='__main__':main()
