"""Independent mapped-state/shared-impulse audit and actual-scale pictures."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_audit import gaps
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='PASS':raise ValueError('completed actual event run required')
 for name,digest in meta['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed:'+name)
 scene=ET.parse(src/'scene.scn');top=scene.find('.//TriangleSetTopologyContainer');rest=np.fromstring(top.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(top.get('triangles'),sep=' ',dtype=int).reshape(-1,3);event=next(csv.DictReader((src/'three.event.csv').open()));rows=list(csv.DictReader((src/'three.impact_rows.csv').open()));end=next(csv.DictReader((src/'three.states.csv').open()));index=np.full(rest.size,-1,dtype=int);weight=np.ones(rest.size);nf=0
 for offset,ny in ((0,5),(105,3),(168,3)):
  for i in range(1,21):
   for j in range(ny):
    for d in range(3):
     if i!=1 or d!=2:index[3*(offset+i*ny+j)+d]=nf;nf+=1
  for j in range(ny):index[3*(offset+ny+j)+2]=index[3*(offset+2*ny+j)+2];weight[3*(offset+ny+j)+2]=.25
 def expand(x,f):
  value=np.zeros(rest.size);mask=index>=0;value[mask]=x[f*nf+index[mask]]*weight[mask];return value.reshape(-1,3)
 layout=ROOT/'results/autonomous_film_20261117_three_finger_negative809';dims=next(csv.DictReader((layout/'geometry.csv.layout.csv').open()))
 if sha(layout/'sources/models/film_three_finger/FrameLayout.h')!=meta['sources']['models/film_three_finger/FrameLayout.h']:raise ValueError('archived mount definition mismatch')
 theta=float(dims['mount_angle']);frames=[]
 for f in range(3):
  phi=2*np.pi*f/3;rad=np.array([np.cos(phi),np.sin(phi),0]);tan=np.array([-np.sin(phi),np.cos(phi),0]);R=np.column_stack((-np.sin(theta)*rad-np.cos(theta)*np.array([0,0,1]),tan,np.cos(theta)*rad-np.sin(theta)*np.array([0,0,1])));frames.append((R,50*rad-12*R[:,1]))
 q=np.fromstring(event['qminus'],sep=' ');vm=np.fromstring(event['vminus'],sep=' ');vp=np.fromstring(event['vplus'],sep=' ');qe=np.fromstring(event['qend'],sep=' ');ve=np.fromstring(event['vend'],sep=' ');impulse=np.fromstring(event['impulse'],sep=' ');J=np.array([np.fromstring(r['jacobian'],sep=' ') for r in rows]);mass_tokens=np.fromstring((src/'public_mass_reference.txt').read_text(),sep=' ');count=int(mass_tokens[0]);masses=mass_tokens[1:1+3*count].reshape(3,count);diagonal=np.zeros(len(q))
 for f in range(3):
  for node in range(count):
   for d in range(3):
    k=index[3*node+d]
    if k>=0:diagonal[f*nf+k]+=masses[f,node]*weight[3*node+d]**2
 diagonal[-6:-3]=mass_tokens[-2];diagonal[-3:]=mass_tokens[-1]
 if len(rows)!=int(event['rows']) or J.shape!=(len(rows),len(q)) or [int(r['owner']) for r in rows]!=list(range(len(rows))):raise ValueError('actual impulse owner dimensions/order')
 errors=dict(momentum=float(np.linalg.norm(diagonal*(vp-vm)-J.T@impulse)),normal_before=0.,normal_after=0.,normal=0.,linear_row=0.,radial_moment=0.,actual_position=0.,actual_film_K=0.,whole_gap=float('inf'))
 for i,r in enumerate(rows):
  f=int(r['owner_finger']);ids=tri[int(r['triangle'])];R,origin=frames[f];points=(rest+expand(q,f))@R.T+origin;normal=np.array([float(r[k]) for k in ('nx','ny','nz')]);full=np.zeros_like(rest)
  for node in ids:
   for d in range(3):
    k=index[3*node+d]
    if k<0 or weight[3*node+d]!=1:raise ValueError('root/slave contact requires explicit root reaction observer;unsupported here')
    full[node,d]=J[i,f*nf+k]
  world=full@R.T;errors['normal']=max(errors['normal'],float(np.linalg.norm(normal+J[i,-6:-3])),abs(np.linalg.norm(normal)-1));errors['linear_row']=max(errors['linear_row'],float(np.linalg.norm(world.sum(axis=0)+J[i,-6:-3])));errors['radial_moment']=max(errors['radial_moment'],float(np.linalg.norm(np.cross(points-q[-6:-3],world).sum(axis=0)+J[i,-3:])));errors['normal_before']=max(errors['normal_before'],abs(J[i]@vm-float(r['normal_before'])));errors['normal_after']=max(errors['normal_after'],abs(J[i]@vp-float(r['normal_after'])))
 for f,(R,origin) in enumerate(frames):
  field=list(csv.DictReader((src/('film_'+str(f)+'.csv')).open()))[-1];actual=np.fromstring(field['x'],sep=' ').reshape(-1,3);errors['actual_position']=max(errors['actual_position'],float(np.max(abs(rest+expand(qe,f)-actual))));errors['actual_film_K']=max(errors['actual_film_K'],abs(.5*np.sum(masses[f,:,None]*expand(ve,f)**2)-float(field['K'])));points=actual@R.T+origin;errors['whole_gap']=min(errors['whole_gap'],float(np.min(gaps(points[tri],qe[-6:-3],30.01))))
 loss=-.5*impulse@((J@vm)+(J@vp));errors['impulse_work']=abs(loss-float(event['energy_loss']));errors['normal_velocity']=float(np.max(np.maximum(0,-J@vp)));errors['complementarity']=float(np.max(abs(impulse*(J@vp))))
 valid=errors['momentum']<=1e-17 and errors['whole_gap']>=-1e-10 and errors['normal_velocity']<=1e-10 and min(impulse)>=0 and loss>=0 and all(errors[k]<=1e-12 for k in ('normal_before','normal_after','normal','linear_row','radial_moment','actual_position','actual_film_K','impulse_work','complementarity'))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 initial=q.copy();initial[:3*nf]=0;initial[-6:-3]=[float(x) for x in scene.find('Node[@name="free_object"]/MechanicalObject').get('position').split()[:3]]
 for label,state,time in (('initial',initial,0),('pre_impact',q,float(event['event_time'])),('post_impact',q,float(event['event_time'])),('remaining_step_end',qe,.0002)):
  fig,axes=plt.subplots(1,3,figsize=(14,4));vertices=[];faces=[]
  for f,(R,origin) in enumerate(frames):
   world=(rest+expand(state,f))@R.T+origin;vertices.extend(world.tolist());faces.extend((tri+f*len(rest)+1).tolist())
   for ax,(d,e) in zip(axes,((0,1),(0,2),(1,2))):ax.add_collection(PolyCollection(world[tri][:,:,[d,e]],facecolor=('#7ab','#da8','#8b9')[f],edgecolor='#456',linewidth=.12,alpha=.6))
  for ax,(d,e) in zip(axes,((0,1),(0,2),(1,2))):ax.add_patch(plt.Circle((state[-6+d],state[-6+e]),30,color='#aaa',alpha=.3));ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('xyz'[d]+' [mm]');ax.set_ylabel('xyz'[e]+' [mm]')
  fig.suptitle('ACTUAL SOFA '+label+' t='+format(time,'.9g')+'s dt=200us scale1;NOT qualified grasp\n'+meta['source_commit'][:8]+' DLL '+meta['binary_sha256'][:12]+' zero gravity / Fz=-.001N / plastic frictionless impact');fig.tight_layout();fig.savefig(out/(label+'.png'),dpi=150);plt.close(fig)
  (out/(label+'.obj')).write_text('# Actual SOFA saved state,scale1,NOT grasp\n'+'\n'.join('v '+' '.join(format(x,'.17g') for x in v) for v in vertices)+'\n'+'\n'.join('f '+' '.join(str(x) for x in t) for t in faces)+'\n')
 fig,axes=plt.subplots(1,2,figsize=(11,4));axes[0].plot(J@vm,'o',label='pre');axes[0].plot(J@vp,'x',label='post');axes[0].set_ylabel('relative normal velocity [mm/s]');axes[0].legend();axes[1].plot(impulse,'o');axes[1].set_ylabel('INSTANTANEOUS impulse [N s],not force');[ax.set_xlabel('actual owner row') for ax in axes];fig.tight_layout();fig.savefig(out/'impact_observables.png',dpi=150);plt.close(fig)
 write_json(out/'summary.json',dict(status='PASS' if valid else 'FAIL',scope='actual mapped/whole-end-surface/shared impulse audit;NOT whole-path/time/full energy/grasp',case=a.case,errors=errors,impact_energy_loss_Nmm=loss,rows=len(rows),rank=int(np.linalg.matrix_rank(J)),displacement_magnification=1,contact_area_mm2=None,peak_pressure=None,root_reaction='not measured;observer rejects root/slave contacts',raw={f:sha(src/f) for f in ('summary.json','scene.scn','three.event.csv','three.impact_rows.csv','three.states.csv')}));print(json.dumps(dict(status='PASS' if valid else 'FAIL',errors=errors,loss_Nmm=loss)))
if __name__=='__main__':main()
