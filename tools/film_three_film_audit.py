"""Actual used-row virtual work/whole-stage geometry and mapped-state observer.

This does NOT certify a contact Hessian,full dynamics time convergence or grasp.
"""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_audit import gaps
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text());summary=json.loads((src/'summary.json').read_text())
 if summary['status']!='PASS':raise ValueError('completed actual three-film contact experiment required')
 driven=meta['actual_solver'].startswith('ThreeFilmDrivenODE');input_label='C2 10ms already-touching pilot' if driven else 'T=0,100us REST-contact IVP'
 scene=ET.parse(src/'scene.scn');layout=ROOT/'results/autonomous_film_20261117_three_finger_negative809';dims=next(csv.DictReader((layout/'geometry.csv.layout.csv').open()))
 if sha(layout/'sources/models/film_three_finger/FrameLayout.h')!=meta['sources']['models/film_three_finger/FrameLayout.h']:raise ValueError('compiled actual fixed-frame definition differs from independent layout')
 theta=float(dims['mount_angle']);frames=[]
 for f in range(3):
  phi=2*np.pi*f/3;rad=np.array([np.cos(phi),np.sin(phi),0]);tan=np.array([-np.sin(phi),np.cos(phi),0]);z=np.array([0,0,1]);R=np.column_stack((-np.sin(theta)*rad-np.cos(theta)*z,tan,np.cos(theta)*rad-np.sin(theta)*z));frames.append((R,50*rad-12*R[:,1]))
 topology=scene.find('.//TriangleSetTopologyContainer');rest=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3);nx=21;index=np.full(rest.size,-1,dtype=int);weight=np.ones(rest.size);nf=0
 for offset,ny in ((0,5),(5*nx,3),(8*nx,3)):
  for i in range(1,nx):
   for j in range(ny):
    for d in range(3):
     if i!=1 or d!=2:index[3*(offset+i*ny+j)+d]=nf;nf+=1
  for j in range(ny):index[3*(offset+ny+j)+2]=index[3*(offset+2*ny+j)+2];weight[3*(offset+ny+j)+2]=.25
 def expand(q,f):
  x=np.zeros(rest.size);mask=index>=0;x[mask]=q[f*nf+index[mask]]*weight[mask];return x.reshape(-1,3)
 states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));end=states[-1];q=np.fromstring(end['q'],sep=' ');v=np.fromstring(end['v'],sep=' ');errors=dict(world=0.,K_film=0.,linear=0.,angular=0.,normal=0.,point=0.,normal_velocity=0.,unowned_finger=0.);minimum=float('inf');forces=[];energies=[]
 for f in range(3):
  fields=list(csv.DictReader((src/('film_'+str(f)+'.csv')).open()));mass=np.fromstring(scene.find('Node[@name="finger'+str(f)+'"]//DiagonalMass').get('vertexMass'),sep=' ')
  if len(fields)!=len(states):raise ValueError('incomplete actual field trace')
  for state,ff in zip(states,fields):
   x=np.fromstring(state['q'],sep=' ');velocity=np.fromstring(state['v'],sep=' ');u=expand(x,f);vel=expand(velocity,f);actual=np.fromstring(ff['x'],sep=' ').reshape(-1,3);errors['world']=max(errors['world'],float(np.max(abs(rest+u-actual))));errors['K_film']=max(errors['K_film'],abs(float(ff['K'])-.5*np.sum(mass[:,None]*vel*vel)))
   if abs(float(state['time'])-float(ff['time']))>1e-12:raise ValueError('field/accepted physical clock mismatch')
  energies.append({k:float(fields[-1][k]) for k in ('U_shell','U_attachment','K','T_per_rail','cable_length','tendon_work')})
 for number,row in enumerate(rows):
  macro,within=divmod(number,9);stage_id,finger_id=divmod(within,3);expected_time=(macro+(0,.5,1)[stage_id])*meta['dt']
  if int(row['owner_finger'])!=finger_id or abs(float(row['time'])-expected_time)>1e-12:raise ValueError('fixed three-row stage ownership/order/clock differs;not a general lifetime inference')
  stage=np.fromstring(row['stage_q'],sep=' ');velocity=np.fromstring(row['stage_v'],sep=' ');f=int(row['owner_finger']);R,origin=frames[f];center=stage[3*nf:3*nf+3];normal=np.array([float(row[k]) for k in ('nx','ny','nz')]);point=np.array([float(row[k]) for k in ('px','py','pz')]);J=np.fromstring(row['jacobian'],sep=' ');points=(rest+expand(stage,f))@R.T+origin;ids=tri[int(row['triangle'])];full=np.zeros_like(rest)
  for node in ids:
   for d in range(3):
    free=index[3*node+d]
    if free<0 or weight[3*node+d]!=1:raise ValueError('this unprojection observer does NOT support contact on root/slave DOFs')
    full[node,d]=J[f*nf+free]
  world=full@R.T;bodyJ=J[3*nf:3*nf+3];errors['linear']=max(errors['linear'],float(np.linalg.norm(world.sum(axis=0)+bodyJ)));errors['angular']=max(errors['angular'],float(np.linalg.norm(np.cross(points-center,world).sum(axis=0)+J[-3:])));errors['normal']=max(errors['normal'],float(np.linalg.norm(normal+bodyJ)),abs(np.linalg.norm(normal)-1));bary=world@normal;errors['point']=max(errors['point'],float(np.linalg.norm(bary@points-point)));errors['normal_velocity']=max(errors['normal_velocity'],abs(J@velocity-float(row['normal_velocity'])))
  for other in range(3):
   if other!=f:errors['unowned_finger']=max(errors['unowned_finger'],float(np.linalg.norm(J[other*nf:(other+1)*nf])))
  for other in range(3):
   RR,oo=frames[other];worldPoints=(rest+expand(stage,other))@RR.T+oo;minimum=min(minimum,float(np.min(gaps(worldPoints[tri],center,30.01))))
  forces.append(dict(time=float(row['time']),finger=f,force=float(row['force']),normal_velocity=float(row['normal_velocity']),minimum_barycentric=float(bary.min())))
 valid=len(states)==meta['steps'] and len(rows)==9*meta['steps'] and minimum>=-1e-10 and all(x<=1e-12 for x in errors.values()) and all(r['force']>=0 and r['minimum_barycentric']>=-1e-12 for r in forces)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 finalWorld=[];initial=q.copy();initial[:3*nf]=0;initial[3*nf:3*nf+3]=[float(dims[k]) for k in ('body_x','body_y','body_z')]
 for name,state in (('initial',initial),('end',q)):
  fig,axes=plt.subplots(1,3,figsize=(14,5));allworld=[]
  for f,(R,origin) in enumerate(frames):
   x=(rest+expand(state,f))@R.T+origin;allworld.append(x)
   for ax,(d,e) in zip(axes,((0,1),(0,2),(1,2))):ax.add_collection(PolyCollection(x[tri][:,:,[d,e]],facecolor=('#66aabb','#eeaa66','#88bb77')[f],edgecolor='#445',linewidth=.15,alpha=.5))
  center=state[3*nf:3*nf+3]
  for ax,(d,e) in zip(axes,((0,1),(0,2),(1,2))):ax.add_patch(plt.Circle((center[d],center[e]),30,color='#aaa',alpha=.25));ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('xyz'[d]+' [mm]');ax.set_ylabel('xyz'[e]+' [mm]');ax.grid()
  fig.suptitle('ACTUAL SOFA '+name+';'+input_label+';scale1,NOT wrapping/grasp\n'+meta['source_commit'][:8]+' DLL '+meta['binary_sha256'][:12]);fig.tight_layout();fig.savefig(out/(name+'.png'),dpi=170);plt.close(fig)
  with (out/(name+'.obj')).open('w') as stream:
   stream.write('# Actual accepted SOFA state+explicit fixed owner frames;scale1;NOT grasp\n')
   for x in allworld:
    for vertex in x:stream.write('v '+' '.join(format(c,'.17g') for c in vertex)+'\n')
   for f in range(3):
    for face in tri:stream.write('f '+' '.join(str(int(i)+1+f*len(rest)) for i in face)+'\n')
 result=dict(status='PASS' if valid else 'FAIL',scope='actual mapped/used-row virtual-work/whole-stage audit;NOT independent Hessian/time/energy/pressure/grasp certification',case=a.case,errors=errors,minimum_whole_stage_gap_mm=minimum,forces=forces,actual_partial_energies=energies,displacement_magnification=1,visualization_note='saved local SOFA displacements transformed by compiled fixed frame;100us deformation is too small to see,NOT wrapping',source_hashes={f:sha(src/f) for f in ('identity.json','summary.json','scene.scn','three.states.csv','three.rows.csv','three.policy.csv','film_0.csv','film_1.csv','film_2.csv')},not_measured=['independent contact Hessian FD','3finger time/mesh convergence','root-reaction journal','full work/energy','self-contact/friction','closing/lift/hold/release/grasp'])
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],errors=errors,minimum_gap_mm=minimum)))
if __name__=='__main__':main()
