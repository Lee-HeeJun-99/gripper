"""Native layer coupon one-axis mesh contrast;all collision models retained."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_mesh_reference import mesh
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--nx',type=int,choices=[17,33,65],required=True);p.add_argument('--steps',type=int,choices=[50,500],default=50);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_free1189';tree=ET.parse(src/'scene.scn');root=tree.getroot();q0,tet,tri=mesh(a.nx);flat=lambda x:' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
 for i in (0,1):
  node=root.find(f"./Node[@name='layer{i}']");q=q0+[0,0,i*.000202];top=node.find('MeshTopology');top.set('position',flat(q));top.set('tetrahedra',flat(tet));top.set('triangles',flat(tri));node.find('MechanicalObject').set('position',flat(q));node.find('FixedProjectiveConstraint').set('indices',' '.join(map(str,np.flatnonzero(q0[:,0]==0))));F=np.zeros_like(q);F[q0[:,0]==.04,2]=-1e-4/8;field=node.find('ConstantForceField');field.set('indices',' '.join(map(str,range(len(q)))));field.set('forces',flat(F))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'mesh_dependency.py').write_bytes((BASE/'sofa/layer_mesh_reference.py').read_bytes());(out/'mesh.json').write_text(json.dumps(dict(q0=q0.tolist(),tetrahedra=tet.tolist(),triangles=tri)));pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'].copy();cmd[cmd.index('-n')+1]=str(a.steps);cmd[-1]=str(out/'scene.scn');pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),nx=a.nx,steps=a.steps,child_limit_s=120,estimated_runtime_s=2 if a.steps==50 else 20,classification='ONE_AXIS_NATIVE_MESH_CONTRAST_NOT_JAMMING',hypothesis='High pure-bending interpolant shear energy suggests mesh stiffness dominates. ONLY lengthwise cell count changed. E,density,geometry,mass,endload,dt,BC,collision,solver settings kept. Two-layer free pressure0 control.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[];tips=[];quality=[]
 for i in (0,1):
  path=out/f'layer{i}.csv';rows=list(csv.DictReader(path.open())) if path.exists() else [];counts.append(len(rows))
  if rows:
   q=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows]);init=q0+[0,0,i*.000202];tips.append(float((q[-1,q0[:,0]==.04,2]-init[q0[:,0]==.04,2]).mean()));D=(q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2);D0=(q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1);quality.append(float((np.linalg.det(D)/np.linalg.det(D0)).min()))
 d=dict(status='NATIVE_MESH_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and counts==[a.steps]*2 and quality and min(quality)>0 else 'FAIL_EXECUTION_OR_INVERSION',process=proc,outputs=counts,tip_displacement_m=tips,minimum_volume_ratio=quality,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
