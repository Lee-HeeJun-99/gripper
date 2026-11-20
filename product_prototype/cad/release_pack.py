"""Manufacturing review pack,not a release-to-fabrication or physics certificate."""
import argparse,csv,json,math,subprocess,sys
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from manufacturing_assembly import BASE,evaluate,root_frame,cyl,transform,sector,sha,standoff_positions


def render(parts,shapes,path,exploded=False,title=None,footer=None):
 view=np.array([[1,-1,0],[1,1,2],[1,1,-1]],float);view/=np.linalg.norm(view,axis=1)[:,None]
 colors={'finger':'#56a9bf','eyelet':'#c79432','support':'#b8b27a','palm':'#a9b5be','mount':'#597c91','cartridge':'#408fa3','clamp':'#8baeb9','drive_deck':'#c3c7cc','drum':'#b25f59','motor_envelope':'#d7adc3','fastener_proxy':'#9a9a9a','standoff':'#a6a6a6'}
 triangles=[];facecolors=[];depth=[]
 for part,shape in zip(parts,shapes):
  q=shape.triangles.copy()
  if exploded:q[:,:,2]+=dict(palm=20,drive_deck=60,standoff=40,motor_envelope=90,drum=120,clamp=10).get(part['group'],0)
  projected=q@view.T;triangles.extend(projected[:,:,:2]);depth.extend(projected[:,:,2].mean(axis=1));facecolors.extend([colors.get(part['group'],'#999999')]*len(q))
 order=np.argsort(depth);triangles=np.asarray(triangles)[order];facecolors=np.asarray(facecolors)[order];fig,ax=plt.subplots(figsize=(9,9));ax.add_collection(PolyCollection(triangles,facecolors=facecolors,edgecolors='none'));xy=triangles.reshape(-1,2);ax.set_xlim(xy[:,0].min()-8,xy[:,0].max()+8);ax.set_ylim(xy[:,1].min()-8,xy[:,1].max()+8);ax.set_aspect('equal');ax.set_xlabel('Orthographic projection [mm]');ax.set_ylabel('Orthographic projection [mm]');ax.set_title(title if title is not None else 'ReGrip B3 MANUFACTURING CANDIDATE\n'+('EXPLODED design view:display-only offsets,NOT motion' if exploded else 'As-designed rest assembly,NOT SOFA grasp result'));fig.text(.03,.02,footer if footer is not None else '160 mesh parts/proxies;motor output interface,threads,wires,moving clearance,STEP and strength NOT qualified.',fontsize=8);fig.savefig(path,dpi=140);plt.close(fig)


