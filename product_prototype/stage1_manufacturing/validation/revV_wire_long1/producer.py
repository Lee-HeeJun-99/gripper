"""Finite wire/rotor geometric contract; prescribed planar inextensible path.
No cable material, friction, bend-fatigue or driven dynamics claim.
"""
import argparse,json,math,shutil
import numpy as np
import trimesh
from mechanism_motion import ROOT,tip,beta,rot,move,intersection,flexible,configure,laminate_ends
DRUM_R=8.25;IDLER_R=4.75;START_PHI=0.;MODEL='bezier'
def setup(index):
 global DRUM_R,IDLER_R,START_PHI,MODEL
 configure(index);g=index.get('design_geometry',{});DRUM_R=g.get('drum_wire_radius_mm',8.25);IDLER_R=g.get('idler_wire_radius_mm',4.75);START_PHI=g.get('drum_start_phi',0.);MODEL=g.get('wire_model','bezier')
def arc(c,r,a,b):
 t=np.linspace(a,b,max(2,math.ceil(abs(b-a)/.04)+1))
 return np.array([[c[0]+r*math.cos(v),0,c[1]+r*math.sin(v)] for v in t])
def segment(p,q,r):
 # Extended finite cylinder contains the full capsule, including the arc
 # vertex wedges flat-ended cylinders would miss. Polygon circumscribes.
 d=(q-p)/np.linalg.norm(q-p)
 return trimesh.creation.cylinder(radius=r,segment=[p-r*d,q+r*d],sections=20)
def path(deg):
 a=math.radians(deg);P=(tip(a)@np.array([43,0,-92,1]))[:3];b=beta(P)
 t=np.array([math.sin(b),0,math.cos(b)]);n=np.array([math.cos(b),0,-math.sin(b)])
 E=P+20*t;Q=np.array([44.,0,25])-IDLER_R*n
 # Upper common external tangent: n dot(Cidler-Cdrum)=Rdrum-Ridler.
 d=np.array([-36.,5.]);u=d/np.linalg.norm(d);v=np.array([-u[1],u[0]])
 k=(DRUM_R-IDLER_R)/np.linalg.norm(d);nn=k*u+math.sqrt(1-k*k)*v
 if nn[1]<0:nn=k*u-math.sqrt(1-k*k)*v
 A=np.array([80+DRUM_R*nn[0],0,20+DRUM_R*nn[1]]);B=np.array([44+IDLER_R*nn[0],0,25+IDLER_R*nn[1]])
 phi=math.atan2(nn[1],nn[0]);end=math.atan2(-n[2],-n[0])
 while end<phi:end+=2*math.pi
 free=float(np.linalg.norm(A-B)+IDLER_R*(end-phi)+np.linalg.norm(Q-E))
 return dict(P=P,beta=b,E=E,Q=Q,A=A,B=B,phi=phi,end=end,free=free)
