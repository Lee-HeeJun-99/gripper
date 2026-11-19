"""Shared manufactured-reference/route checks. Geometry is NOT dynamic evidence."""
import argparse,copy,hashlib,json,sys,math,shutil
from pathlib import Path
import numpy as np
import trimesh
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'cad'))
from generate import world,width,guide_normal,guide_outboard,reference_local,mesh,stl

def preflight(c,m,R,fingers=1):
 local=np.array(m['local_positions_mm']);tet=np.array(m['tetrahedra']);faces=np.array(m['triangles']);centre=np.array(c['simulation']['sphere_center_mm']);records=[]
 for angle in c['palm']['angles_deg'][:fingers]:
  q=np.array([world(c,p,angle) for p in local]);d=q[tet[:,1:]]-q[tet[:,0,None]];det=np.linalg.det(d.transpose(0,2,1));edges=q[tet[:,[1,2,3,2,3,3]]]-q[tet[:,[0,0,0,1,1,2]]];quality=12*(abs(det)/2)**(2/3)/np.sum(edges*edges,axis=(1,2))
  near=trimesh.triangles.closest_point(q[faces],np.repeat(centre[None],len(faces),axis=0));gap=float((np.linalg.norm(near-centre,axis=1)-R).min());wire=1e9;guide=1e9;routes=[]
  for side in (-1,1):
   route=np.array([world(c,[x,side*(width(c,x)/2+guide_outboard(c,x)),guide_normal(c,x)],angle) for x in [0]+c['tendon']['guide_stations']]);routes.append(route.tolist());a=route[:-1];v=np.diff(route,axis=0);u=np.clip(np.sum((centre-a)*v,axis=1)/np.sum(v*v,axis=1),0,1);wire=min(wire,float((np.linalg.norm(a+u[:,None]*v-centre,axis=1)-R-c['tendon']['wire_radius']).min()));guide=min(guide,float((np.linalg.norm(route[1:]-centre,axis=1)-R-math.hypot(c['tendon']['guide_outer_radius'],1)).min()))
  records.append(dict(angle_deg=angle,minimum_surface_gap_mm=gap,wire_object_gap_mm=wire,guide_enclosing_sphere_gap_mm=guide,minimum_signed_tet_determinant_mm3=float(det.min()),minimum_mean_ratio_quality=float(quality.min()),volume_mm3=float(det.sum()/6),routes_mm=routes))
 between=None
 if fingers>1:
  groups=[np.array(r['routes_mm'])[:,1:].reshape(-1,3) for r in records];between=min(float(np.linalg.norm(groups[i][:,None]-groups[j][None,:],axis=2).min()-2*math.hypot(c['tendon']['guide_outer_radius'],1)) for i in range(fingers) for j in range(i+1,fingers))
 ok=all(r['minimum_surface_gap_mm']>=c['simulation']['contact_distance_mm'] and r['wire_object_gap_mm']>0 and r['guide_enclosing_sphere_gap_mm']>0 and r['minimum_signed_tet_determinant_mm3']>0 for r in records) and (between is None or between>=0)
 return dict(status='INITIAL_GEOMETRY_PASS' if ok else 'REJECT_INITIAL_GEOMETRY',scope='initial closest triangle/finite wire/conservative guide spheres/interfinger guide sphere/signed tetra quality only;NOT swept clearance,self-collision,assembly or bending validation',initial_interfinger_guide_sphere_gap_mm=between,records=records,stress_free_reference=c['finger'].get('precurve'),area=None,pressure=None)

def configs():
 c=json.loads((BASE/'meshes/native_skin_out24_v6/config.json').read_text());c['simulation']['sphere_center_mm']=[0,0,-65];c['simulation']['sphere_mass_kg']=.05;c['tendon']['maximum_stroke']=4
 c.pop('guide_mechanics',None);c.pop('surface_partition',None)
 a=copy.deepcopy(c);a['tendon']['distal_profile']=dict(start_mm=60,tip_offset_mm=9)
 b=copy.deepcopy(c);b['finger']['precurve']=dict(start_mm=60,angle_deg=20,reference='stress-free manufactured native FEM rest state,not observed bending')
 hybrid=copy.deepcopy(b);hybrid['tendon']['distal_profile']=copy.deepcopy(a['tendon']['distal_profile'])
 return dict(baseline=c,A_distal=a,B_precurve=b,C_hybrid=hybrid)

