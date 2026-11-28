"""Independent full clipped triangles, element forces, edge pullback and rim cones."""
import sys,json,shutil
import numpy as np
from scipy.optimize import nnls
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_keeper_coupled71 import faces,rot
from primary_keeper_elastic_verify71 import clip
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[]
 for tag in sys.argv[2:]:
  sp=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(sp.read_text());cp=REPO/s['candidate']['path'];assert sha(cp)==s['candidate']['SHA256'];cad=json.loads(cp.read_text());assert all(sha((REPO/r['path']))==r['SHA256'] for r in cad['part_references'].values());f=REPO/s['field']['path'];assert sha(f)==s['field']['SHA256'];a=np.load(f);p=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];pos=p+u;F=a['load_N'];tri=a['boundary_triangles'];lam=a['normal_force_N'];keys=json.loads((REPO/s['contact_keys']['path']).read_text());ang=np.array(s['bolt_reference_spin_rad'])+a['bolt_spin_increment_rad'];pitch=.5/(2*np.pi)
  xyz=p[t];mat=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2);iv=np.linalg.inv(mat);grad=iv[:,1:,:].transpose(0,2,1);vol=abs(np.linalg.det(mat))/6;G=np.einsum('tai,taj->tij',u[t],grad);strain=(G+G.transpose(0,2,1))/2;E=s['E_ASSUMED_MPa'];nu=s['nu_ASSUMED'];mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));objective='elastic_law' in s
  FG=G+np.eye(3)
  if objective:strain=(FG.transpose(0,2,1)@FG-np.eye(3))/2
  stress=2*mu*strain+la*np.trace(strain,axis1=1,axis2=2)[:,None,None]*np.eye(3)
  physicalstress=FG@stress if objective else stress
  element=np.einsum('tij,taj,t->tai',physicalstress,grad,vol);internal=np.zeros_like(u)
  for j in range(4):np.add.at(internal,t[:,j],element[:,j])
  energy=float(np.sum(.5*np.einsum('tij,tij->t',strain,stress)*vol))
  def physical(uu):
   FF=np.eye(3)+np.einsum('tai,taj->tij',uu[t]-uu[t[:,0,None]],grad);CC=FF.transpose(0,2,1)@FF;EE=(CC-np.eye(3))/2;SS=mu*(CC-np.eye(3))+.5*la*np.trace(CC-np.eye(3),axis1=1,axis2=2)[:,None,None]*np.eye(3);PP=FF@SS
   ef=np.einsum('tij,taj,t->tai',PP,grad,vol);ff=np.zeros_like(uu)
   for j in range(4):np.add.at(ff,t[:,j],ef[:,j])
   en=np.sum((mu*np.sum(EE*EE,axis=(1,2))+.5*la*np.trace(EE,axis1=1,axis2=2)**2)*vol);return ff,en
  extra={};extra_checks={}
  if objective:
   rng=np.random.default_rng(7272);du=rng.normal(size=u.shape);df,de=physical(u.astype(complex)+1e-20j*du);virtual=float(np.sum(internal*du));cs=float(de.imag/1e-20);R=rot(.173);ur=pos.astype(np.longdouble)@R.astype(np.longdouble).T+np.array([.2,-.3,.1],dtype=np.longdouble)-p.astype(np.longdouble);fr,er=physical(ur);extra=dict(energy_gradient_virtualwork_error_N=abs(cs-virtual),rigid_rotated_force_error_N=float(abs(fr-internal@R.T).max()),rigid_rotated_energy_relative_error=float(abs(er/energy-1)))
   extra_checks=dict(energy_gradient=extra['energy_gradient_virtualwork_error_N']<1e-8,rigid_objective_force=extra['rigid_rotated_force_error_N']<1e-8,rigid_objective_energy=extra['rigid_rotated_energy_relative_error']<1e-6)
  settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];walls=[];centers=[];facets=[]
  for i,q in enumerate(settings):
   center=np.array([q['x'],q['y'],0.]);centers.append(center);R=rot(ang[i]);ww=[]
   for face in faces(read(REPO/cad['part_references'][q['bolt']]['path'])):
    ad=BRepAdaptor_Surface(face)
    if ad.GetType()!=GeomAbs_Plane:continue
    pl=ad.Plane();o=pl.Location();axis=pl.Axis().Direction();o=np.array([o.X(),o.Y(),o.Z()]);n=np.array([axis.X(),axis.Y(),axis.Z()]);bb=bounds(face)
    if abs(n[2])<1e-7 and np.linalg.norm((np.array(bb[:3])+bb[3:])[:2]/2-center[:2])<2:
     if n@(center-o)<0:n=-n
     ww.append((R@(o-center)+center+[0,0,pitch*ang[i]],R@n))
   assert len(ww)==6;walls.append(ww);eligible=tri[np.all(np.linalg.norm(p[tri,:2]-center[:2],axis=2)<1.6,axis=1)];minimum=1e9;count=0;bad=0
   for tr in eligible:
    poly=clip(list(pos[tr]),-1.3+pitch*ang[i],True);poly=clip(poly,pitch*ang[i],False)
    if not len(poly):continue
    gaps=np.array([np.sum((np.array(poly)-o)*n,axis=1) for o,n in ww]);g=float(gaps.min());minimum=min(minimum,g);count+=1;bad+=g<-1e-9
   facets.append(dict(bolt=q['bolt'],clipped_triangles=count,minimum_gap_mm=minimum,violating_triangles=int(bad)))
  pulled=np.zeros_like(F);tor=np.array(s['conditional_bolt_torque_Nmm']);workerr=[];rim=[];gaperr=[];direrr=[]
  for row,(key,lm) in enumerate(zip(keys,lam)):
   bi,wi,typ,*rest=key;o,n=walls[bi][wi];c=centers[bi]
   if typ=='v':
    node=rest[0];pt=pos[node];nd=[node];wt=[1.];g=n.copy();ds=0.
   else:
    aa,bb,end=rest;d=pos[bb]-pos[aa];z=pitch*ang[bi]+(-1.3 if end==0 else 0);tau=(z-pos[aa,2])/d[2];pt=pos[aa]+tau*d;nd=[aa,bb];wt=[1-tau,tau];g=n.copy();g[2]=-n@d/d[2];ds=n@d/d[2]*pitch
    if lm>1e-10:
     # Socket edge force on keeper must lie in cone(side inward, axial away).
     axial=np.array([0,0,1. if end else -1.]);cone=np.column_stack([n,axial]);coef,err=nnls(cone,g);rim.append(dict(row=row,lambda_N=float(lm),end=end,axial_gradient=float(g[2]),cone_relative_residual=float(err/np.linalg.norm(g)),nonnegative_coefficients=coef.tolist()))
   spin=-n@np.array([-(pt-c)[1],(pt-c)[0],0.])+ds;tor[bi]+=lm*spin
   for node,w in zip(nd,wt):pulled[node]+=lm*w*g
   gaperr.append(abs(n@(pt-o)-a['gap_mm'][row]));direrr.append(float(abs(g-a['pullback_direction'][row]).max()))
  forceerr=float(abs(internal-F).max());pullerr=float(abs(pulled-F).max());resultant=F.sum(0);moment=np.cross(pos,F).sum(0);badload=F.copy();badload[0,2]+=.01
  checks=dict(all_original_tetra_force=forceerr<1e-8,independent_edge_pullback=pullerr<1e-12,independent_torque=max(abs(tor))<1e-8,independent_gaps=max(gaperr)<1e-12,independent_edge_direction=max(direrr)<1e-12,nonnegative_multipliers=float(lam.min())>=-1e-9,complementarity=float(abs(lam*a['gap_mm']).max())<1e-8,complete_clipped_facets=all(q['minimum_gap_mm']>=-1e-9 for q in facets),independent_energy=abs(energy/s['static_energy_Nmm']-1)<1e-8,zero_force=max(abs(resultant))<1e-8,zero_deformed_moment=max(abs(moment))<1e-8,altered_load_rejected=float(abs(internal-badload).max())>.009,socket_rim_normal_cones=all(q['cone_relative_residual']<1e-8 for q in rim))
  checks.update(extra_checks)
  rows.append(dict(objective_independent=extra,source=ref(sp),field=ref(f),checks={k:bool(v) for k,v in checks.items()},all_clipped_facets=facets,force_residual_N=forceerr,pullback_error_N=pullerr,energy_Nmm=energy,independent_free_spin_residual_Nmm=tor.tolist(),keeper_force_N=resultant.tolist(),keeper_deformed_moment_Nmm=moment.tolist(),active_rim_rows=rim,sharp_edge_cone_scope='Socketrim cone only; plug facet pressure distribution andcurvedSTEP domain remain separate.',accepted83body_physical_equilibria=0))
 dump(out/'summary.json',dict(status='FINITE_SOCKET_INDEPENDENT_AUDIT',candidate=s['candidate'],producer=ref(out/'producer.py'),rows=rows,all_checks_pass=all(all(q['checks'].values()) for q in rows),newly_qualified_system_gate_ids=[],whole_system_release=False));print(json.dumps(rows));return 0 if all(all(q['checks'].values()) for q in rows) else 2
if __name__=='__main__':sys.exit(main())
