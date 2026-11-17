"""Independent nonlinear contact correction on actual single-active-plane states."""
import argparse,csv,json,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);source=ROOT/'results'/('autonomous_film_'+a.case)/'1';tree=ET.parse(source/'scene.scn');field=tree.find("Node[@name='assembly']/FilmRailTendon");ode=tree.find('ReGripBDFSolver');center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ');mass=np.fromstring(tree.find("Node[@name='assembly']/DiagonalMass").get('vertexMass'),sep=' ');j=list(csv.DictReader((source/'journal.csv').open()));c=list(csv.DictReader((source/'contact.csv').open()));v=list(csv.DictReader((source/'momentum.csv').open()));packets=[]
 for row,contact,velocity in zip(j,c,v):
  lam=np.fromstring(contact['lambda_impulse'],sep=' ');positive=lam[lam>0]
  if len(positive)!=1:continue
  impulse=np.fromstring(velocity['contact_impulse'],sep=' ').reshape(-1,3);J=impulse/positive[0];normal=J.sum(axis=0)
  if abs(np.linalg.norm(normal)-1)>1e-10:raise RuntimeError('single normal row required')
  packets.append((row,contact,velocity,float(positive[0]),J,float(normal@center+8.01)))
 with (out/'packets.txt').open('x') as stream:
  stream.write(str(len(packets))+'\n')
  for row,contact,velocity,lam,J,target in packets:
   stream.write(' '.join(map(str,[row['time'],field.get('nx'),field.get('guideIntervals','4'),field.get('guideOffset'),field.get('bondStiffness'),contact['dt'],ode.get('rayleighMass'),row['T_per_rail'],lam,target]))+'\n');stream.write(' '.join(map(str,mass))+'\n')
   for vector in (contact['begin_positions'],velocity['v_begin'],velocity['v_accepted'],' '.join(map(str,J.ravel()))):stream.write(vector+'\n')
 stages={};stages['compile']=logged(['g++','-std=c++17','-O3','-march=native','-fno-fast-math','-ffp-contract=off','-DREGRIP_FILM_REUSE_LIFT','-I/usr/include/eigen3',ROOT/'diagnostics/film_rail_tendon/CoupledPlaneReference.cpp','-o',out/'coupled'],out/'compile',180)
 if stages['compile']['exit_code']:raise RuntimeError('reference compile')
 stages['reference']=logged([out/'coupled',out/'packets.txt',out/'comparison.csv'],out/'reference',120);rows=list(csv.DictReader((out/'comparison.csv').open())) if (out/'comparison.csv').exists() else []
 write_json(out/'summary.json',dict(status='PASS' if stages['reference']['exit_code']==0 and len(rows)==len(packets) and len(rows)>0 else 'FAIL',scope='independent frozen single-plane BE reference,NOT actual SOFA corrected dynamics',rows=rows,stages=stages,inputs={f:sha(source/f) for f in ('scene.scn','contact.csv','journal.csv','momentum.csv')},binary_sha256=sha(out/'coupled'),source_sha256=sha(ROOT/'models/film_native_contact/CoupledPlaneStep.h')));print(json.dumps(rows))
if __name__=='__main__':main()
