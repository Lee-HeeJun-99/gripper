"""Native section-only refinement control with existing face traction."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_section_reference import mesh
from layer_face_load import tip_load

def geometry(nz):
 q,t=mesh(9,2,nz);faces={}
 for a,b,c,d in t:
  for f in ((b,c,d),(a,d,c),(a,b,d),(a,c,b)):faces.setdefault(tuple(sorted(f)),[]).append(f)
 tri=[[int(i) for i in v[0]] for v in faces.values() if len(v)==1]
 V=np.linalg.det((q[t[:,1:]]-q[t[:,0,None]]).transpose(0,2,1))/6
 assert np.all(V>0)
 F,area,_=tip_load(q,t,[0,0,-5e-5]);mass=.000112/len(q)
 # UniformMass retained;section inertia is NOT invariant under refinement.
 centre=np.sum(q*mass,axis=0)/.000112
 inertia=sum(mass*((p@p)*np.eye(3)-np.outer(p,p)) for p in q-centre)
 return q,t,tri,F,dict(volume_m3=float(V.sum()),minimum_tet_volume_m3=float(V.min()),load_area_m2=area,total_mass_kg=.000112,nodal_mass_kg=mass,COM_m=centre.tolist(),uniform_nodal_inertia_kg_m2=inertia.tolist(),mass_quadrature='UniformMass retained,total mass same;discrete section inertia changes with mesh;NOT continuum-consistent mass refinement')

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--nz',type=int,choices=[3,5],default=3);p.add_argument('--steps',type=int,choices=[50,500],default=50);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_traction_native1282';q,t,tri,F,quality=geometry(a.nz);tree=ET.parse(src/'scene.scn');root=tree.getroot();flat=lambda v:' '.join(format(x,'.17g') for x in np.asarray(v).ravel())
 for i in (0,1):
  n=root.find(f"./Node[@name='layer{i}']");pos=q+[0,0,i*.000202];top=n.find('MeshTopology');top.set('position',flat(pos));top.set('tetrahedra',flat(t));top.set('triangles',flat(tri));n.find('MechanicalObject').set('position',flat(pos));n.find('FixedProjectiveConstraint').set('indices',' '.join(map(str,np.flatnonzero(q[:,0]==0))));ff=n.find('ConstantForceField');ff.set('indices',' '.join(map(str,range(len(q)))));ff.set('forces',flat(F))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'mesh.json').write_text(json.dumps(dict(q0=q.tolist(),tetrahedra=t.tolist(),triangles=tri)))
 for name in ('layer_section_native.py','layer_section_reference.py','layer_face_load.py'):(out/name).write_bytes((BASE/'sofa'/name).read_bytes())
 pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'].copy();cmd[cmd.index('-n')+1]=str(a.steps);cmd[-1]=str(out/'scene.scn');forecast=10.
 if a.steps>50:
  if not a.pilot:raise ValueError('clean matching pilot required')
  pilot=BASE/'results'/a.pilot;pm=json.loads((pilot/'preflight.json').read_text());pr=json.loads((pilot/'summary.json').read_text());assert pm['section_nz']==a.nz and pm['steps']==50 and pr['status']=='PASS_NATIVE_SECTION_EXECUTION_ONLY';forecast=pr['process']['runtime_s']*10
  if forecast>120:raise ValueError('forecast exceeds budget')
 plugins={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')};assert list(plugins.values())==[pre['binary_sha256']]
 pre.update(command=cmd,steps=a.steps,section_nz=a.nz,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),estimated_runtime_s=forecast,quality=quality,plugin_hashes=plugins,scope='ONLY section thickness subdivision changes;consistent face traction,small FEM,E,nu,geometry,mass total,dt,ODE,collision unchanged. UniformMass nodal inertia changes disclosed.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[];ratios=[];tips=[]
 for i in (0,1):
  rows=list(csv.DictReader((out/f'layer{i}.csv').open())) if (out/f'layer{i}.csv').exists() else [];counts.append(len(rows))
  if rows:
   states=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows]);initial=q+[0,0,i*.000202];tips.append(float((states[-1,q[:,0]==.04,2]-initial[q[:,0]==.04,2]).mean()));ratios.append(float((np.linalg.det((states[:,t[:,1:]]-states[:,t[:,0,None]]).transpose(0,1,3,2))/np.linalg.det((q[t[:,1:]]-q[t[:,0,None]]).transpose(0,2,1))).min()))
 clean=proc['exit_code']==0 and '[ERROR]'not in logs and 'Unused Attribute'not in logs and counts==[a.steps]*2 and len(ratios)==2 and min(ratios)>0
 d=dict(status='PASS_NATIVE_SECTION_EXECUTION_ONLY' if clean else 'FAIL_EXECUTION_OR_INVERSION',process=proc,outputs=counts,tip_m=tips,minimum_volume_ratio=ratios,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
