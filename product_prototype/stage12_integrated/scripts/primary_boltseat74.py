"""Actual P1: separate free axial head seating from the old imposed screw lead.
Finite actual BRep head/Root patches; full24 necessary wrench LP. No preload
or thread/nut constitutive closure is inferred from a feasible contact cone.
"""
import sys,json,shutil,math,time
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
from primary_keeper_coupled71 import faces,pointdist,wrench,rot
from primary_shoulder_coupled73 import axial_bounds
from primary_clocked62 import spin
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,bounds
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.TopAbs import TopAbs_REVERSED,TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

def planes(shape,nz):
 ret=[]
 for face in faces(shape):
  ad=BRepAdaptor_Surface(face)
  if ad.GetType()!=GeomAbs_Plane:continue
  n=ad.Plane().Axis().Direction();z=n.Z()*(-1 if face.Orientation()==TopAbs_REVERSED else 1)
  if abs(z-nz)<1e-8:ret.append((face,ad.Plane().Location().Z()))
 return ret

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_shoulder73a/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);old=ROOT/'validation/integrated/primaryP1_shouldercoupled73/summary.json';previous=json.loads(old.read_text())['rows'][0];assert previous['signs']==[1,1];x=np.array(previous['solution']);settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];keeper=read(REPO/refs['ROOT_SOCKET_KEEPER']['path']);host=read(REPO/refs['F0_ROOT_BACK']['path']);pk=translate(spin(keeper,60,0,math.degrees(x[2])),x[0],x[1],0);bolts=[]
 for i,q in enumerate(settings):
  off=3+3*i;b=read(REPO/refs[q['bolt']]['path']);bolts.append(translate(spin(b,q['x'],q['y'],math.degrees(x[off+2])),x[off],x[off+1],0))
 bodies=[pk,*bolts,host];columns=[];meta=[]
 def add(i,j,p,n,label):
  col=np.zeros((4,6));col[i]=wrench(p,n);col[j]=-col[i];columns.append(col.ravel());meta.append(dict(body_i=i,body_j=j,point_mm=p.tolist(),normal_on_i=n.tolist(),label=label,distance_i_mm=pointdist(bodies[i],p),distance_j_mm=pointdist(bodies[j],p)))
 # Retain all genuine previous socket/bore/tongue/shoulder witnesses that still
 # lie on both actual bodies after independently seating the bolts axially.
 dropped=[]
 for c in previous['contacts']:
  i,j=c['body_i'],c['body_j'];p=np.array(c['point_mm']);n=np.array(c['normal_on_i'])
  if max(pointdist(bodies[i],p),pointdist(bodies[j],p))<1e-7:add(i,j,p,n,c['label'])
  else:dropped.append(c)
 patches=[]
 for bi,b in enumerate(bolts):
  for bf,bz in planes(b,-1):
   for hf,hz in planes(host,1):
    if abs(bz-hz)>1e-9:continue
    cut=BRepAlgoAPI_Common(bf,hf);cut.Build();assert cut.IsDone();patch=cut.Shape();gp=GProp_GProps();BRepGProp.SurfaceProperties_s(patch,gp)
    if gp.Mass()<1e-10:continue
    cg=gp.CentreOfMass();points=[np.array([cg.X(),cg.Y(),cg.Z()])];ex=TopExp_Explorer(patch,TopAbs_VERTEX)
    while ex.More():
     pt=BRep_Tool.Pnt_s(TopoDS.Vertex_s(ex.Current()));points.append(np.array([pt.X(),pt.Y(),pt.Z()]));ex.Next()
    unique={tuple(np.round(p,11)):p for p in points};valid=[]
    for p in unique.values():
     if max(pointdist(bf,p),pointdist(hf,p))<1e-7:add(1+bi,3,p,np.array([0.,0.,1.]),'actual_finite_headseat_Root_patch');valid.append(p.tolist())
    patches.append(dict(bolt_index=bi,z_mm=bz,area_mm2=gp.Mass(),finite_points_mm=valid))
 ext=np.zeros((4,6));ext[1:3,5]=previous['torque_Nmm']
 for bi,shape in enumerate(bodies[:3]):
  gp=GProp_GProps();BRepGProp.VolumeProperties_s(shape,gp);cg=gp.CentreOfMass();ext[bi]+=wrench(np.array([cg.X(),cg.Y(),cg.Z()]),np.array([0.,0.,-gp.Mass()*7.9e-6*9.80665]))
 A=np.column_stack(columns);P=np.zeros((24,6));P[-6:]=np.eye(6);AP=np.c_[A,P];eq=linprog(np.r_[np.ones(A.shape[1]),np.zeros(6)],A_eq=AP,b_eq=-ext.ravel(),bounds=[(0,None)]*A.shape[1]+[(None,None)]*6,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});hits=dict(keeper_host_mm3=common(pk,host),keeper_bolts_mm3=[common(pk,b) for b in bolts],bolts_host_mm3=[common(b,host) for b in bolts]);checks=dict(all83hashes=True,both_actual_headseat_patches={q['bolt_index'] for q in patches}=={0,1},all_witnesses=all(max(q['distance_i_mm'],q['distance_j_mm'])<1e-7 for q in meta),subassembly_no_interference=max([hits['keeper_host_mm3'],*hits['keeper_bolts_mm3'],*hits['bolts_host_mm3']])<=1e-8,full24_necessary_equilibrium=bool(eq.success));result={}
 if eq.success:
  residual=(AP@eq.x+ext.ravel()).reshape(4,6);result=dict(normal_forces_N=eq.x[:A.shape[1]].tolist(),host_external_wrench_N_Nmm=eq.x[-6:].tolist(),all24_original_residual_N_Nmm=residual.tolist(),maximum_residual=float(abs(residual).max()));checks['all24_original_tolerance']=result['maximum_residual']<1e-8
 else:
  cert=linprog(-ext.ravel(),A_ub=-A.T,b_ub=np.zeros(A.shape[1]),A_eq=P.T,b_eq=np.zeros(6),bounds=[(-1,1)]*24,method='highs');result=dict(certificate_success=bool(cert.success))
  if cert.success:result.update(separating_body_twists=cert.x.reshape(4,6).tolist(),minimum_column_work=float((A.T@cert.x).min()),required_work=float((-ext.ravel())@cert.x))
 dump(out/'summary.json',dict(status='ACTUAL_P1_AXIAL_HEADSEAT_NECESSARY_CONE_ONLY' if all(checks.values()) else 'ACTUAL_P1_AXIAL_HEADSEAT_FAIL',candidate_reference=ref(cp),producer=ref(out/'producer.py'),previous=ref(old),checks={k:bool(v) for k,v in checks.items()},pose_planar=x.tolist(),actual_bolt_axial_translation_mm=[0.,0.],old_imposed_lead_translation_mm=[.5*x[5]/(2*np.pi),.5*x[8]/(2*np.pi)],mechanism='Independent axial head seating replaces old imposed spin/lead translation. Finite actual planar headunderside/Root BRep intersection; full24 original wrenches.',actual_headseat_patches=patches,contacts=meta,removed_old_nonwitnesses=dropped,interferences=hits,external_body_wrenches_N_Nmm=ext.tolist(),LP_message=eq.message,result=result,actual_CAD_changed=[],accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Necessary finite frictionlesscontact cone at one recorded planarpose, not free3Dtilt equilibrium or stability. Host has explicit external6wrench cut.','Bolt head axialmotion independent of spin; actual nut threadflank compatibility/elasticpreload and freetilt remain unsolved. No arbitrary axialreaction supplied at axis.','Only actualheadseat subsetpoints used; no continuouspressure/strength/tolerance/time/globalenergy/full83operatingPASS.','Conditional lead-derived torques remain bounds, not actual100g operating demand or tightening preload.']))
 print(json.dumps(dict(checks=checks,patches=patches,result=result,hits=hits)),flush=True);return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
