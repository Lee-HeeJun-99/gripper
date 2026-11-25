"""Independent mesh/motion/tolerance checks of exported CAD, not dynamics."""
import argparse,csv,hashlib,json,math,shutil
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]

def strip(angle):
 # Prescribed constant-curvature envelope below Palm, not a SOFA trajectory.
 # Physical sheet/ribs are approximated by a conservative0.7mm-thick strip.
 s=np.linspace(0,88,45);a=math.radians(angle)
 if a==0:x=np.full_like(s,50.);z=-12-s
 else:r=88/a;x=50-r*(1-np.cos(s/r));z=-12-r*np.sin(s/r)
 vertices=np.array([[u+d,y,w] for u,w in zip(x,z) for d,y in [(-.05,-12),(.75,-12),(.75,12),(-.05,12)]])
 faces=[]
 for j in range(44):
  for k in range(4):
   p=4*j+k;q=4*j+(k+1)%4;faces.extend([[p,q,q+4],[p,q+4,p+4]])
 faces.extend([[0,2,1],[0,3,2],[176,177,178],[176,178,179]])
 m=trimesh.Trimesh(vertices,faces,process=True)
 if m.volume<0:m.invert()
 assert m.is_volume
 return m

def main():
 p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
 src=ROOT/'cad/exports'/a.revision;out=ROOT/'validation'/a.tag;out.mkdir(parents=True,exist_ok=False)
 audit=json.loads((src/'audit.json').read_text());meshes={};quality=[]
 for row in audit['parts']:
  m=trimesh.load(src/(row['id']+'.stl'),force='mesh',process=True);meshes[row['id']]=m
  quality.append(dict(id=row['id'],watertight=bool(m.is_watertight),winding=bool(m.is_winding_consistent),positive_volume=bool(m.volume>0),bounds_mm=m.bounds.tolist(),brep_volume_mm3=row['volume_mm3'],mesh_volume_mm3=float(m.volume)))
 # Full-turn rotor ENVELOPE against every fixed exported mesh. Sufficient
 # conservative check only; positive volume is a candidate obstruction.
 rotational=[]
 for i in range(3):
  centre=80 if a.revision not in ('revA','revB','revC','revD') else 27 if a.revision=='revD' else 35
  env=trimesh.creation.cylinder(radius=10,height=9,sections=128)
  rx=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);env.apply_transform(rx);env.apply_translation([centre,8,20]);env.apply_transform(trimesh.transformations.rotation_matrix(i*2*math.pi/3,[0,0,1]))
  for name,m in meshes.items():
   if name==f'F{i}_DRUM':continue
   if np.any(np.minimum(env.bounds[1],m.bounds[1])-np.maximum(env.bounds[0],m.bounds[0])<=0):continue
   v=trimesh.boolean.intersection([env,m],engine='manifold').volume
   if v>1e-6:rotational.append(dict(rotor=i,part=name,volume_mm3=float(v)))
 # The envelope fills the axial shaft hole: own shaft overlap is EXPECTED
 # and is reported separately, NOT used to suppress actual CAD collisions.
 foreign=[r for r in rotational if r['part']!=f"F{r['rotor']}_SHAFT"]
 motion=[]
 for angle in range(0,61,2):
  shapes=[]
  for i in range(3):
   m=strip(angle);m.apply_transform(trimesh.transformations.rotation_matrix(i*2*math.pi/3,[0,0,1]));shapes.append(m)
  for i in range(3):
   for j in range(i+1,3):
    v=trimesh.boolean.intersection([shapes[i],shapes[j]],engine='manifold').volume
    if v>1e-6:motion.append(dict(angle_deg=angle,fingers=[i,j],volume_mm3=float(v)))
 # Explicit drawing-based stack, not generic NEMA assumptions.
 tolerance=dict(motor_source='https://www.pololu.com/file/0J714/SY42STH38-1684A.pdf',motor_hole_pitch_mm=[30.8,31.2],mount_hole_D_mm=3.6,nominal_screw_D_mm=3,diagonal_pitch_error_mm=math.sqrt(2)*.1,radial_clearance_mm=.3,pitch_margin_mm=.3-math.sqrt(2)*.1,motor_pilot_max_D_mm=22,mount_pilot_D_mm=22.5,pilot_radial_margin_mm=.25,motor_shaft_D_mm=[4.988,5.0],coupler_bore_D_mm=5.10,coupler_diametral_gap_mm=[.10,.112],bearing_pocket_D_mm=[16.05,16.07],bearing_nominal_outer_D_mm=16,bearing_actual_tolerance='NOT YET supplier lot/tolerance class verified',shaft_fit='h6 design intent; selected bearing fit/retention unqualified',thread_torque_Nm=None)
 # Individual front-projection outlines from actual exported meshes; sizes
 # are computed, not copied from rendered pictures.
 draw=ROOT/'cad/drawings'/a.revision;draw.mkdir(parents=True,exist_ok=False)
 for name,m in meshes.items():
  if not name.startswith('F0_') and name!='PALM':continue
  lo,hi=m.bounds;w,h=hi[0]-lo[0],hi[2]-lo[2]
  lines=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650" viewBox="0 0 900 650">','<rect width="900" height="650" fill="white"/>',f'<text x="20" y="25">{name} — mm; X/Z projection; revision {a.revision}</text>']
  scale=min(700/max(w,1),450/max(h,1));pts=m.vertices
  for e in m.edges_unique:
   x1,z1=(pts[e[0],[0,2]]-lo[[0,2]])*scale;x2,z2=(pts[e[1],[0,2]]-lo[[0,2]])*scale
   lines.append(f'<path d="M{80+x1:.3f},{550-z1:.3f} L{80+x2:.3f},{550-z2:.3f}" stroke="black" stroke-width=".3"/>')
  lines.extend([f'<text x="20" y="590">Bounds XYZ: {np.round(hi-lo,4).tolist()} mm; datum/world coordinates in audit.json</text>','<text x="20" y="620">REVIEW DRAWING: hidden features/threads/process tolerances use producer and BOM; NOT RELEASED</text>','</svg>'])
  (draw/(name+'.svg')).write_text('\n'.join(lines))
 bom=ROOT/'bom';bom.mkdir(exist_ok=True)
 with (bom/'STAGE1_BOM.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['part_ID','quantity','material_candidate','make_or_buy','manufacturing_method','dimensions_XYZ_mm','STEP','STL','assembly_position','qualification_note'])
  for r,q in zip(audit['parts'],quality):w.writerow([r['id'],1,r['material'],r['role'],r['process'],str(np.round(np.ptp(q['bounds_mm'],axis=0),4).tolist()),str((src/(r['id']+'.step')).relative_to(ROOT)),str((src/(r['id']+'.stl')).relative_to(ROOT)),r['id'],r['note']])
 result=dict(revision=a.revision,geometry=quality,all_meshes_watertight=all(q['watertight'] and q['positive_volume'] and q['winding'] for q in quality),rotor_envelope_hits=rotational,foreign_rotor_hits=foreign,prescribed_finger_hits=motion,prescribed_clear_range_deg=[0, min([m['angle_deg'] for m in motion],default=62)-2],tolerance=tolerance,continuous_CCD=False,Native_executed=False,wire_sliding_or_fatigue_qualified=False,stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py')
 manifest={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for directory in (src,draw) for f in sorted(directory.iterdir()) if f.is_file()}
 (out/'input_export_sha256.json').write_text(json.dumps(manifest,indent=2))
 print(json.dumps(dict(watertight=result['all_meshes_watertight'],foreign_rotor_hits=len(foreign),first_finger_collision_deg=min([m['angle_deg'] for m in motion],default=None),stage1_release=False)))
if __name__=='__main__':main()
