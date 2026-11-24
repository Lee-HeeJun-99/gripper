"""One rear-plane support reroute after actual finite-wire obstruction1408.
Leaves bore and wire radii unchanged;cannot promote unresolved bore to PASS.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from opposed_tendon_coupon import segment_bound
def witness(supports,wires):
 best=None
 for i,(a,b) in enumerate(supports):
  n=max(1,int(np.ceil(np.linalg.norm(b-a)/.25)));P=np.linspace(a,b,n+1)
  for j,k,c,d in wires:
   D=d-c;s=np.clip((P-c)@D/(D@D),0,1);Q=c+s[:,None]*D;dist=np.linalg.norm(P-Q,axis=1);z=int(np.argmin(dist));lower=float(dist[z]-.5-np.linalg.norm(b-a)/(2*n))
   if best is None or lower<best['lower_bound_mm']:best=dict(support_segment=i,wire_route=j,wire_segment=k,lower_bound_mm=lower,sampled_axis_distance_mm=float(dist[z]),actual_sample_capsule_gap_mm=float(dist[z]-.5),support_axis_point_mm=P[z].tolist(),wire_axis_point_mm=Q[z].tolist())
 return best
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/four_route_gate1408/summary.json';g=json.loads(src.read_text());routes=[np.array(r['route_mm']) for r in g['routes']];wires=[(j,k,p,q) for j,route in enumerate(routes) for k,(p,q) in enumerate(zip(route[:-1],route[1:]))];old=[(np.array(a),np.array(b)) for a,b in g['support_B_segments_mm']];A=g['support_A_segments_mm'];new=[];records=[]
 for j,r in enumerate(g['routes']):
  for k,wall in enumerate(np.array(r['outer_wall_attachment_mm'])):
   foot=np.array(A[6*j+k][0]);n=(routes[j%2][k+1]-routes[2+j%2][k+1])/6;assert abs(np.linalg.norm(n)-1)<1e-12;rootpost=foot-5.5*n;endpost=wall-(9 if j<2 else 3)*n;new.extend([(foot,rootpost),(rootpost,endpost),(endpost,wall)]);records.append(dict(route=j,guide=k,foot_mm=foot.tolist(),rear_root_mm=rootpost.tolist(),rear_wall_mm=endpost.tolist(),outer_wall_mm=wall.tolist()))
 before=witness(old,wires);after=witness(new,wires);root=ET.parse(BASE/'results/opposed_nonuniform_mid1398/scene.scn').getroot();f=root.find("Node[@name='finger0']");q=np.fromstring(f.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;s=f.find("Node[@name='skinCollision']");ids=np.fromstring(s.find('SubsetMapping').get('indices'),sep=' ',dtype=int);tri=q[ids[np.fromstring(s.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)]];skin=min(segment_bound(a,b,tri,.25,.25) for a,b in new);length0=sum(np.linalg.norm(b-a) for a,b in old);length1=sum(np.linalg.norm(b-a) for a,b in new);d=dict(status='PASS_REAR_SUPPORT_WIRE_SKIN_PROXY_ONLY' if min(after['lower_bound_mm'],skin)>0 else 'REJECT_REAR_SUPPORT_ROUTE',previous_collision_witness=before,rear_support_wire_witness=after,rear_support_skin_lower_bound_mm=skin,previous_total_rod_length_mm=float(length0),new_total_rod_length_mm=float(length1),nominal_added_cylinder_volume_mm3=float(np.pi*.25**2*(length1-length0)),existing_straight_bore_margin_mm=g['minimum_straight_bore_wire_margin_mm'],four_route_overall='REJECTED_UNRESOLVED_STRAIGHT_BORE_AND_BEND_RADIUS',records=records,support_segments_mm=[(a.tolist(),b.tolist()) for a,b in new],Native_four_cable='NOT RUN',scope='ONE backplane−6mm reroute of finiteOD.5 rods,samewire/bore/eyeletgeometry. Actualsampledistance<sumradii proves priorobstruction;positive Lipschitzlowerbounds prove only checkedinitialwire/Skin separation. Not union-solidvolume,massCOM,inertia,rodstrength,manufacturing,fullassembly/interfinger/sweptcollision orborePASS.',physical_validation='NOT QUALIFIED',input_hashes={'four_route_summary':sha(src),'scene':sha(BASE/'results/opposed_nonuniform_mid1398/scene.scn')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('records','support_segments_mm','input_hashes')}))
if __name__=='__main__':main()