def export(name,c,out):
 out.mkdir(parents=True,exist_ok=False);v,t,surf=mesh(c);m=dict(local_positions_mm=v,tetrahedra=t,triangles=surf);q=np.array([reference_local(c,p) for p in v]);stl(out/'finger_bonded.stl',q,surf)
 # Part surfaces are generated from each material subset of the SAME tetra mesh.
 vv=np.array(v);tt=np.array(t)
 for part,mask in [('skin',np.all(vv[tt,2]>=0,axis=1)),('rail_left',np.all(vv[tt,2]<=0,axis=1)&(vv[tt,1].mean(axis=1)<0)),('rail_right',np.all(vv[tt,2]<=0,axis=1)&(vv[tt,1].mean(axis=1)>0))]:
  face_map={}
  for x in tt[mask]:
   for f in ((x[1],x[2],x[3]),(x[0],x[3],x[2]),(x[0],x[1],x[3]),(x[0],x[2],x[1])):face_map.setdefault(tuple(sorted(f)),[]).append(f)
  stl(out/(part+'.stl'),q,[f[0] for f in face_map.values() if len(f)==1])
 (out/'config.json').write_text(json.dumps(c,indent=2));(out/'mesh.json').write_text(json.dumps(m));report=preflight(c,m,30,3);report['candidate']=name;report['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();(out/'checks.json').write_text(json.dumps(report,indent=2))
 # Exact triangulated CAD reference,not a misleading flat extrusion of curved parts.
 lines=['// Manufactured design reference only;NOT actual simulation. Dimensions mm.','// STEP/solid kernel assembly/fasteners/support strength NOT VERIFIED.','$fn=24;']
 for angle in c['palm']['angles_deg']:
  pts=np.array([world(c,p,angle) for p in v]);lines.append('polyhedron(points='+json.dumps(pts.tolist())+',faces='+json.dumps(surf)+',convexity=10);')
  for side in (-1,1):
   for x in c['tendon']['guide_stations']:
    p=world(c,[x,side*(width(c,x)/2+guide_outboard(c,x)),guide_normal(c,x)],angle);lines.append('translate('+json.dumps(p)+') sphere(r='+str(math.hypot(c['tendon']['guide_outer_radius'],1))+');')
 (out/'reference_assembly.scad').write_text('\n'.join(lines))
 paths=[]
 for label,points,color in [('Skin',np.array([world(c,[x,0,c['finger']['skin_thickness']]) for x in np.linspace(0,100,101)]),'#1673a0'),('Tendon',np.array([world(c,[x,width(c,x)/2+c['tendon']['outboard'],guide_normal(c,x)]) for x in [0]+c['tendon']['guide_stations']]),'#b34225')]:
  paths.append('<polyline fill="none" stroke="'+color+'" stroke-width="2" points="'+' '.join(f'{300+4*p[0]:.4f},{80-4*p[2]:.4f}' for p in points)+'"/>')
 (out/'orthographic.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600"><rect width="900" height="600" fill="white"/><text x="20" y="25">'+name+' — manufactured reference, NOT actual simulation</text><text x="20" y="50">L material arc100 mm;root R50 mm;3x120deg;Skin0.1 / Rail0.5 mm</text>'+''.join(paths)+'<text x="20" y="555">Side projection:blue Skin / red tendon. Guide/support solids,STEP,assembly NOT VERIFIED.</text></svg>')
 (out/'BOM.csv').write_text('part,quantity,status\nSkin,3,assumed manufactured stress-free reference\nBonded rail,6,assumed continuously bonded\nGuide bracket,36,10mg each assumed;actual support strength unverified\nEdge wire,6,radius0.25mm assumed;physical bend radius unverified\nPalm mount cartridge clamp fasteners actuator,1,existing baseline placeholders;new assembly NOT VERIFIED\n')
 return report

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--publish-actual-cases',action='store_true');p.add_argument('--publish-sector-cases',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);result={}
 if a.publish_sector_cases:
  for name,case in [('distal_A_sector_v8','distal_sector_single285'),('precurve_B_sector_v8','precurve_sector_single286'),('hybrid_C_sector_v8','hybrid_sector_single292')]:
   src=BASE/'results'/case;c=json.loads((src/'config.json').read_text());target=BASE/'meshes'/name;report=export(name,c,target);draw=BASE/'drawings'/name;draw.mkdir(exist_ok=False)
   for f in ('reference_assembly.scad','orthographic.svg','BOM.csv','checks.json','config.json'):shutil.copy2(target/f,draw/f)
   report['actual_case']=case;report['exact_config_bytes_equal']=hashlib.sha256((src/'config.json').read_bytes()).digest()==hashlib.sha256((target/'config.json').read_bytes()).digest();result[name]=report
  (out/'summary.json').write_text(json.dumps(dict(status='CAD_REFERENCE_CREATED_NOT_ASSEMBLY_VERIFIED',candidates=result),indent=2));print(json.dumps({k:v['exact_config_bytes_equal'] for k,v in result.items()}));return
 if a.publish_actual_cases:
  for name,case in [('distal_A_v7','distal_single261'),('precurve_B_v7','precurve_single262'),('hybrid_C_v7','hybrid_single268')]:
   src=BASE/'results'/case;c=json.loads((src/'config.json').read_text());target=BASE/'meshes'/name;report=export(name,c,target);draw=BASE/'drawings'/name;draw.mkdir(exist_ok=False)
   for f in ('reference_assembly.scad','orthographic.svg','BOM.csv','checks.json','config.json'):shutil.copy2(target/f,draw/f)
   report['actual_case']=case;report['exact_config_bytes_equal']=hashlib.sha256((src/'config.json').read_bytes()).digest()==hashlib.sha256((target/'config.json').read_bytes()).digest();result[name]=report
  (out/'summary.json').write_text(json.dumps(dict(status='CAD_REFERENCE_CREATED_NOT_ASSEMBLY_VERIFIED',candidates=result),indent=2));print(json.dumps({k:v['exact_config_bytes_equal'] for k,v in result.items()}));return
 for name,c in configs().items():result[name]=export(name,c,out/name)
 (out/'summary.json').write_text(json.dumps(dict(status='GEOMETRY_ONLY_NOT_ACTUATION',candidates=result),indent=2));print(json.dumps({k:[r['minimum_surface_gap_mm'] for r in v['records']] for k,v in result.items()}))
if __name__=='__main__':main()
