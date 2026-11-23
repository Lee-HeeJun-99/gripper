"""Finite guide/support DESIGN candidate from shared B3 config;NOT simulation.
STL/SCAD only;no CAD Boolean union/STEP/fabrication certification claimed.
"""
import argparse,csv,json,sys,hashlib
from pathlib import Path
import numpy as np
import trimesh
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from finite_guide_coupon import eyelet
from generate import world,width,guide_normal,guide_outboard,stl
def guide_basis(c,p,angle):
 h=1e-3;centre=np.array(world(c,p,angle));ex=np.array(world(c,p+[h,0,0],angle))-np.array(world(c,p-[h,0,0],angle));ex/=np.linalg.norm(ex);ey=np.array(world(c,p+[0,h,0],angle))-centre;ey-=ex*(ex@ey);ey/=np.linalg.norm(ey);return np.stack((ex,ey,np.cross(ex,ey)),axis=1)
def support(c,x,side,angle):
 # Existing generate.py guide_support hull,now using shared curved/sector route.
 points=[];rail=c['finger']['rail_thickness'];lo=max(c['finger']['clamp_length'],x-1.5);hi=min(c['finger']['length'],x+1.5)
 bases=[([xx-.4,yy-.4,-rail-.8],[.8,.8,.8]) for xx,yy in ((lo,side*width(c,lo)/2),(lo,side*(width(c,lo)/2-2)),(hi,side*width(c,hi)/2))]
 bases.append(([x-1,side*(width(c,x)/2+guide_outboard(c,x))-.6,guide_normal(c,x)-1.5],[2,1.2,.8]))
 for origin,size in bases:
  for dx in (0,size[0]):
   for dy in (0,size[1]):
    for dz in (0,size[2]):points.append(world(c,np.array(origin)+[dx,dy,dz],angle))
 return trimesh.convex.convex_hull(np.array(points))
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--config',type=Path,required=True);a=p.parse_args()
 if Path(a.name).name!=a.name:raise ValueError('local unique name')
 out=BASE/'meshes'/a.name;out.mkdir(exist_ok=False);draw=BASE/'drawings'/a.name;draw.mkdir(exist_ok=False);cfg=json.loads(a.config.read_text());shape,checks=eyelet(cfg,64);stl(out/'eyelet_local_mm.stl',shape.vertices,shape.faces);(out/'config.json').write_bytes(a.config.read_bytes());guides=[];supports=[];lines=['// DESIGN CANDIDATE ONLY;not simulated deformation or STEP assembly.','$fn=64;']
 for finger,angle in enumerate(cfg['palm']['angles_deg']):
  for cable,side in enumerate((-1,1)):
   for k,x in enumerate(cfg['tendon']['guide_stations']):
    p=np.array([x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)]);centre=np.array(world(cfg,p,angle));basis=guide_basis(cfg,p,angle);verts=shape.vertices@basis.T+centre;ring=trimesh.Trimesh(verts,shape.faces,process=False);bracket=support(cfg,x,side,angle);prefix=f'f{finger}_c{cable}_s{k}';stl(out/(prefix+'_eyelet_mm.stl'),verts,shape.faces);stl(out/(prefix+'_support_mm.stl'),bracket.vertices,bracket.faces)
    for mesh,color in ((ring,'[0.8,0.5,0.1]'),(bracket,'[0.3,0.5,0.7]')):lines.append('color('+color+') polyhedron(points='+json.dumps(mesh.vertices.tolist())+',faces='+json.dumps(mesh.faces.tolist())+');')
    guides.append(dict(finger=finger,cable=cable,station_mm=x,center_mm=centre.tolist(),basis=basis.tolist(),geometry=checks));supports.append(dict(finger=finger,cable=cable,station_mm=x,volume_mm3=float(bracket.volume),watertight=bool(bracket.is_watertight),manufacturing='proposed convex support hull,not validated material/join/strength',mass_kg=None))
 (out/'finite_hardware.scad').write_text('\n'.join(lines));(out/'geometry.json').write_text(json.dumps(dict(guides=guides,supports=supports),indent=2));(draw/'finite_hardware.scad').write_bytes((out/'finite_hardware.scad').read_bytes());(draw/'config.json').write_bytes(a.config.read_bytes())
 (draw/'eyelet_section.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="360"><rect width="720" height="360" fill="white"/><g fill="none" stroke="black"><circle cx="160" cy="170" r="105"/><circle cx="160" cy="170" r="42"/><rect x="360" y="65" width="140" height="210"/></g><g font-family="sans-serif" font-size="16"><text x="20" y="25">DESIGN CANDIDATE — dimensions mm;not actual simulation</text><text x="50" y="310">OD3 / ID1.2</text><text x="350" y="310">L2, wire diameter0.5</text><text x="300" y="45">Axis follows manufactured finger tangent</text><text x="20" y="345">Support hull / joint / strength / moving interference NOT VERIFIED;STEP absent</text></g></svg>')
 with (draw/'BOM.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['part','quantity','dimensions_mm','status']);w.writerow(['finite annular eyelet',36,'OD3 ID1.2 L2','research assumed;stock/material unselected']);w.writerow(['convex guide support',36,'shared 3-foot hull to guide','candidate;bonding and strength NOT VERIFIED']);w.writerow(['wire',6,'diameter0.5','assumed;stroke and bending radius NOT VERIFIED'])
 result=dict(status='FINITE_HARDWARE_CAD_CANDIDATE_NOT_ASSEMBLY_VERIFIED',scope='Manufactured rest guide and proposed support parts,not whole product/actual dynamics. Skin/Palm/Motor/Fasteners not re-exported. Support-eyelet intended overlap requires valid join/Boolean and strength qualification.',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),config_sha256=hashlib.sha256(a.config.read_bytes()).hexdigest(),eyelet=checks,guides=len(guides),supports=len(supports),all_supports_watertight=all(x['watertight'] for x in supports),wire_to_bore_radial_clearance_mm=cfg['tendon']['guide_hole_radius']-cfg['tendon']['wire_radius'],STEP='NOT GENERATED',CAD_kernel='FreeCADCmd/freecadcmd/openscad executable unavailable in current PATH',dynamic_support_model='NOT IMPLEMENTED',fabrication_ready=False)
 (out/'checks.json').write_text(json.dumps(result,indent=2));(draw/'checks.json').write_bytes((out/'checks.json').read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