def rotor_name(n):
 return n.startswith(('F0_DRUM','F0_SHAFT','F0_INNER_WASHER','F0_COUPLING'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);p.add_argument('--diameter',type=float,default=.5);p.add_argument('--length-offset',type=float,default=0.);args=p.parse_args();assert .48<=args.diameter<=.52 and abs(args.length_offset)<=.25
 index=json.loads((ROOT/'cad/exports'/args.case/'summary.json').read_text());out=ROOT/'validation'/args.tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 setup(index)
 allmeshes={n:trimesh.load(ROOT/(__import__('pathlib').Path(v['path']).with_suffix('.stl')),force='mesh') for n,v in index['parts'].items()}
 meshes={n:m for n,m in allmeshes.items() if (n.startswith('F0_') or n=='PALM') and not n.endswith('TENDON_WIRE')}
 rigid={n:m for n,m in meshes.items() if 'TERMINAL' in n or n in ('F0_SWIVEL_AXLE','F0_SWIVEL_AXLE_NUT','F0_SWIVEL_SPACER_L','F0_SWIVEL_SPACER_R')}
 swivel={n:m for n,m in meshes.items() if n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE'))}
 rotors={n:m for n,m in meshes.items() if rotor_name(n)}
 fixed={n:m for n,m in meshes.items() if n not in rigid and n not in swivel and n not in rotors and not n.endswith(('SKIN','RAIL_L','RAIL_R'))}
 roots,ends=laminate_ends(meshes);fixed.update(roots);rigid.update(ends)
 b0=beta([43,0,-92]);free0=path(0)['free'];rows=[];hits=[];rotorhits=[]
 for deg in range(0,61,2):
  g=path(deg);eta=(free0-g['free']+args.length_offset)/DRUM_R;T=tip(math.radians(deg));S=rot(g['beta']-math.radians(deg)-b0,point=g['P'])@T;R=rot(eta,point=[80,0,20])
  moving={n:move(m,T) for n,m in rigid.items()};moving.update({n:move(m,S) for n,m in swivel.items()});moving.update({n:move(m,R) for n,m in rotors.items()})
  for n in rotors:
   for k,f in fixed.items():
    v=intersection(moving[n],f)
    if v>1e-6:rotorhits.append(dict(angle_deg=deg,a=n,b=k,volume_mm3=v))
  # Swept wire arcs have exact analytic inner radii8/4.5. Chords are
  # conservatively inflated by their sagitta ONLY for other hardware.
  routes=[('drum_arc',arc((80,20),DRUM_R,START_PHI-eta,g['phi']),{'F0_DRUM'}),('lead',np.array([g['A'],g['B']]),{'F0_DRUM','F0_IDLER'}),('idler_arc',arc((44,25),IDLER_R,g['phi'],g['end']),{'F0_IDLER'}),('tip_line',np.array([g['Q'],g['E']]),{'F0_IDLER'})]
  # Actual cut Bezier channel, including the out-of-plane loading pocket.
  C=np.array([[86,3.6,13.5],[88,3.6,13.5],[88.25,0,18],[88.25,0,20]])
  bez=np.array([(1-t)**3*C[0]+3*(1-t)**2*t*C[1]+3*(1-t)*t*t*C[2]+t**3*C[3] for t in np.linspace(0,1,65)])
  bez=trimesh.transform_points(bez,R)
  if MODEL=='bezier':routes.append(('internal_lead',bez,set()))
  tt=np.array([math.sin(g['beta']),0,math.cos(g['beta'])]);routes.append(('tip_internal_exit',np.array([g['P']+16*tt,g['E']]),{'F0_TIP_FACTORY_NIPPLE'}))
  targets={**fixed,**moving,'F0_FLEX_ENVELOPE':flexible(math.radians(deg))}
  for i in (1,2):
   frame=rot(i*2*math.pi/3,(0,0,1))
   for n,m in fixed.items():
    if n!='PALM':targets[n.replace('F0_',f'F{i}_',1)]=move(m,frame) if n.endswith('ROOT_FIXED') else allmeshes[n.replace('F0_',f'F{i}_',1)]
   targets.update({n.replace('F0_',f'F{i}_',1):move(m,frame) for n,m in moving.items()})
   targets[f'F{i}_FLEX_ENVELOPE']=move(flexible(math.radians(deg)),frame)
  for label,points,analytic in routes:
   for segid,(u,v) in enumerate(zip(points,points[1:])):
    sag=.003 if label in ('drum_arc','idler_arc','internal_lead') else 0
    # Circumscribed polygon, not an inscribed thinner wire.
    m=segment(u,v,(args.diameter/2+sag)/math.cos(math.pi/20))
    for n,f in targets.items():
     if n in analytic or (MODEL=='planar_tangent_nipple' and label=='drum_arc' and segid==0 and n=='F0_DRUM_FACTORY_NIPPLE'):continue
     vol=intersection(m,f)
     if vol>1e-6:hits.append(dict(angle_deg=deg,route=label,part=n,volume_mm3=vol))
  winding=g['phi']-START_PHI+eta
  rows.append(dict(angle_deg=deg,free_wire_mm=g['free'],takeup_mm=free0-g['free'],rotor_deg=math.degrees(eta),wrap_deg=math.degrees(winding),total_external_mm=g['free']+DRUM_R*winding,length_error_mm=g['free']+DRUM_R*winding-(free0+DRUM_R*(path(0)['phi']-START_PHI)),single_layer=winding<2*math.pi,swivel_deg=math.degrees(g['beta'])))
 result=dict(status='WIRE_ROTOR_SCREEN_PASS' if not hits and not rotorhits and all(r['single_layer'] for r in rows) else 'WIRE_ROTOR_SCREEN_FAIL',rows=rows,wire_hits=hits,rotor_hits=rotorhits,wire_diameter_mm=.5,analytic_contact_pending='Own drum/idler contact and factory wire-metal outlet joins require independent analytic/actual CAD certificates. Only first tangent-nipple arc capsule has artificial backward extension at bonded factory join; remaining arc checked against actual nipple.',scope='F0 wire against actual full3Finger hardware,31poses, flexible envelopes and internal tip exit included;120deg symmetry covers other wires against hardware. Wire-wire sector certificate still required. Prescribed NOT dynamic sliding/fatigue. Circumscribed extended capsules include .003mm chord allowance; no uncovered vertex wedges.',stage1_release=False)
 result['wire_diameter_mm']=args.diameter
 result['finished_length_offset_mm']=args.length_offset
 result['assembly_indexing_phase_deg']=math.degrees(args.length_offset/DRUM_R)
 # The physical factory outlet rotates with the drum. Length is adjusted
 # by assembly indexing, not by scaling/stretching/teleporting the cable.
 for row in rows:row['length_error_mm']-=args.length_offset
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],wire_hits=len(hits),rotor_hits=len(rotorhits),first_wire=hits[:8],first_rotor=rotorhits[:5],takeup=rows[-1]['takeup_mm'])))
if __name__=='__main__':main()
