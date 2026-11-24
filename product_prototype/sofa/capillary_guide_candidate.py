"""Supplier-dimensioned thin metal ferrule replaces bulky finite rings.
Not a chamfer/OD sweep: ONE named16RW tube, same centres, axes and cable law.
Independent convex support/slab radial projection checks bore obstruction and
nominal bond overlap. Actual bond strength, cut finish and tolerances unknown.
"""
import argparse,csv,itertools,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import ConvexHull
from analyse import BASE,sha
from finite_hardware_grasp_pilot import flat

SPEC=dict(source_url='https://www.vitaneedle.com/products/small-diameter-tubing/master-tubing-gauge-chart',retrieved_date='2026-11-24',row='16RW',OD_in=.065,ID_in=.047,OD_tolerance_in=.0005,ID_tolerance_in=.0015,material='Manufacturer chart: full-hard TIG welded/drawn304SS;316SS also listed. NOT measured ReGrip material.',cut_length_mm=2.,cut_length_source='ReGrip design assumption, NOT supplier length tolerance',price='UNKNOWN',domestic_stock='UNKNOWN',bond_strength='NOT MEASURED',wire_friction='NOT MEASURED')

def support_bore_radial_min(v,faces,c,basis,half_length=.001):
 local=(v-c)@basis;hull=trimesh.Trimesh(local,faces,process=False);points=list(local[np.abs(local[:,0])<=half_length])
 for ia,ib in hull.edges_unique:
  a,b=local[ia],local[ib]
  if a[0]==b[0]:continue
  for x in (-half_length,half_length):
   t=(x-a[0])/(b[0]-a[0])
   if 0<=t<=1:points.append(a+t*(b-a))
 if len(points)<3:raise ValueError('no finite support in tube slab; connection unproven')
 yz=np.unique(np.array(points)[:,1:],axis=0);poly=yz[ConvexHull(yz).vertices];edge=np.roll(poly,-1,axis=0)-poly
 cross=edge[:,0]*(-poly[:,1])-edge[:,1]*(-poly[:,0]);inside=np.all(cross>=0) or np.all(cross<=0)
 u=np.clip(-(poly*edge).sum(1)/(edge*edge).sum(1),0,1);near=poly+u[:,None]*edge;d=np.linalg.norm(near,axis=1)
 return 0. if inside else float(d.min())

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/dispatch_finite_holding1586';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();ro=SPEC['OD_in']*.0254/2;ri=SPEC['ID_in']*.0254/2;ro_min=(SPEC['OD_in']-SPEC['OD_tolerance_in'])*.0254/2;ri_max=(SPEC['ID_in']+SPEC['ID_tolerance_in'])*.0254/2;records=[]
 for i in range(3):
  for j in range(2):
   cable=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']")
   for k in range(6):
    ring=cable.find(f"Node[@name='eyelet{k}']");v=np.fromstring(ring.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);faces=np.fromstring(ring.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);n=len(v)//4;c=v.mean(0);axis=v[2*n:].mean(0)-v[:2*n].mean(0);axis/=np.linalg.norm(axis);ey=v[0]-c;ey-=axis*(ey@axis);ey/=np.linalg.norm(ey);basis=np.stack([axis,ey,np.cross(axis,ey)],axis=1);local=(v-c)@basis;rad=np.linalg.norm(local[:,1:],axis=1);outer=np.isclose(rad,.0015,rtol=0,atol=1e-12);assert outer.sum()==2*n
    local[:,1:]*=np.where(outer,ro,ri)[:,None]/rad[:,None];newv=local@basis.T+c;mesh=trimesh.Trimesh(newv,faces,process=False);assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
    for tag in ('MechanicalObject','MeshTopology'):ring.find(tag).set('position',flat(newv))
    support=cable.find(f"Node[@name='support{k}']");sv=np.fromstring(support.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);sf=np.fromstring(support.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);rmin=support_bore_radial_min(sv,sf,c,basis)
    records.append(dict(finger=i,cable=j,station=k,support_min_radius_in_bore_slab_mm=rmin*1000,bore_support_clearance_at_MAX_ID_mm=(rmin-ri_max)*1000,support_wall_reach_at_MIN_OD_mm=(ro_min-rmin)*1000,old_ring_volume_mm3=float(trimesh.Trimesh(v,faces,process=False).volume)*1e9,new_ring_volume_mm3=float(mesh.volume)*1e9))
    if k==5:mesh.export(out/f'f{i}c{j}_terminal_tube_metres.stl')
 for node in root.iter():
  for key,value in list(node.attrib.items()):node.set(key,value.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');c=json.loads((src/'config.json').read_text());c['tendon']['guide_outer_radius']=ro*1000;c['tendon']['guide_hole_radius']=ri*1000;c['tendon']['guide_length_mm']=2.;(out/'config.json').write_text(json.dumps(c,indent=2));(out/'supplier_dimensions.json').write_text(json.dumps(SPEC,indent=2))
 ok=all(r['bore_support_clearance_at_MAX_ID_mm']>0 and r['support_wall_reach_at_MIN_OD_mm']>0 for r in records)
 d=dict(status='READY_GEOMETRY_REPLAY_ONLY' if ok else 'FAIL_CAPILLARY_SUPPORT_BORE_OR_CONNECTION',parts=records,OD_mm=2*ro*1000,ID_mm=2*ri*1000,radial_wall_nominal_mm=(ro-ri)*1000,wire_radius_mm=.25,minimum_manufacturer_ID_straight_radial_wire_clearance_mm=(SPEC['ID_in']-SPEC['ID_tolerance_in'])*25.4/2-.25,scope='ONE supplier16RW dimensional architecture, all36rings closed finite meshes, same centres/axes/cable input and all72hardware collisionfeatures. Original finite support solids retained: projection of their convex slab gives bore exclusion and radial ring-wall reach only. NOT joint strength/retention/tolerance or finite-wire bend/sliding qualification. Parent mass/inertia deliberately inherited for geometry sensitivity, NOT recalibrated304 density. No Native run yet.',SDK='/home/ubuntu/SOFA/v26.06.00',actual_Native_execution=False,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),supplier=SPEC)
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='parts'},indent=2));print('fit minima',min(r['bore_support_clearance_at_MAX_ID_mm'] for r in records),min(r['support_wall_reach_at_MIN_OD_mm'] for r in records))
if __name__=='__main__':main()