def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',default='b3_manufacturing_spotface_v18');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'meshes'/a.candidate;draw=BASE/'drawings'/a.candidate;assembly=json.loads((src/'assembly_recipe.json').read_text());design=assembly['manufacturing_config'];cfg=assembly['baseline_config'];parts=assembly['parts'];shapes=[evaluate(p['shape']) for p in parts];byname={p['name']:s for p,s in zip(parts,shapes)};tools=[]
 # Explicit assumed cylindrical driver SHANKS only,no handles/wiring/supplier tool.
 for i,angle in enumerate(cfg['palm']['angles_deg']):
  R=root_frame(cfg,angle);S=sector(angle)
  configs=[(f'clamp_{y}',transform(cyl(2.25,6.2,26.2,(2.5,y)),R)) for y in (-14,14)]
  configs += [(f'retaining_{y}',transform(cyl(2.25,-35.1,-15.1,(-4,y)),R)) for y in (-14,14)]
  configs += [(f'deck_{r}_{y}',transform(cyl(2.25,23.1,55.1,(r,y)),S)) for r,y in standoff_positions(design['drive'])]
  for label,op in configs:
   tool=evaluate(op);hits=[]
   for part,s in zip(parts,shapes):
    if np.any(np.minimum(tool.bounds[1],s.bounds[1])-np.maximum(tool.bounds[0],s.bounds[0])<=0):continue
    intersection=trimesh.boolean.intersection([tool,s],engine='manifold',check_volume=True);volume=float(intersection.volume) if not intersection.is_empty else 0.
    if abs(volume)>1e-6:hits.append(dict(part=part['name'],signed_intersection_mm3=volume))
   tools.append(dict(finger=i,tool=label,assumed_shank_radius_mm=2.25,intersections=hits,scope='nominal cylindrical driver approach only;NOT full tool/hand/connector clearance or captive-nut insertion'))
 with (draw/'REGRIP_BOM.csv').open('w') as stream:
  w=csv.writer(stream);w.writerow(['CAD_instance','quantity','group','candidate_specification','material','source','measured_mass_kg','unit_cost_KRW','qualification'])
  for part in parts:
   name,group=part['name'],part['group'];spec='shared CAD recipe';material='UNSELECTED';url=''
   if group=='motor_envelope':spec='XL33020x34x26 supplier bbox ONLY;axis/horn/mount unverified';url='https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/'
   if group=='fastener_proxy':
    material='UNSELECTED FASTENER GRADE';spec='M3 nut AF5.5x2.4,unthreaded bore proxy' if '_nut_' in name else 'M3x'+('35' if '_deck_bolt_58_' in name else '20' if '_deck_bolt_' in name else '12')+' nominal cylinder/head proxy;thread/preload unverified'
   if group=='finger':spec='B3 L100 distal40deg start70;Skin0.1/Rail0.5;bondline absent in FEM'
   w.writerow([name,1,group,spec,material,url,'NULL','NULL','DESIGN_ONLY_NOT_RELEASED'])
  # Physical supplemental items NOT already represented by part instances.
  for row in [('wire',6,'nominal0.5mm baseline;alternative0.45mm requiresnewconfig'),('adhesive',1,'cut-to-fit rail/support bond coupons;actualquantity/coverage TBD'),('motor_horn_adapter',3,'supplier interface unresolved'),('TTL_interface_and_regulated_power',1,'U2D2 doesNOTsupply motorpower'),('wire_termination',6,'crimp/anchor retention unverified')]:w.writerow([row[0],row[1],'NOT_MODELED',row[2],'UNSELECTED','','NULL','NULL','PROCUREMENT_HOLD'])
 render(parts,shapes,draw/'assembly_design.png');render(parts,shapes,draw/'exploded_design.png',True)
 # Dimensioned local section schematic has explicit thickness enlargement only.
 section='''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="540"><rect width="1100" height="540" fill="white"/><g stroke="black" fill="none"><rect x="120" y="150" width="720" height="12"/><rect x="120" y="162" width="60" height="60"/><rect x="780" y="162" width="60" height="60"/><path d="M160 125 V100 H800 V125 M100 150 H70 V162 H100 M850 162 H900 V222 H850"/><rect x="120" y="320" width="260" height="80"/><rect x="280" y="258" width="100" height="60"/><circle cx="220" cy="360" r="17"/><circle cx="330" cy="360" r="17"/></g><g font-family="sans-serif" font-size="15"><text x="20" y="28">B3 v18 MANUFACTURING DESIGN:local root section,NOT simulation;dimensions mm</text><text x="330" y="90">Skin W24 root to12 tip;L100</text><text x="20" y="140">0.10</text><text x="910" y="200">Rail0.50</text><text x="230" y="195">Support saddle proposed0.05 bondline;adhesive NOT in B3 FEM</text><text x="120" y="245">Carrier x[-8,5],width36,back4;root clamp x[0,5],thickness3</text><text x="410" y="300">Root M3 clearance3.4;retaining x=-4,y=±14,normal axis</text><text x="410" y="335">Clamp bolts x=2.5,y=±14;M3x12 geometric proxies</text><text x="410" y="370">Normal head spotface R3 atlocalz=-12;preload NOT VERIFIED</text><text x="30" y="450">Palm OD128/ID60,t8;root radius50,tilt14deg,3x120deg;distal R42.9718,40deg,start70</text><text x="30" y="480">Provisional fit clearance0.2 is DESIGN intent,NOT proven print/machining tolerance.</text><text x="30" y="510">Drawing thickness enlarged for readability;full sizes/holes/parts use shared assembly_recipe.json.</text></g></svg>'''
 (draw/'root_section_dimensioned.svg').write_text(section)
 # True mm1:1 profile template,not a fabricated neutral-axis forming result.
 from generate import reference_local
 points=[reference_local(cfg,[float(x),0,0]) for x in np.linspace(0,100,201)]
 with (draw/'finger_reference_profile.dxf').open('w') as f:
  f.write('0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n0\nLWPOLYLINE\n100\nAcDbEntity\n8\nMANUFACTURED_REFERENCE_NOT_MOTION\n100\nAcDbPolyline\n90\n201\n70\n0\n')
  for x,_,z in points:f.write(f'10\n{x:.12g}\n20\n{z:.12g}\n')
  f.write('0\nENDSEC\n0\nEOF\n')
 bounds=np.array([s.bounds for s in shapes]);result=dict(status='MANUFACTURING_REVIEW_PACK_NOT_FABRICATION_RELEASE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),candidate=a.candidate,source_recipe_sha256=sha(src/'assembly_recipe.json'),CAD_instances=len(parts),fastener_proxy_instances=sum(p['group']=='fastener_proxy' for p in parts),driver_shank_checks=tools,assembly_AABB_mm=[bounds[:,0,:].min(axis=0).tolist(),bounds[:,1,:].max(axis=0).tolist()],contact_pad='NOT MODELED',wire_full_routing='NOT MODELED:shared finger guide path only;motorlead-in unresolved',STEP_generated=False,BRep_verified=False,material_strength_verified=False,fabrication_ready=False,files={p.name:sha(p) for p in draw.iterdir() if p.is_file()})
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));(draw/'release_review.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],CAD_instances=len(parts),tool_paths=len(tools),tool_paths_with_intersection=sum(bool(t['intersections']) for t in tools),assembly_AABB_mm=result['assembly_AABB_mm']),indent=2))
if __name__=='__main__':main()
