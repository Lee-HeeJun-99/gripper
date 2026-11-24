"""Read-only saved geometric work inventory,NOT global Native energy closure.
Chord Jacobian is reconstructed from previous accepted paths,not captured stage J.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));body=read(src/'object.csv');t=np.array([float(r['time_s']) for r in body]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in body]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in body]);massdata=np.fromstring(root.find("Node[@name='object']/UniformMass").get('vertexMass'),sep=' ');mass=massdata[0];Ibody=mass*massdata[2:].reshape(3,3);assert np.max(abs(Ibody-np.eye(3)*Ibody[0,0]))<1e-15,'This configured kinetic inventory assumes spherical isotropic inertia';geom=np.zeros(len(t));chord=geom.copy();initials=[]
 for i in range(3):
  film=read(src/f'finger{i}.csv');assert [float(r['time_s']) for r in film]==t.tolist()
  for j in range(2):
   node=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']");pull=np.fromstring(node.find('CableConstraint').get('pullPoint'),sep=' ');previous=np.vstack([pull,np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)]);initials.append(float(np.linalg.norm(np.diff(previous,axis=0),axis=1).sum()))
   for k,r in enumerate(film):
    actual=np.vstack([pull,np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]);before=np.diff(previous,axis=0);after=np.diff(actual,axis=0);length=np.linalg.norm(before,axis=1);assert (length>0).all();force=float(r[f'cable{j}_force_raw'])/dt;geom[k]+=force*(length.sum()-np.linalg.norm(after,axis=1).sum());chord[k]-=force*np.sum((before/length[:,None])*(after-before));previous=actual
 kinetic_translation=.5*mass*np.sum(v[:,:3]**2,axis=1);kinetic_rotation=.5*Ibody[0,0]*np.sum(v[:,3:]**2,axis=1);gravity=np.fromstring(root.get('gravity'),sep=' ');q0=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3];potential=-mass*((q[:,:3]-q0)@gravity);wc=np.cumsum(geom);wj=np.cumsum(chord);records=[]
 with (out/'work_inventory.csv').open('x') as f:
  w=csv.writer(f);w.writerow(['time_s','configured_object_translation_J','configured_object_rotation_J','object_gravity_potential_change_J','cumulative_geometric_cable_work_J','cumulative_previous_chord_cable_work_J'])
  for values in zip(t,kinetic_translation,kinetic_rotation,potential,wc,wj):w.writerow(values)
 for lo,hi in ((0.,.6),(1.,1.2),(1.6,2.)):
  window=(t>lo+1e-12)&(t<=hi+1e-12)
  if not window.any():continue
  records.append(dict(window_s=[lo,hi],samples=int(window.sum()),geometric_cable_work_J=float(geom[window].sum()),previous_chord_cable_work_J=float(chord[window].sum()),maximum_object_translational_kinetic_J=float(kinetic_translation[window].max()),maximum_object_rotational_kinetic_J=float(kinetic_rotation[window].max())))
 d=dict(status='SAVED_GEOMETRIC_WORK_INVENTORY_NOT_ENERGY_PASS',case=a.case,windows=records,configured_object_mass_kg=mass,configured_isotropic_inertia_kg_m2=float(Ibody[0,0]),maximum_absolute_cumulative_chord_geometric_work_difference_J=float(abs(wc-wj).max()),initial_cable_lengths_m=initials,FEM_strain_energy=None,actual_stage_work=None,friction_loss=None,full_energy_residual=None,scope='Endpoint force-weighted length change and reconstructed previous-accepted chord row are references,not measured Native stage J/work. Native forceNs dividedbydt;fixed pullpoints only,noLift. Configured RigidMass normalized inertia multipliedbymass;not independently captured Nativekinetic API. No totalenergy closure or unique instability cause.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','object.csv','finger0.csv','finger1.csv','finger2.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
