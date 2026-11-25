"""Finite REST wire spans and declared service cut-set checks, no dynamics."""
import argparse,hashlib,json,math,shutil
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
def tube(a,b,r):
 a,b=np.array(a,float),np.array(b,float)
 return trimesh.creation.cylinder(radius=r,segment=[a,b],sections=48)
def hits(s,meshes,excluded=()):
 result=[]
 for name,m in meshes.items():
  if name in excluded:continue
  if np.any(np.minimum(s.bounds[1],m.bounds[1])-np.maximum(s.bounds[0],m.bounds[0])<=0):continue
  c=trimesh.boolean.intersection([s,m],engine='manifold');v=float(c.volume)
  if v>1e-6:result.append(dict(part=name,volume_mm3=v))
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
 src=ROOT/'cad/exports'/a.revision;out=ROOT/'validation'/a.tag;out.mkdir(parents=True,exist_ok=False)
 audit=json.loads((src/'audit.json').read_text());meshes={p['id']:trimesh.load(src/(p['id']+'.stl'),force='mesh') for p in audit['parts']}
 # Common upper tangent; wire CENTRELINE radii include0.25mm physical radius.
 c1=np.array([80.,20.]);c2=np.array([44.,25.]);r1,r2=8.25,4.75
 d=c2-c1;theta=math.atan2(d[1],d[0]);alpha=math.acos((r1-r2)/np.linalg.norm(d))
 normals=[np.array([math.cos(theta+t),math.sin(theta+t)]) for t in (-alpha,alpha)]
 n=max(normals,key=lambda n:n[1]);p1=c1+r1*n;p2=c2+r2*n
 end=np.array([47.,-98.]);v=end-c2;phi=math.atan2(v[1],v[0]);beta=math.acos(r2/np.linalg.norm(v))
 candidates=[c2+r2*np.array([math.cos(phi+t),math.sin(phi+t)]) for t in (-beta,beta)]
 leave=min(candidates,key=lambda p:p[0]);wire=[]
 for i in range(3):
  R=trimesh.transformations.rotation_matrix(i*2*math.pi/3,[0,0,1])
  for label,u,w in [('drum_to_idler',[p1[0],6,p1[1]],[p2[0],6,p2[1]]),('idler_to_terminal',[leave[0],6,leave[1]],[47,0,-98])]:
   s=tube(u,w,.25);s.apply_transform(R);s.export(out/f'F{i}_{label}.stl');wire.append(dict(finger=i,span=label,local_start_mm=list(u),local_end_mm=list(w),hits=hits(s,meshes)))
 # Cartridge slides down, with ROOT_FRONT and its bolts/nuts deliberately
 # removed ONLY for this unloaded, wire-disconnected service operation.
 # All other Fingers, drives, Palm and Root back halves remain present.
 mover=[n for n in meshes if n.startswith(('F0_SKIN','F0_RAIL','F0_TERMINAL'))]
 cutset=[n for n in meshes if n.startswith(('F0_ROOT_FRONT','F0_ROOT_BOLT','F0_ROOT_NUT'))]
 extraction=[]
 for dz in np.linspace(0,120,25):
  for name in mover:
   s=meshes[name].copy();s.apply_translation([0,0,-dz]);h=hits(s,meshes,set(mover+cutset))
   if h:extraction.append(dict(downward_mm=float(dz),moving=name,hits=h))
 tools=[]
 for i in range(3):
  R=trimesh.transformations.rotation_matrix(i*2*math.pi/3,[0,0,1])
  # These parts are not yet installed at motor screw installation, or must
  # be removed for the reverse operation. Not a collision-model exemption.
  removed=[n for n in meshes if n.startswith(tuple(f'F{i}_{s}' for s in ('PEDESTAL','BEARING','SHAFT','DRUM','COUPLING')))]
  for x in (64.5,95.5):
   for z in (4.5,35.5):
    t=tube([x,-31,z],[x,-1,z],2.25);t.apply_transform(R)
    tools.append(dict(finger=i,x_mm=x,z_mm=z,full_assembly_hits=hits(t,meshes),assembly_step_cutset=removed,staged_hits=hits(t,meshes,removed)))
 result=dict(revision=a.revision,wire_diameter_mm=.5,straight_REST_wire_spans=wire,idler_arc=dict(centre_xz_mm=c2.tolist(),wire_centre_radius_mm=r2,groove_radius_mm=4.5,radial_surface_gap_mm=0.,axial_flange_gap_mm=1.25,scope='analytic concentric circular intended contact; no sliding/friction/dynamic qualification'),cartridge=dict(moving=mover,cutset=cutset,wire_disconnected_required=True,samples=25,range_mm=[0,120],collision_samples=extraction,continuous_CCD=False),motor_tools=tools,tool_scope='R2.25x30mm straight shank envelope, NOT full hex key/handle/hand',Stage1_release=False,Native_executed=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py')
 (out/'inputs_sha256.json').write_text(json.dumps({str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [src/'audit.json',*sorted(src.glob('*.stl'))]},indent=2))
 print(json.dumps(dict(wire_spans_with_hits=sum(bool(w['hits']) for w in wire),extraction_collision_samples=len(extraction),tool_full_hits=sum(bool(t['full_assembly_hits']) for t in tools),tool_staged_hits=sum(bool(t['staged_hits']) for t in tools))))
if __name__=='__main__':main()
