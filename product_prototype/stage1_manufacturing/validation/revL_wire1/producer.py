"""Finite wire/rotor geometric contract; prescribed planar inextensible path.
No cable material, friction, bend-fatigue or driven dynamics claim.
"""
import argparse,json,math,shutil
import numpy as np
import trimesh
from mechanism_motion import ROOT,tip,beta,rot,move,intersection,flexible
def arc(c,r,a,b):
 t=np.linspace(a,b,max(2,math.ceil(abs(b-a)/.04)+1))
 return np.array([[c[0]+r*math.cos(v),0,c[1]+r*math.sin(v)] for v in t])
def segment(p,q,r):
 return trimesh.creation.cylinder(radius=r,segment=[p,q],sections=20)
def path(deg):
 a=math.radians(deg);P=(tip(a)@np.array([43,0,-92,1]))[:3];b=beta(P)
 t=np.array([math.sin(b),0,math.cos(b)]);n=np.array([math.cos(b),0,-math.sin(b)])
 E=P+20*t;Q=np.array([44.,0,25])-4.75*n
 # Upper common external tangent: n dot(Cidler-Cdrum)=Rdrum-Ridler.
 d=np.array([-36.,5.]);u=d/np.linalg.norm(d);v=np.array([-u[1],u[0]])
 k=3.5/np.linalg.norm(d);nn=k*u+math.sqrt(1-k*k)*v
 if nn[1]<0:nn=k*u-math.sqrt(1-k*k)*v
 A=np.array([80+8.25*nn[0],0,20+8.25*nn[1]]);B=np.array([44+4.75*nn[0],0,25+4.75*nn[1]])
 phi=math.atan2(nn[1],nn[0]);end=math.atan2(-n[2],-n[0])
 while end<phi:end+=2*math.pi
 free=float(np.linalg.norm(A-B)+4.75*(end-phi)+np.linalg.norm(Q-E))
 return dict(P=P,beta=b,E=E,Q=Q,A=A,B=B,phi=phi,end=end,free=free)
def rotor_name(n):
 return n.startswith(('F0_DRUM','F0_SHAFT','F0_INNER_WASHER','F0_COUPLING'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);args=p.parse_args()
 index=json.loads((ROOT/'cad/exports'/args.case/'summary.json').read_text());out=ROOT/'validation'/args.tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 meshes={n:trimesh.load(ROOT/(__import__('pathlib').Path(v['path']).with_suffix('.stl')),force='mesh') for n,v in index['parts'].items() if n.startswith('F0_') or n=='PALM'}
 rigid={n:m for n,m in meshes.items() if 'TERMINAL' in n or n in ('F0_SWIVEL_AXLE','F0_SWIVEL_AXLE_NUT','F0_SWIVEL_SPACER_L','F0_SWIVEL_SPACER_R')}
 swivel={n:m for n,m in meshes.items() if n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE'))}
 rotors={n:m for n,m in meshes.items() if rotor_name(n)}
 fixed={n:m for n,m in meshes.items() if n not in rigid and n not in swivel and n not in rotors and not n.endswith(('SKIN','RAIL_L','RAIL_R'))}
 b0=beta([43,0,-92]);free0=path(0)['free'];rows=[];hits=[];rotorhits=[]
 for deg in range(0,61,2):
  g=path(deg);eta=(free0-g['free'])/8.25;T=tip(math.radians(deg));S=rot(g['beta']-math.radians(deg)-b0,point=g['P'])@T;R=rot(eta,point=[80,0,20])
  moving={n:move(m,T) for n,m in rigid.items()};moving.update({n:move(m,S) for n,m in swivel.items()});moving.update({n:move(m,R) for n,m in rotors.items()})
  for n in rotors:
   for k,f in fixed.items():
    v=intersection(moving[n],f)
    if v>1e-6:rotorhits.append(dict(angle_deg=deg,a=n,b=k,volume_mm3=v))
  # Swept wire arcs have exact analytic inner radii8/4.5. Chords are
  # conservatively inflated by their sagitta ONLY for other hardware.
  routes=[('drum_arc',arc((80,20),8.25,-eta,g['phi']),{'F0_DRUM'}),('lead',np.array([g['A'],g['B']]),{'F0_DRUM','F0_IDLER'}),('idler_arc',arc((44,25),4.75,g['phi'],g['end']),{'F0_IDLER'}),('tip_line',np.array([g['Q'],g['E']]),{'F0_IDLER'})]
  # Actual cut Bezier channel, including the out-of-plane loading pocket.
  C=np.array([[86,3.6,13.5],[88,3.6,13.5],[88.25,0,18],[88.25,0,20]])
  bez=np.array([(1-t)**3*C[0]+3*(1-t)**2*t*C[1]+3*(1-t)*t*t*C[2]+t**3*C[3] for t in np.linspace(0,1,65)])
  bez=trimesh.transform_points(bez,R)
  routes.append(('internal_lead',bez,set()))
  targets={**fixed,**moving,'F0_FLEX_ENVELOPE':flexible(math.radians(deg))}
  for label,points,analytic in routes:
   for u,v in zip(points,points[1:]):
    sag=.002 if label in ('drum_arc','idler_arc','internal_lead') else 0
    # Circumscribed polygon, not an inscribed thinner wire.
    m=segment(u,v,(.25+sag)/math.cos(math.pi/20))
    for n,f in targets.items():
     if n in analytic:continue
     vol=intersection(m,f)
     if vol>1e-6:hits.append(dict(angle_deg=deg,route=label,part=n,volume_mm3=vol))
  winding=g['phi']+eta
  rows.append(dict(angle_deg=deg,free_wire_mm=g['free'],takeup_mm=free0-g['free'],rotor_deg=math.degrees(eta),wrap_deg=math.degrees(winding),total_external_mm=g['free']+8.25*winding,length_error_mm=g['free']+8.25*winding-(free0+8.25*path(0)['phi']),single_layer=winding<2*math.pi,swivel_deg=math.degrees(g['beta'])))
 result=dict(status='WIRE_ROTOR_SCREEN_PASS' if not hits and not rotorhits and all(r['single_layer'] for r in rows) else 'WIRE_ROTOR_SCREEN_FAIL',rows=rows,wire_hits=hits,rotor_hits=rotorhits,wire_diameter_mm=.5,analytic_contact_pending='Own drum/idler circular arcs omitted from chord test ONLY: exact inner radius certificates and actual active-plane shape containment must independently pass before release.',scope='F0 own package,31poses, actual exported meshes except flexible skin/rails; other Finger wire interference and exact radius certificate PENDING; prescribed NOT dynamic sliding/fatigue. Polygon tube overbound includes .002mm chord allowance.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],wire_hits=len(hits),rotor_hits=len(rotorhits),first_wire=hits[:8],first_rotor=rotorhits[:5],takeup=rows[-1]['takeup_mm'])))
if __name__=='__main__':main()
