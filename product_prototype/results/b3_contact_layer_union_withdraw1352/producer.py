"""Native FEM finite contact-layer mechanism hypothesis;no custom solver.

Baseline1298 remains unmodified. Added layer bottom is exactly subset-bonded to
Skin,top is independently deformable. Added mass/material are explicit assumptions.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def flat(a):return ' '.join(format(float(v),'.17g') for v in np.asarray(a).ravel())
def add(n,tag,**kw):return ET.SubElement(n,tag,{k:str(v) for k,v in kw.items()})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=[.0025,.05,.6,1.2],default=.05);p.add_argument('--pilot');p.add_argument('--no-contact-control',action='store_true');p.add_argument('--exterior-union',action='store_true');a=p.parse_args();src=BASE/'results/b3_railback_grasp1001298';geom=BASE/'results/b3_contact_layer_geometry1336';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);g=json.loads((geom/'mesh.json').read_text());design=json.loads((geom/'summary.json').read_text());assert design['status']=='PASS_LIMITED_INITIAL_GEOMETRY';tree=ET.parse(src/'scene.scn');root=tree.getroot();original=ET.tostring(root);added=[]
 for i in range(3):
  q=np.array(g['world_reference_m'][i]);free=add(root,'Node',name=f'layerFree{i}');added.append(free);add(free,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q[1::2]))
  layer=add(root,'Node',name=f'contactLayer{i}');added.append(layer);add(layer,'MeshTopology',name='topology',position=flat(q),tetrahedra=flat(g['tetrahedra']),triangles=flat(g['triangles']));add(layer,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q));add(layer,'UniformMass',totalMass=g['records'][i]['mass_kg']);add(layer,'TetrahedronFEMForceField',name='layerFEM',method='large',youngModulus=1e6,poissonRatio=.3)
  pairs=[]
  for k,parent in enumerate(g['bottom_Skin_parent_indices']):pairs.extend([1,parent,0,k])
  add(layer,'SubsetMultiMapping',template='Vec3d,Vec3d',input=f'@../layerFree{i}/dofs @../finger{i}/dofs',output='@dofs',indexPairs=' '.join(map(str,pairs)),mapMatrices=1)
  add(layer,'TriangleCollisionModel',group=1);add(layer,'LineCollisionModel',group=1);add(layer,'PointCollisionModel',group=1);add(layer,'NativePointJournal',body='@dofs',filename=str(out/f'contact_layer{i}.csv'))
 # Baseline graph remains exactly present;no original collision or physical input removed.
 for n in added:root.remove(n)
 assert ET.tostring(root)==original
 for n in added:root.append(n)
 if a.exterior_union:
  from contact_layer_union import apply_union
  union=apply_union(root,json.loads((src/'mesh.json').read_text()),g,out);(out/'union_surface.json').write_text(json.dumps(union,indent=2))
 if a.no_contact_control:root.remove(root.find('CollisionPipeline'))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'pad_mesh.json').write_bytes((geom/'mesh.json').read_bytes())
 for f in ('mesh.json','config.json'):(out/f).write_bytes((src/f).read_bytes())
 forecast=30.
 if a.duration>.05:
  if not a.pilot:raise ValueError('actual same-mechanism pilot required')
  pm=json.loads((BASE/'results'/a.pilot/'preflight.json').read_text());pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert pr['status']=='BOUNDED_EXECUTION_ONLY' and pm['duration_s']<a.duration
  assert pm.get('exterior_union',False)==a.exterior_union and pm.get('no_contact_control',False)==a.no_contact_control
  if a.exterior_union:
   clearance=BASE/'results/contact_layer_initial_clearance1350/summary.json';assert json.loads(clearance.read_text())['status']=='PASS_MODELED_INITIAL_NEW_PART_SEPARATION'
  factor=4 if pm['duration_s']==.05 else 2
  forecast=pr['process']['runtime_s']*a.duration/pm['duration_s']*factor
  if forecast>420:raise ValueError('bounded contact forecast exceeds420s')
 dt=float(root.get('dt'));steps=round(a.duration/dt);cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')];bins={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')}
 limit=30 if a.no_contact_control or (a.exterior_union and a.duration<=.05) else 420
 pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=bins,scene_sha256=sha(out/'scene.scn'),baseline_scene_sha256=sha(src/'scene.scn'),geometry_sha256=sha(geom/'mesh.json'),layer_design=design['design'],baseline_graph_unchanged=not a.no_contact_control,duration_s=a.duration,dt_s=dt,forecast_s=forecast,child_limit_s=limit,memory_GiB=4,no_contact_control=a.no_contact_control,classification='NO_CONTACT_COUPLING_DIAGNOSTIC_NOT_GRASP' if a.no_contact_control else 'EXPLORATORY_CONTACT_LAYER_NOT_JAMMING',hypothesis='Finite separately deformable layer might distribute actual contact beyond distal Skin-tip edge. No improved force/contact coverage assumed.',scope='Adds finite material and mass with ideal perfect bond;not equal-volume efficiency comparison. Control removes CollisionPipeline ONLY to isolate coupled FEM/mapping,no Holding claim.' if a.no_contact_control else 'Adds finite material and mass with ideal perfect bond;not equal-volume efficiency comparison. No original collision disabled.',physical_validation='NOT QUALIFIED')
 pre['exterior_union']=a.exterior_union
 if a.exterior_union:pre.update(baseline_graph_unchanged=False,collision_change='Cancel24 exactly shared bond interface triangles;retain all other originalSkin/Rail exterior and finite hardware. New composite exterior replaces separate material collision nodes. Not contact removal to claim Holding.',union_sha256=sha(out/'union_surface.json'))
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',limit);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));quality=[];bond=[];counts=[]
 for i in range(3):
  film=list(csv.DictReader((out/f'finger{i}.csv').open())) if (out/f'finger{i}.csv').exists() else [];pad=list(csv.DictReader((out/f'contact_layer{i}.csv').open())) if (out/f'contact_layer{i}.csv').exists() else [];counts.append([len(film),len(pad)])
  for label,rows,q0,tet,key in [('SkinRail',film,np.fromstring(root.find(f"./Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3),np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']),'q_m'),('contactLayer',pad,np.array(g['world_reference_m'][i]),np.array(g['tetrahedra']),'q')]:
   if not rows:continue
   q=np.array([np.fromstring(r[key],sep=' ').reshape(-1,3) for r in rows]);ratio=np.linalg.det((q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2))/np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));bad=np.argwhere(ratio<=0);quality.append(dict(finger=i,part=label,minimum_saved_volume_ratio=float(ratio.min()),finite=bool(np.isfinite(q).all()),first_inverted_sample=int(bad[0,0]) if len(bad) else None))
  if film and pad and len(film)==len(pad):
   err=max(float(abs(np.fromstring(p['q'],sep=' ').reshape(-1,3)[::2]-np.fromstring(f['q_m'],sep=' ').reshape(-1,3)[g['bottom_Skin_parent_indices']]).max()) for f,p in zip(film,pad));bond.append(err)
 valid=proc['exit_code']==0 and '[ERROR]'not in logs and counts==[[steps,steps]]*3 and len(quality)==6 and all(x['finite'] and x['minimum_saved_volume_ratio']>0 for x in quality) and len(bond)==3 and max(bond)<=1e-12
 d=dict(status='BOUNDED_EXECUTION_ONLY' if valid else 'FAIL_EXECUTION_ELEMENTS_OR_BOND',process=proc,outputs=counts,qualities=quality,maximum_bond_position_error_m=max(bond) if bond else None,SOFA_error_count=logs.count('[ERROR]'),holding='NOT MEASURED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
