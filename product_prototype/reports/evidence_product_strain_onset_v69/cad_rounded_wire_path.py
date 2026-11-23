"""Circular-filleted reference wire design; bend radius is a hypothesis,not supplier approval."""
import argparse,json,math,subprocess
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from generate import world,width,guide_outboard,guide_normal

def fillet(points,radius):
 if radius<=0:raise ValueError('positive proposed bend radius required')
 route=[points[0]];trim=[];max_sag=0.
 for k in range(1,len(points)-1):
  p=points[k];u=p-points[k-1];v=points[k+1]-p;lu=np.linalg.norm(u);lv=np.linalg.norm(v);u/=lu;v/=lv;cross=np.cross(u,v);s=np.linalg.norm(cross)
  if s==0:
   if u@v<=0:raise ValueError('opposite branch not a valid fillet')
   route.append(p);trim.append(0.);continue
  phi=math.atan2(s,float(u@v));d=radius*math.tan(phi/2)
  if d>=min(lu,lv)/2:raise ValueError('fillets may overlap:reject this radius')
  trim.append(d);normal=cross/s;start=p-u*d;center=start+radius*np.cross(normal,u);radial=start-center;n=max(2,math.ceil(phi/math.radians(1)))
  for theta in np.linspace(0,phi,n+1):route.append(center+radial*math.cos(theta)+np.cross(normal,radial)*math.sin(theta))
  max_sag=max(max_sag,radius*(1-math.cos(phi/(2*n))))
 route.append(points[-1]);return np.asarray(route),max_sag,trim

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);p.add_argument('--radius-mm',type=float,required=True);p.add_argument('--tight-envelope',action='store_true');args=p.parse_args();out=BASE/'results'/args.tag;out.mkdir(exist_ok=False);source=BASE/'meshes'/args.candidate/'assembly_recipe.json';a=json.loads(source.read_text());cfg=a['baseline_config'];td=cfg['tendon'];solids=[(p,evaluate(p['shape'])) for p in a['parts']];records=[]
 for f,angle in enumerate(cfg['palm']['angles_deg']):
  for c,side in enumerate((-1,1)):
   points=np.asarray([world(cfg,[x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)],angle) for x in [0]+td['guide_stations']]);route,sag,trim=fillet(points,args.radius_mm);hits=[];rad=td['wire_radius']+sag
   # A circumscribed square prism encloses each radius-r segment, including
   # roundoff-independent polygon radial containment. Endpoint cubes enclose
   # spheres. This is a conservative obstacle screening,not exact tube CSG.
   for k,point in enumerate(route):
    probes=[trimesh.creation.box(extents=[2*rad]*3,transform=trimesh.transformations.translation_matrix(point))]
    if args.tight_envelope:
     ball=trimesh.creation.icosphere(subdivisions=2);plane_distance=np.min(np.abs(np.einsum('ij,ij->i',ball.face_normals,ball.triangles[:,0])));ball.apply_scale(rad/plane_distance);ball.apply_translation(point);probes=[ball]
    if k:
     chord=route[k]-route[k-1];length=np.linalg.norm(chord)
     if length==0:continue
     m=trimesh.geometry.align_vectors([0,0,1],chord/length);m[:3,3]=(route[k]+route[k-1])/2
     probes.append(trimesh.creation.box(extents=[2*rad,2*rad,length],transform=m))
     if args.tight_envelope:probes[-1]=trimesh.creation.cylinder(radius=rad/math.cos(math.pi/64),segment=route[k-1:k+1],sections=64)
    for probe in probes:
     for part,solid in solids:
      if np.any(np.minimum(probe.bounds[1],solid.bounds[1])-np.maximum(probe.bounds[0],solid.bounds[0])<=0):continue
      hit=trimesh.boolean.intersection([probe,solid],engine='manifold')
      if len(hit.faces):hits.append(dict(sample=k,part=part['name'],signed_volume_mm3=float(hit.volume)))
   records.append(dict(finger=f,cable=c,route_mm=route.tolist(),arc_sagitta_bound_mm=sag,trim_distances_mm=trim,conservative_envelope_intersections=hits))
 result=dict(status='ROUNDED_REFERENCE_WIRE_DESIGN_SCREEN_NOT_MATERIAL_OR_MOTION_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),source_recipe_sha256=sha(source),candidate=args.candidate,proposed_centerline_bend_radius_mm=args.radius_mm,supplier_minimum_bend_radius_mm=None,records=records,scope='Circular fillet between reference guide stations; stress/friction/lead-in/tension shape not modeled. Circumscribed box envelopes can report false-positive tube collisions; no-hit means geometric screening only under finite precision. No Native geometry adoption.')
 result['envelope']='circumscribed64gon cylinders and circumscribedicospheres' if args.tight_envelope else 'circumscribedboxes'
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(wires=len(records),envelope_hits=sum(len(r['conservative_envelope_intersections']) for r in records)),indent=2))
if __name__=='__main__':main()
