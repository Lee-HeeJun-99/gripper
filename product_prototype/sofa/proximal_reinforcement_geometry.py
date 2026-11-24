"""Footprint-preserving finite proximal backing;not selected hardware material.

Adds0.125mm behind BOTH existing2mm rails over0–70mm. All original material
nodes and guide anchors stay unchanged. Perfect bond and effective density are
research assumptions. No terminal/thickness/force sweep is performed.
"""
import argparse,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from mechanism_candidates import world,stl,width
from contact_layer_union import exterior

def section_I(w,h):
 area=np.array([w*.1,2*h,2*h]);z=np.array([.05,-h/2,-h/2]);neutral=float(area@z/area.sum());I=w*.1**3/12+2*(2*h**3/12)+float(area@((z-neutral)**2));return I
def boxgap(a,b):return float(np.linalg.norm(np.maximum(0,np.maximum(a.min(0)-b.max(0),b.min(0)-a.max(0)))))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';c=json.loads((src/'config.json').read_text());mesh=json.loads((src/'mesh.json').read_text());local=np.array(mesh['local_positions_mm']);parents=np.flatnonzero((local[:,0]<=70)&(local[:,2]==-.5));assert len(parents)==60;points=np.array([p+[0,0,d] for p in local[parents] for d in (0,-.125)]);idx=lambda i,j,k:2*(4*i+j)+k;tets=[]
 for i in range(14):
  for j in (0,2):
   box=[idx(i+a,j+b,k) for a,b,k in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1))]
   for pat in ((0,1,3,7),(0,3,2,7),(0,2,6,7),(0,6,4,7),(0,4,5,7),(0,5,1,7)):
    t=[box[k] for k in pat]
    if np.linalg.det((points[t[1:]]-points[t[0]]).T)<0:t[1],t[2]=t[2],t[1]
    tets.append(t)
 faces={}
 for b,c1,d,e in tets:
  for f in ((c1,d,e),(b,e,d),(b,c1,e),(b,d,c1)):faces.setdefault(tuple(sorted(f)),[]).append(f)
 surf=[f[0] for f in faces.values() if len(f)==1];tet=np.array(tets);root=ET.parse(src/'scene.scn').getroot();qbase=[np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3) for i in range(3)];oldt=np.array(mesh['tetrahedra']);volume0=float(np.linalg.det((qbase[0][oldt[:,1:]]-qbase[0][oldt[:,0,None]]).transpose(0,2,1)).sum()/6);rho=.001/volume0;young=np.unique(np.fromstring(root.find("Node[@name='finger0']/TetrahedronFEMForceField").get('youngModulus'),sep=' '));assert len(young)==1;records=[];reference=[]
 for i,angle in enumerate((0,120,240)):
  q=np.array([world(c,p,angle) for p in points])*.001;reference.append(q.tolist());assert abs(q[::2]-qbase[i][parents]).max()<1e-15;det=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));near=trimesh.triangles.closest_point(q[np.array(surf)],np.repeat(np.array([0.,0.,-.065])[None],len(surf),axis=0));gap=float((np.linalg.norm(near-[0,0,-.065],axis=1)-.03).min());guides=[];wires=[];other=[]
  for j in range(3):
   if i!=j:other.append(boxgap(q,qbase[j]))
   for cable in range(2):
    n=root.find(f"Node[@name='guides{j}']/Node[@name='cable{cable}']");route=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);pull=np.fromstring(n.find('CableConstraint').get('pullPoint'),sep=' ')
    for g in route:
     closest=trimesh.triangles.closest_point(q[np.array(surf)],np.repeat(g[None],len(surf),axis=0));guides.append(float(np.linalg.norm(closest-g,axis=1).min()-np.hypot(.0015,.001)))
    path=np.vstack([pull,route])
    for k in range(len(path)-1):wires.append(boxgap(q,path[k:k+2])-.00025)
  pairs=np.fromstring(root.find(f"Node[@name='finger{i}']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);assert (pairs[:,0]==1).sum()==36
  records.append(dict(finger=i,minimum_initial_extension_sphere_gap_m=gap,minimum_all_guide_proxy_gap_m=min(guides),minimum_wire_AABB_capsule_lower_bound_m=min(wires),minimum_other_finger_AABB_lower_bound_m=min(other),minimum_signed_tet_determinant_m3=float(det.min()),volume_m3=float(det.sum()/6),mass_kg=float(det.sum()/6*rho),unchanged_guide_anchors=36));stl(out/f'reinforcement_finger{i}_reference.stl',q*1000,surf)
 g=dict(kind='proximal_backing_reinforcement',local_positions_mm=points.tolist(),bottom_Skin_parent_indices=parents.tolist(),attached_parent_scope='LEGACY FIELD NAME:these are RailBOTTOM nodes,z-.5,NOT Skin',tetrahedra=tets,triangles=surf,world_reference_m=reference,records=records,expected_interface_triangles=56,root_free_fixed_indices=np.flatnonzero(points[1::2,0]<=5).tolist(),material=dict(young_modulus_Pa=float(young[0]),poisson_ratio=.3,density_kg_m3=rho,scope='E/nu copied existing nativeassumptions;density derived from1g/originalactualFEMvolume,NOT measured material'))
 union=exterior(mesh,g);(out/'mesh.json').write_text(json.dumps(g));(out/'union_surface.json').write_text(json.dumps(union,indent=2));safe=all(r['minimum_initial_extension_sphere_gap_m']>=.0002 and min(r['minimum_all_guide_proxy_gap_m'],r['minimum_wire_AABB_capsule_lower_bound_m'],r['minimum_other_finger_AABB_lower_bound_m'],r['minimum_signed_tet_determinant_m3'])>0 for r in records)
 d=dict(status='PASS_MODELED_INITIAL_REINFORCEMENT_GEOMETRY' if safe else 'REJECT_INITIAL_REINFORCEMENT_GEOMETRY',records=records,original_core_volume_m3=volume0,material=g['material'],nominal_rail_only_I_ratio=(.625/.5)**3,composite_section_I_ratios=[dict(station_mm=x,ratio=section_I(width(c,x),.625)/section_I(width(c,x),.5)) for x in (0,50,70)],interface_triangles_cancelled=union['interface_triangles_cancelled'],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','mesh.json','config.json')},scope='One finite0.125mmproximalreinforcement,original2mmrailfootprint/108guideanchors retained. Addsvolume/mass,not equalvolume efficiency. Perfectbond/rootclampedmaterialrange0–5mm are assumptions. ActualClamp/support fabricationandmovinginterference NOTQUALIFIED;sectionI ratios are referencealgebra,NOT Native stiffness.',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
