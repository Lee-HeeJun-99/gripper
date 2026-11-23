"""Support-to-Skin/Rail geometry provenance;not a bonded or tied physical joint."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,root_frame

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'results/product_eyelet_keeper894/full_assembly_recipe.json';cfgfile=BASE/'meshes/b3_manufacturing_bore_v21/assembly_recipe.json';cfg=json.loads(cfgfile.read_text())['baseline_config'];M=root_frame(cfg,0);parts=json.loads(src.read_text())['parts'];support=evaluate(next(p['shape'] for p in parts if p['name']=='f0_c1_s0_support'));local=(support.vertices-M[:3,3])@M[:3,:3];records=[]
 for name in ('f0_skin','f0_rail_left','f0_rail_right'):
  body=evaluate(next(p['shape'] for p in parts if p['name']==name));closest,dist,tri=trimesh.proximity.closest_point(body,support.vertices);index=int(np.argmin(dist));intersection=trimesh.boolean.intersection([support,body],engine='manifold');pointlocal=(support.vertices[index]-M[:3,3])@M[:3,:3];nearestlocal=(closest[index]-M[:3,3])@M[:3,:3]
  records.append(dict(target=name,minimum_SUPPORT_VERTEX_sampled_distance_mm=float(dist[index]),support_vertex_world_mm=support.vertices[index].tolist(),target_closest_point_world_mm=closest[index].tolist(),support_vertex_finger_coordinates_mm=pointlocal.tolist(),target_point_finger_coordinates_mm=nearestlocal.tolist(),target_triangle_id=int(tri[index]),CSG_volume_mm3=float(intersection.volume) if len(intersection.faces) else 0.,CSG_faces=len(intersection.faces)))
 result=dict(status='ATTACHMENT_GEOMETRY_AUDIT_NOT_JOINT_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,cfgfile,BASE/'cad/manufacturing_assembly.py',BASE/'cad/generate.py')},records=records,support_finger_coordinate_bounds_mm=np.array([local.min(axis=0),local.max(axis=0)]).tolist(),nominal_rail_back_coordinate_mm=-cfg['finger']['rail_thickness'],actual_joint_type=None,actual_joint_strength_N=None,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='All actual Support vertices queried against actual Skin/Rail triangle meshes in mm,plus true solid CSG. Vertex-sampled distance is NOT whole triangle-triangle clearance or contactarea. Manufactured root frame appropriate to localstraight region;not a dynamic shape. Nearcoincidence with Rail is NOT a bonded joint,load transfer or direct Skin contact. No connector force or material data invented.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
