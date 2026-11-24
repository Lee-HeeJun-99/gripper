"""Finite closed-sleeve mechanism preflight, NOT adopted fabrication design.
Source old capillary geometry is immutable. New carrier, keyed sleeve and
wire windows are actual CSG solids; no collision shell removed to make fit.
"""
import argparse,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from finite_support_sat import sat
from yoke_bond_material_audit import surface

def translated_box(extents,centre):
 return trimesh.creation.box(extents,transform=trimesh.transformations.translation_matrix(centre))
def cylinder_x(radius,length,centre=(0,0,0)):
 T=trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]);T[:3,3]=centre
 return trimesh.creation.cylinder(radius=radius,height=length,sections=64,transform=T)
def wire(a,b,r):
 d=b-a;T=trimesh.geometry.align_vectors([0,0,1],d/np.linalg.norm(d));T[:3,3]=(a+b)/2
 # Trimesh primitive construction drops cap triangles at tiny metre scale.
 # Build topology in mm, then scale without remeshing; no physical size change.
 tube=trimesh.creation.cylinder(radius=r*1000,height=np.linalg.norm(d)*1000,sections=64);tube.apply_scale(.001);tube.apply_transform(T);assert tube.is_volume
 return tube

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/capillary_hold1700';root=ET.parse(src/'scene.scn').getroot();obj=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3];records=[];newparts=[];oldparts=[];stroke=.002;ro=.8255;hole=.5969;carrier_size=2.4;clearance=.1;wall=.8;window_radius=hole+clearance
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");anchors=np.fromstring(parent.find("Node[@name='anchors']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);theta=np.deg2rad(i*120);et=np.array([-np.sin(theta),np.cos(theta),0])
  for j in range(2):
   cable=parent.find(f"Node[@name='cable{j}']")
   for child in cable.findall('Node'):
    if child.get('name','').startswith(('eyelet','support')) and child.get('name')!='support5':oldparts.append((i,j,child.get('name'),surface(child)))
   tube=surface(cable.find("Node[@name='eyelet5']"));support=surface(cable.find("Node[@name='support5']"));v=tube.vertices;n=len(v)//4;centre=v.mean(0);axis=v[2*n:].mean(0)-v[:2*n].mean(0);axis/=np.linalg.norm(axis);side=np.sign(centre@et);slide=-side*et;slide-=axis*(axis@slide);slide/=np.linalg.norm(slide);basis=np.stack([axis,slide,np.cross(axis,slide)],axis=1)
   local_support=trimesh.Trimesh((support.vertices-centre)@basis*1000,support.faces,process=False)
   shell=translated_box([carrier_size+2*clearance+2*wall,carrier_size+stroke*1000+2*wall,carrier_size+2*clearance+2*wall],[0,stroke*500,0]);cavity=translated_box([carrier_size+2*clearance,carrier_size+stroke*1000,carrier_size+2*clearance],[0,stroke*500,0]);window=trimesh.boolean.union([cylinder_x(window_radius,10,(0,0,0)),cylinder_x(window_radius,10,(0,stroke*1000,0)),translated_box([10,stroke*1000,2*window_radius],[0,stroke*500,0])],engine='manifold')
   housing=trimesh.boolean.difference([trimesh.boolean.union([shell,local_support],engine='manifold'),cavity,window],engine='manifold');carrier=trimesh.boolean.difference([translated_box([carrier_size]*3,[0,0,0]),cylinder_x(ro+.05,6)],engine='manifold');assert all(m.is_watertight and m.volume>0 for m in (housing,carrier))
   world=lambda mesh:trimesh.Trimesh(mesh.vertices*.001@basis.T+centre,mesh.faces,process=False)
   hg=world(housing);cg=world(carrier);feet=anchors[j*18+15:j*18+18];contains=housing.contains((feet-centre)@basis*1000);fits=[]
   for travel in (0,stroke/2,stroke):
    moved=carrier.copy();moved.apply_translation([0,travel*1000,0]);hit=trimesh.boolean.intersection([moved,housing],engine='manifold');fits.append(dict(travel_mm=travel*1000,positive_fit_intersection_mm3=float(max(0.,hit.volume))))
   ring_inside_carrier=trimesh.boolean.intersection([tube,cg],engine='manifold');minimum=1.;gaps={}
   for name,m in [('housing',hg),('carrier',cg)]:
    near=trimesh.triangles.closest_point(m.triangles,np.repeat(obj[None],len(m.faces),axis=0));g=float(np.linalg.norm(near-obj,axis=1).min()-.03);gaps[name]=g*1000;minimum=min(minimum,g);m.export(out/f'f{i}_c{j}_{name}_m.stl');newparts.append((i,j,name,m))
   # Positive intersection of an INSCRIBED64facet tube is a valid witness of
   # a straight circular wire conflict, not a claim no bent wire could fit.
   path=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);incoming=wire(path[-2],path[-1],.00025);wire_hits=[]
   for name,m in [('housing',hg),('carrier',cg)]:
    hit=trimesh.boolean.intersection([incoming,m],engine='manifold');wire_hits.append(dict(part=name,straight_wire_inscribed_intersection_mm3=float(max(0.,hit.volume))*1e9))
   records.append(dict(finger=i,cable=j,guide=5,initial_centre_m=centre.tolist(),slide_axis_world=slide.tolist(),basis=basis.tolist(),housing_connected_components=int(housing.body_count),carrier_connected_components=int(carrier.body_count),three_original_feet_retained=contains.tolist(),carrier_stroke_fit=fits,ring_carrier_intersection_mm3=float(max(0.,ring_inside_carrier.volume))*1e9,initial_new_object_gaps_mm=gaps,wire_conflicts=wire_hits))
 # Every NEW/foreign hardware pair; exact convex separation is sufficient,
 # envelope near-overlap remains unqualified unless actual solid intersection.
 pairs=[]
 for k,(i,j,name,m) in enumerate(newparts):
  for fi,fj,fn,n in oldparts+newparts[k+1:]:
   if i==fi:continue
   if np.any(m.bounds[1]+.0002<n.bounds[0]) or np.any(n.bounds[1]+.0002<m.bounds[0]):continue
   hm=m.convex_hull;hn=n.convex_hull;gap,status=sat(hm.vertices,hn.vertices,hm.faces,hn.faces,hm.edges_unique,hn.edges_unique)
   if gap>.0002:continue
   hit=trimesh.boolean.intersection([m,n],engine='manifold');pairs.append(dict(left=[i,j,name],right=[fi,fj,fn],separating_axis_gap_mm=gap*1000,convex_status=status,actual_solid_intersection_mm3=float(max(0.,hit.volume))*1e9))
 failed_object=any(min(r['initial_new_object_gaps_mm'].values())<.2 for r in records);badfit=any(any(x['positive_fit_intersection_mm3']>0 for x in r['carrier_stroke_fit']) or not all(r['three_original_feet_retained']) or r['housing_connected_components']!=1 for r in records);badwire=any(any(x['straight_wire_inscribed_intersection_mm3']>0 for x in r['wire_conflicts']) for r in records)
 d=dict(status='REJECTED_CLOSED_SLEEVE_INITIAL_GEOMETRY' if failed_object or badfit or badwire or pairs else 'INITIAL_CLOSED_SLEEVE_GEOMETRY_ONLY_NOT_NATIVE_READY',failed_object_or_buffer=failed_object,failed_nominal_stroke_or_feet=badfit,straight_incoming_wire_conflict=badwire,foreign_buffer_uncertainties_or_penetrations=pairs,records=records,parameters_mm=dict(tube_OD=2*ro,tube_ID=2*hole,tube_length=2,wire_diameter=.5,stroke=stroke*1000,carrier_size=carrier_size,transverse_fit_clearance_per_side=clearance,housing_wall=wall,tube_mount_clearance_per_radius=.05,wire_window_radius=window_radius),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scope='Actual separate CSG prototype, no overwrite of originalCAD/Scene. Stroke2mm is a studied conditional prototype, exceeds1753fixed-pose1.879mm necessary bound but is NOT dynamically proven. Explicit nominal clearances/walls are research assumptions, not manufacturer tolerances. Split lid/fasteners/retention/friction/strength NOT MEASURED; one-piece closed housing is a geometry envelope, not completed assembly. Original six terminal supports replaced only in this candidate. No new Native grasp executed if initial object/wire/hardware gate fails. Three carriage samples per guide are not continuous/swept or actual FEM motion.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('records','foreign_buffer_uncertainties_or_penetrations')},indent=2))
if __name__=='__main__':main()
