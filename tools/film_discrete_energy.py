"""Derived signed BE terms, not an arbitrary residual named numerical dissipation."""
import argparse,csv,json,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);source=ROOT/'results'/('autonomous_film_'+a.case)/'1';tree=ET.parse(source/'scene.scn');field=tree.find("Node[@name='assembly']/FilmRailTendon");ode=tree.find('ReGripBDFSolver')
 summary=json.loads((source.parent/'summary.json').read_text())
 identity=json.loads((source.parent/'identity.json').read_text())
 accepted=tree.find('FilmNativeCoupledCorrection')
 if accepted is not None and accepted.get('integrationOrder','1')!='1':raise RuntimeError('BE identity is not a BDF2 identity;native BE predictor does not define accepted integration')
 if summary.get('status')!='PASS' or not summary.get('finite'):raise RuntimeError('completed finite execution required;partial states are not evidence')
 if ode.get('order')!='1' or ode.get('theta')!='1' or float(ode.get('rayleighStiffness'))!=0:raise RuntimeError('BE/mass-damping-only derivation')
 if field.get('rootGuideSecondOrder','0').lower() not in ('0','false'):raise RuntimeError('quadratic guide is not included in this reference')
 mass=np.fromstring(tree.find("Node[@name='assembly']/DiagonalMass").get('vertexMass'),sep=' ')[:,None];j=list(csv.DictReader((source/'journal.csv').open()));c=list(csv.DictReader((source/'contact.csv').open()));v=list(csv.DictReader((source/'momentum.csv').open()))
 if not len(j)==len(c)==len(v) or not j:raise RuntimeError('incomplete/synchronized journals required')
 command=identity['command'];expected=int(command[command.index('--steps')+1]) if '--steps' in command else 200
 if len(j)!=expected:raise RuntimeError('requested step count not complete')
 with (out/'states.txt').open('x') as stream:
  stream.write(f'{field.get("nx")} {field.get("guideIntervals","4")} {field.get("guideOffset")} {field.get("bondStiffness")} {len(j)}\n')
  for row,contact,velocity in zip(j,c,v):
   if not row['time']==contact['time']==velocity['time']:raise RuntimeError('stage mismatch')
   stream.write(row['time']+' '+row['T_per_rail']+' '+contact['begin_positions']+' '+contact['positions']+'\n')
 stages={};stages['compile']=logged(['g++','-std=c++17','-O3','-march=native','-fno-fast-math','-ffp-contract=off','-DREGRIP_FILM_REUSE_LIFT',ROOT/'diagnostics/film_rail_tendon/DiscreteEnergy.cpp','-o',out/'energy'],out/'compile',180)
 if stages['compile']['exit_code']:raise RuntimeError('energy reference compile')
 stages['reference']=logged([out/'energy',out/'states.txt',out/'terms.csv'],out/'reference',120)
 if stages['reference']['exit_code']:raise RuntimeError('energy reference')
 terms=list(csv.DictReader((out/'terms.csv').open()));records=[];energy_error=0
 for row,contact,velocity,term in zip(j,c,v,terms):
  v0,v1,impulse=(np.fromstring(velocity[k],sep=' ').reshape(-1,3) for k in ('v_begin','v_accepted','contact_impulse'));h=float(contact['dt']);T=float(row['T_per_rail']);dK=float(.5*np.sum(mass*(v1*v1-v0*v0)));dU=float(term['U1'])-float(term['U0']);dL=float(term['L1'])-float(term['L0']);W=-T*dL;Wcontact=float(np.sum(impulse*v1));Dkin=float(.5*np.sum(mass*(v1-v0)**2));Ddamp=float(h*float(ode.get('rayleighMass'))*np.sum(mass*v1*v1));Ds=float(term['stored_gradient_dot_delta_q'])-dU;Dt=float(term['tendon_gradient_dot_delta_q'])-T*dL;residual=dK+dU-W-Wcontact+Dkin+Ddamp+Ds+Dt;scale=sum(abs(x) for x in (dK,dU,W,Wcontact,Dkin,Ddamp,Ds,Dt));relative=abs(residual)/scale if scale else (0 if residual==0 else None);energy_error=max(energy_error,abs(float(term['U1'])-float(row['U_shell'])-float(row['U_attachment'])));records.append(dict(time=float(row['time']),delta_K=dK,delta_U=dU,tendon_held_force_work=W,constraint_impulse_work=Wcontact,BE_kinetic_term=Dkin,Rayleigh_work=Ddamp,signed_elastic_endpoint_term=Ds,signed_tendon_endpoint_term=Dt,unexplained_residual=residual,relative_residual=relative))
 maximum=max(r['relative_residual'] for r in records);write_json(out/'summary.json',dict(discrete_identity_status='PASS' if maximum<=.001 else 'FAIL',threshold=.001,scope='derived BE identity for frictionless fixed-object film/rails coupon;NOT full physical energy certification',maximum_relative_residual=maximum,maximum_stored_energy_reconstruction_error=energy_error,records=records,stages=stages,signed_terms_are_not_physical_heat=True,constraint_work_is_not_automatically_friction_loss=True,full_energy='BLOCKED',pressure_work=None,real_actuator_energy=None,inputs={f:sha(source/f) for f in ('journal.csv','contact.csv','momentum.csv','scene.scn')},binary_sha256=sha(out/'energy'),source_sha256=sha(ROOT/'diagnostics/film_rail_tendon/DiscreteEnergy.cpp')));print(json.dumps(dict(discrete_identity='PASS' if maximum<=.001 else 'FAIL',maximum_relative_residual=maximum,stored_energy_error=energy_error)))
if __name__=='__main__':main()
