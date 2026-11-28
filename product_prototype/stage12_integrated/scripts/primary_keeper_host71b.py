"""Actual Root keeper + two bolts + finite host: free planar clearance closure.
Replaces arbitrary radial support ports by actual1.7mm bore and2.1mm slot normals.
All24 original resultant rows checked. Externalhost wrench remains explicit.
"""
import sys,json,shutil,math,time
import numpy as np
from scipy.optimize import minimize,linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_keeper_coupled71 import faces,rot,pointdist,wrench
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,translate,common
from primary_clocked62 import spin
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Plane

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];keeper=read(REPO/refs['ROOT_SOCKET_KEEPER']['path']);host=read(REPO/refs['F0_ROOT_BACK']['path']);pin=read(REPO/refs['ROOT_SOCKET_KEEPER_INSTALLED_SPLIT_PIN']['path']);bolts=[read(REPO/refs[q['bolt']]['path']) for q in settings];anchor=np.array([60.,0.,0.]);groups=[]
 for q,b in zip(settings,bolts):
  c=np.array([q['x'],q['y'],0.]);cs=[];ws=[];bores=[];shanks=[]
  for f in faces(keeper):
   a=BRepAdaptor_Surface(f)
   if a.GetType()!=GeomAbs_Cylinder:continue
   cyl=a.Cylinder();o=cyl.Location();p=np.array([o.X(),o.Y(),o.Z()]);ax=cyl.Axis().Direction()
   if abs(cyl.Radius()-.15)<1e-7 and abs(ax.Z())>.99 and np.linalg.norm((p-c)[:2])<2:cs.append(dict(face=f,c=p,r=.15,bb=bounds(f)))
  for f in faces(b):
   a=BRepAdaptor_Surface(f)
   if a.GetType()==GeomAbs_Cylinder:
    cy=a.Cylinder();ax=cy.Axis().Direction()
    if abs(cy.Radius()-1.5)<1e-7 and abs(ax.Z())>.99:shanks.append(f)
   if a.GetType()!=GeomAbs_Plane:continue
   pl=a.Plane();o=pl.Location();ax=pl.Axis().Direction();p=np.array([o.X(),o.Y(),o.Z()]);n=np.array([ax.X(),ax.Y(),ax.Z()]);bb=bounds(f)
   if abs(n[2])<1e-7 and np.linalg.norm((np.array(bb[:3])+bb[3:])[:2]/2-c[:2])<2:
    if n@(c-p)<0:n=-n
    ws.append(dict(face=f,o=p,n=n,bb=bb))
  for f in faces(host):
   a=BRepAdaptor_Surface(f)
   if a.GetType()!=GeomAbs_Cylinder:continue
   cy=a.Cylinder();o=cy.Location();ax=cy.Axis().Direction()
   if abs(cy.Radius()-1.7)<1e-7 and abs(ax.Z())>.99 and np.linalg.norm(np.array([o.X(),o.Y()])-c[:2])<1e-7:bores.append(f)
  assert len(cs)==len(ws)==6 and len(bores)==len(shanks)==1;groups.append(dict(center=c,circles=cs,walls=ws,bore=bores[0],shank=shanks[0]))
 src=ROOT/'validation/integrated/primaryP1_keepercoupled71/summary.json';sr=json.loads(src.read_text());T=np.array(sr['rows'][0]['conditional_bolt_torque_Nmm']);corners=np.array([[59.,-1,0],[59,1,0],[61,-1,0],[61,1,0]])
 def state(x):
  R=rot(x[2]);shift=np.r_[x[:2],0.];hx=[];tg=[]
  for i,g in enumerate(groups):
   off=3+3*i;B=rot(x[off+2]);delta=np.r_[x[off:off+2],.5*x[off+2]/(2*np.pi)]
   for wi,w in enumerate(g['walls']):
    n=B@w['n'];o=B@(w['o']-g['center'])+g['center']+delta
    for ci,c in enumerate(g['circles']):
     cc=R@(c['c']-anchor)+anchor+shift;hx.append((float(n@(cc-o)-c['r']),i,wi,ci,n,cc,delta[2]))
  pc=(corners-anchor)@R.T+anchor+shift
  for ci,p in enumerate(pc):
   for ax,lo,hi in [(0,58.95,61.05),(1,-1.05,1.05)]:
    for side,gap in [(1,p[ax]-lo),(-1,hi-p[ax])]:
     n=np.eye(3)[ax]*side;tg.append((float(gap),ci,p,n))
  return hx,tg
 def gap(x):
  hx,tg=state(x);return np.r_[[r[0] for r in hx],[.2-np.linalg.norm(x[3:5]),.2-np.linalg.norm(x[6:8])],[r[0] for r in tg]]
 rows=[]
 for signs in [(1,1),(-1,-1),(1,-1),(-1,1)]:
  assert not(ROOT/'runtime/STOP').exists();torque=T*np.array(signs);load=np.zeros(9);load[[5,8]]=torque/max(abs(torque));history=[]
  def callback(x):history.append(dict(x=x.tolist(),minimum_gap_mm=float(gap(x).min())))
  res=minimize(lambda x:-load@x,np.zeros(9),jac=lambda x:-load,method='SLSQP',bounds=[(-.3,.3),(-.3,.3),(-.04,.04),(-.25,.25),(-.25,.25),(-.25,.25),(-.25,.25),(-.25,.25),(-.25,.25)],constraints=[dict(type='ineq',fun=gap)],callback=callback,options={'maxiter':400,'ftol':1e-13});x=res.x;hx,tg=state(x);columns=[];meta=[];pk=translate(spin(keeper,60,0,math.degrees(x[2])),x[0],x[1],0);pbs=[]
  for i,(b,g) in enumerate(zip(bolts,groups)):
   off=3+3*i;pbs.append(translate(spin(b,*map(float,g['center'][:2]),math.degrees(x[off+2])),*map(float,np.r_[x[off:off+2],.5*x[off+2]/(2*np.pi)])))
  def add(i,j,p,n,label):
   col=np.zeros((4,6));col[i]=wrench(p,n);col[j]=-col[i];columns.append(col.ravel());meta.append(dict(body_i=i,body_j=j,point_mm=p.tolist(),normal_on_i=n.tolist(),label=label,actual_body_i_distance_mm=pointdist([pk,*pbs,host][i],p),actual_body_j_distance_mm=pointdist([pk,*pbs,host][j],p)))
  for val,i,wi,ci,n,cc,dz in hx:
   if abs(val)>1e-7:continue
   c=groups[i]['circles'][ci];w=groups[i]['walls'][wi];zlo=max(c['bb'][2],w['bb'][2]+dz);zhi=min(c['bb'][5],w['bb'][5]+dz)
   for fraction in [1/6,.5,5/6]:p=cc-.15*n;p[2]=zlo+fraction*(zhi-zlo);add(0,1+i,p,n,'finite_hex_line')
  for i,g in enumerate(groups):
   off=3+3*i;delta=np.r_[x[off:off+2],0.];r=np.linalg.norm(delta)
   if abs(r-.2)<1e-7:
    radial=delta/r
    for z in [-6.5,-5,-3.5]:p=g['center']+1.7*radial;p[2]=z;add(1+i,3,p,-radial,'actual_Root_bore_shank_line')
  for val,ci,xy,n in tg:
   if abs(val)>1e-7:continue
   for z in [-2.7,-1.8,-1.2]:p=xy.copy();p[2]=z;add(0,3,p,n,'actual_tongue_slot_corner_line')
  A=np.column_stack(columns);ext=np.zeros((4,6));ext[1:3,5]=torque;P=np.zeros((24,6));P[-6:]=np.eye(6);AP=np.c_[A,P];eq=linprog(np.r_[np.ones(A.shape[1]),np.zeros(6)],A_eq=AP,b_eq=-ext.ravel(),bounds=[(0,None)]*A.shape[1]+[(None,None)]*6,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});planar=np.array([0,1,5,6,7,11,12,13,17,18,19,23]);peq=linprog(np.r_[np.ones(A.shape[1]),np.zeros(6)],A_eq=AP[planar],b_eq=-ext.ravel()[planar],bounds=[(0,None)]*A.shape[1]+[(None,None)]*6,method='highs');hits=dict(keeper_host_mm3=common(pk,host),keeper_pin_mm3=common(pk,pin),keeper_bolts_mm3=[common(pk,b) for b in pbs],bolts_host_mm3=[common(b,host) for b in pbs]);row=dict(signs=list(signs),torque_Nmm=torque.tolist(),solution=x.tolist(),optimizer_success=bool(res.success),optimizer_message=res.message,minimum_all90_gap_mm=float(gap(x).min()),bounds_inactive=bool(min(.3-abs(x[0]),.3-abs(x[1]),.04-abs(x[2]),min(.25-abs(x[3:])))>1e-4),full24_original_equilibrium=bool(eq.success),full24_message=eq.message,planar12_equilibrium=bool(peq.success),contacts=meta,interferences=hits,history=history,physical_fixed_planar_DOF=0,unknown_external_host6wrench_port=True)
  if eq.success:
   row.update(normal_force_N=eq.x[:A.shape[1]].tolist(),host_external_wrench_N_Nmm=eq.x[-6:].tolist(),all24_original_residual=(AP@eq.x+ext.ravel()).reshape(4,6).tolist(),maximum24_residual=float(abs(AP@eq.x+ext.ravel()).max()),minimum_normal_force_N=float(eq.x[:A.shape[1]].min()))
  if peq.success:row['planar_solution_original24_residual']=(AP@peq.x+ext.ravel()).reshape(4,6).tolist()
  rows.append(row);dump(out/('case_'+''.join('p' if a>0 else 'm' for a in signs)+'.json'),row)
 checks=dict(actual83hashes=True,all90_gap_constraints=all(r['minimum_all90_gap_mm']>=-1e-9 for r in rows),no_artificial_bound_support=all(r['bounds_inactive'] for r in rows),full24_equilibrium=all(r['full24_original_equilibrium'] and r['maximum24_residual']<1e-8 and r['minimum_normal_force_N']>=-1e-9 for r in rows),finite_actual_contact_witnesses=all(max(c['actual_body_i_distance_mm'],c['actual_body_j_distance_mm'])<1e-7 for r in rows for c in r['contacts']),actual_all_subassembly_interferences_zero=all(max([r['interferences']['keeper_host_mm3'],r['interferences']['keeper_pin_mm3'],*r['interferences']['keeper_bolts_mm3'],*r['interferences']['bolts_host_mm3']])<=1e-8 for r in rows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_ROOT_BORE_TONGUE_COUPLED_NECESSARY_CONTACT' if all(checks.values()) else 'ACTUAL_P1_FINITE_ROOT_BORE_TONGUE_CONTACT_FAIL_PRESERVED',candidate=ref(cp),producer=ref(out/'producer.py'),source=ref(src),checks={k:bool(v) for k,v in checks.items()},rows=rows,physical_fixed_planar_DOF=0,actual_CAD_changed=[],accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Nine planar unknowns free; full24 resultants retained. Remainingoutofplane kinematics, materialcompliance, preload, pinreaction and nut/support/threadcontact unsolved.','Finiteactualbore/slot normal reactions replace artificialradialport. Externalhost6wrench is a cut Neumann load, not actualground solution or hiddenphysicalfixation.','Rigidcontact LP is necessary/possiblynonunique, not actualelasticpressure/capacity. Torques remain conditional frictionlesslead bounds, not actualoperatingdemand.','Full83pose compatibility with remaining nut/support components not certified; sampledsubassembly geometry is not continuousCCD or threadflanklaw.','All22system gates and originalmesh/time/globalenergy/source/minimum/process/fullstroke/protection/mass/final3Finger unqualified.']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},rows=[{k:r.get(k) for k in ['signs','solution','full24_original_equilibrium','planar12_equilibrium','interferences']} for r in rows])));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
