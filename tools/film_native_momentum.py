"""Independent BE-predictor / BE-or-BDF2 accepted impulse residual."""
import argparse,csv,json,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--force-coordinates',choices=('world','local'),default='world');p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);source=ROOT/'results'/('autonomous_film_'+a.case)/'1';tree=ET.parse(source/'scene.scn');field=tree.find("Node[@name='assembly']/FilmRailTendon");ode=tree.find('ReGripBDFSolver')
 if ode.get('theta')!='1' or ode.get('order')!='1' or float(ode.get('rayleighStiffness'))!=0:raise RuntimeError('BE/zero stiffness damping diagnostic only')
 accepted=tree.find('FilmNativeCoupledCorrection')
 accepted_order=int(accepted.get('integrationOrder','1')) if accepted is not None else 1
 if accepted_order not in (1,2):raise RuntimeError('accepted integrator not derived')
 summary=json.loads((source.parent/'summary.json').read_text())
 if summary.get('status')!='PASS' or not summary.get('finite'):raise RuntimeError('completed finite trajectory required')
 mass=np.fromstring(tree.find("Node[@name='assembly']/DiagonalMass").get('vertexMass'),sep=' ');nx=int(field.get('nx'));n=len(mass);j=list(csv.DictReader((source/'journal.csv').open()));c=list(csv.DictReader((source/'contact.csv').open()));v=list(csv.DictReader((source/'momentum.csv').open()))
 if not len(j)==len(c)==len(v) or not j:raise RuntimeError('journal mismatch')
 local_records=None
 if a.force_coordinates=='local':
  if not (source/'displacement.csv').is_file():raise RuntimeError('exact local journal missing;main journal.x is WORLD coordinates,not displacement;do not reinterpret it')
  local_records=list(csv.DictReader((source/'displacement.csv').open()))
  if len(local_records)!=len(j) or any(x['time']!=y['time'] for x,y in zip(local_records,j)):raise RuntimeError('local displacement stage/count mismatch')
 with (out/'states.txt').open('x') as stream:
  stream.write(f'{nx} {field.get("guideIntervals","4")} {field.get("guideOffset")} {field.get("bondStiffness")} {len(j)}\n')
  for index,(row,contact,velocity) in enumerate(zip(j,c,v)):
   if not row['time']==contact['time']==velocity['time']:raise RuntimeError('stage time mismatch')
   stream.write(row['time']+' '+row['T_per_rail']+' '+contact['free_positions']+' '+(local_records[index]['u'] if a.force_coordinates=='local' else contact['positions'])+'\n')
 stages={};stages['compile']=logged(['g++','-std=c++17','-O3','-march=native','-fno-fast-math','-ffp-contract=off','-DREGRIP_FILM_REUSE_LIFT',ROOT/'diagnostics/film_rail_tendon/AcceptedForces.cpp','-o',out/'forces'],out/'compile',180)
 if stages['compile']['exit_code']:raise RuntimeError('force reference compile')
 stages['reference']=logged([out/'forces',out/'states.txt',out/'forces.txt']+(['accepted_displacement'] if a.force_coordinates=='local' else []),out/'reference',120)
 if stages['reference']['exit_code']:raise RuntimeError('force reference')
 force=np.loadtxt(out/'forces.txt');free=np.ones((n,3),dtype=bool)
 for offset,width in ((0,5),(5*nx,3),(8*nx,3)):free[offset:offset+width]=False;free[offset+width:offset+2*width,2]=False
 def pull(value):
  value=value.copy()
  for offset,width in ((0,5),(5*nx,3),(8*nx,3)):value[offset+2*width:offset+3*width,2]+=.25*value[offset+width:offset+2*width,2];value[offset+width:offset+2*width,2]=0
  return value[free]
 records=[];kinetic_error=0
 for index,(row,contact,velocity) in enumerate(zip(j,c,v)):
  dt=float(contact['dt']);vb,vf,va,impulse=(np.fromstring(velocity[k],sep=' ').reshape(n,3) for k in ('v_begin','v_free','v_accepted','contact_impulse'));Ff=force[index,1:1+3*n].reshape(n,3);Fa=force[index,1+3*n:1+6*n].reshape(n,3);dFlin=force[index,1+6*n:].reshape(n,3);rayleigh=float(ode.get('rayleighMass'));entry={'time':float(row['time'])}
  for label,speed,F,imp in (('free',vf,Ff,np.zeros_like(impulse)),('accepted',va,Fa,impulse),('linearized',va,Ff+dFlin,impulse)):
   velocity_difference=speed-vb
   if accepted_order==2 and index>0 and label!='free':
    if float(c[index-1]['dt'])!=dt:raise RuntimeError('variable-step BDF2 residual not derived')
    vold=np.fromstring(v[index-1]['v_begin'],sep=' ').reshape(n,3)
    velocity_difference=(3*speed-4*vb+vold)/2
   terms=[mass[:,None]*velocity_difference,dt*rayleigh*mass[:,None]*speed,-dt*F,-imp];residual=np.linalg.norm(pull(sum(terms)));scale=sum(np.linalg.norm(pull(term)) for term in terms);entry[label+'_absolute_impulse_residual']=float(residual);entry[label+'_relative_impulse_residual']=float(residual/scale) if scale else (0 if residual==0 else None)
  qf,qa=(np.fromstring(contact[k],sep=' ').reshape(n,3) for k in ('free_positions','positions'));entry['kinematic_correction_defect_mm']=float(np.linalg.norm((qa-qf)-dt*(va-vf)));entry['nonlinear_force_remainder_norm']=float(np.linalg.norm(pull(Fa-Ff-dFlin)))
  qb=np.fromstring(contact['begin_positions'],sep=' ').reshape(n,3)
  if accepted_order==2 and index>0:
   qold=np.fromstring(c[index-1]['begin_positions'],sep=' ').reshape(n,3)
   position_defect=(3*qa-4*qb+qold)/2-dt*va
  else:position_defect=qa-qb-dt*va
  entry['accepted_position_identity_defect_mm']=float(np.linalg.norm(position_defect));entry['accepted_order']=2 if accepted_order==2 and index>0 else 1
  kinetic_error=max(kinetic_error,abs(float(row['K'])-float(.5*np.sum(mass[:,None]*va*va))));records.append(entry)
 write_json(out/'summary.json',dict(coordinate_warning=None if a.force_coordinates=='local' else 'world-minus-rest reconstruction can be precision-limited for small forces;not a substitute for exact local coordinates',force_coordinates=a.force_coordinates,status='EXPERIMENTAL',scope='free versus constraint-corrected endpoint impulse residual,not whole energy/balance approval',reference_source_sha256=sha(ROOT/'diagnostics/film_rail_tendon/AcceptedForces.cpp'),script_sha256=sha(__file__),maximum_linearized_relative=max(r['linearized_relative_impulse_residual'] for r in records),maximum_free_relative=max(r['free_relative_impulse_residual'] for r in records),maximum_accepted_relative=max(r['accepted_relative_impulse_residual'] for r in records),maximum_kinetic_reconstruction_error=kinetic_error,records=records,stages=stages,inputs={k:sha(source/k) for k in ('scene.scn','journal.csv','contact.csv','momentum.csv')+(('displacement.csv',) if a.force_coordinates=='local' else ())},force_reference_sha256=sha(out/'forces'),root_reaction=None));print(json.dumps(dict(free=max(r['free_relative_impulse_residual'] for r in records),accepted=max(r['accepted_relative_impulse_residual'] for r in records),linearized=max(r['linearized_relative_impulse_residual'] for r in records),kinetic_error=kinetic_error)))
if __name__=='__main__':main()
