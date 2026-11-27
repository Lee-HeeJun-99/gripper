"""Actual P1 pin local unilateral half-space contrast, not finite-body qualification.
Exact stable internal-cylinder seated gap; integrated rectangular Boussinesq
kernel. Conditional total loads are sensitivities, never an adopted pin split.
"""
import sys,json,shutil,time
import numpy as np
from scipy.linalg import solve
from baseline_registry import ROOT,REPO,ref,sha,dump

def primitive(x,y):
 r=np.hypot(x,y)
 # xy=0 limits evaluated continuously; arguments positive away from axes.
 return x*np.log(np.maximum(y+r,1e-300))+y*np.log(np.maximum(x+r,1e-300))
def kernel(x,y,dx,dy):
 return (primitive(x+dx/2,y+dy/2)-primitive(x-dx/2,y+dy/2)-primitive(x+dx/2,y-dy/2)+primitive(x-dx/2,y-dy/2))
def gap(s,r,R):
 # (r-sqrt(r^2-s^2))-(R-sqrt(R^2-s^2)), no cancellation.
 return s*s*(1/(r+np.sqrt(r*r-s*s))-1/(R+np.sqrt(R*R-s*s)))
def qp(H,g):
 # Primal feasible active-set simplex QP; fraction loads sum to one.
 n=len(g);z=np.zeros(n);z[np.argmin(g)]=1;active=set(np.flatnonzero(z));iterations=0
 for iterations in range(8*n):
  ids=np.array(sorted(active));A=H[np.ix_(ids,ids)];one=np.ones(len(ids));v=solve(A,one,assume_a='pos');w=solve(A,g[ids],assume_a='pos');delta=(1+one@w)/(one@v);target=delta*v-w
  if target.min() < -1e-12:
   direction=target-z[ids];bad=direction< -1e-15;alpha=min(1.,float(np.min(-z[ids][bad]/direction[bad])));z[ids]+=alpha*direction
   for i in ids[z[ids]<1e-13]:z[i]=0;active.discard(int(i))
  else:
   z[:]=0;z[ids]=np.maximum(target,0);z/=z.sum();grad=H@z+g;res=grad-delta;res[ids]=np.inf;j=int(np.argmin(res))
   if res[j]>=-1e-9:break
   active.add(j)
 else:raise RuntimeError('active set did not converge')
 grad=H@z+g;delta=float(z@grad);kkt=max(float(abs(grad[z>1e-12]-delta).max()),max(0.,float(-(grad-delta).min())))
 return z,delta,kkt,iterations+1

def main():
 tag=sys.argv[1];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();start=time.monotonic()
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==78
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
 gp=ROOT/'validation/integrated/primaryP1_gamma_attachment29/pin_hole_geometry.json';geos=json.loads(gp.read_text());sp=ROOT/'validation/integrated/primaryP1_pin_mode29/summary.json';src=json.loads(sp.read_text());total=next(r['total_necessary_pin_reaction_N'] for r in src['results'] if r['case']=='tilt_minus');mp=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/h2_fivebody_reference.npz';m=np.load(mp);E=float(m['F0_ROOT_BACK_E_MPa']);nu=float(m['F0_ROOT_BACK_nu'])
 dump(out/'inputs.json',dict(candidate=ref(cp),geometry=ref(gp),source=ref(sp),conditional_Root_E_MPa=E,conditional_Root_nu=nu,material_reference=ref(mp),opposing_material_qualified=False,law='Boussinesq elastic half-space normal compliance (1-nu^2)/(pi E) times rectangle integral1/r; opposing body rigid or identical conditional half-space. Exact seated CAD internal-cylinder gap. Frictionless tangent-plane normal law; not curved vector traction or finite-body contact.',load_rule='P=total or total/4 on EACH tested port independently. Not simultaneous four-port load allocation.',producer=ref(out/'producer.py')))
 results=[];fields={}
 for gi in [0,2]:
  geo=geos[gi];L=geo['finite_axial_overlap_mm'];r=geo['pin']['radius_mm'];R=geo['hole']['radius_mm'];Reff=1/(1/r-1/R)
  for factor in [1.,2.]:
   c=factor*(1-nu*nu)/(np.pi*E);Estar=factor**-1*E/(1-nu*nu)
   for loadfrac in [.25,1.]:
    P=total*loadfrac;a=np.sqrt(4*P*Reff/(np.pi*L*Estar));width=2.5*a
    for nx,ny in [(4,24),(8,24),(16,24),(8,48),(8,96)]:
     assert not(ROOT/'runtime/STOP').exists();dx=L/nx;dy=2*width/ny;x,y=np.meshgrid((np.arange(nx)+.5)*dx,(np.arange(ny)+.5)*dy-width,indexing='ij');x=x.ravel();y=y.ravel();area=dx*dy;K=c*kernel(x[:,None]-x,y[:,None]-y,dx,dy)/area;K=(K+K.T)/2;g=gap(y,r,R);scale=P*c/L;H=K*P/scale;z,delta,kkt,it=qp(H,g/scale);f=P*z;u=K@f;closure=delta*scale;res=g+u-closure;loaded=z>1e-12;pressure=f/area;key=f'p{gi}_f{factor:g}_l{loadfrac:g}_{nx}_{ny}';fields[key+'_x_y_mm']=np.c_[x,y];fields[key+'_forces_N']=f;fields[key+'_gap_mm']=g;fields[key+'_displacement_mm']=u
     # Real finite interval edges: half-space ignores the nearby free end.
     edge=np.minimum(x,L-x);edge_overlap=np.maximum(0,np.minimum(x+dx/2,5*a)-np.maximum(x-dx/2,0))+np.maximum(0,np.minimum(x+dx/2,L)-np.maximum(x-dx/2,L-5*a));edge_fraction=float(f@edge_overlap/(P*dx));energy=float(f@u/2);row=dict(key=key,port=gi,part=geo['part'],symmetric_other_port=gi+1,axial_interval_mm=[max(geo['pin']['bounds_mm'][0],geo['hole']['bounds_mm'][0]),min(geo['pin']['bounds_mm'][3],geo['hole']['bounds_mm'][3])],nx=nx,ny=ny,opposing_compliance_factor=factor,conditional_load_N=P,Hertz_scale_halfwidth_mm=a,solved_center_halfwidth_mm=float(abs(y[loaded & (abs(x-L/2)<dx*.51)]).max()+dy/2),peak_pressure_MPa=float(pressure.max()),indentation_mm=closure,local_elastic_energy_Nmm=energy,kkt_normalized=kkt,force_error_N=float(abs(f.sum()-P)),min_gap_residual_mm=float(res.min()),loaded_gap_error_mm=float(abs(res[loaded]).max()),iterations=it,halfspace_edge_zone_load_fraction=edge_fraction,patch_radius_ratio=a/r,axial_length_ratio=a/L,actual_four_port_split_solved=False)
     results.append(row)
 np.savez_compressed(out/'local_contact_fields.npz',**fields)
 comparisons=[]
 for gi in [0,2]:
  for fac in [1.,2.]:
   for frac in [.25,1.]:
    rows=[q for q in results if q['port']==gi and q['opposing_compliance_factor']==fac and abs(q['conditional_load_N']/total-frac)<1e-10];by={(q['nx'],q['ny']):q for q in rows}
    for v,a,b in [('axial',(4,24),(8,24)),('axial',(8,24),(16,24)),('transverse',(8,24),(8,48)),('transverse',(8,48),(8,96))]:
     dif={k:abs(by[b][k]/by[a][k]-1) for k in ['indentation_mm','local_elastic_energy_Nmm','peak_pressure_MPa','solved_center_halfwidth_mm']};comparisons.append(dict(port=gi,factor=fac,load_fraction=frac,variable=v,coarse=a,fine=b,relative_changes=dif,original_1percent_response_pass=all(v<=.01 for v in dif.values())))
 checks=dict(all_local_KKT=all(q['kkt_normalized']<1e-8 for q in results),positive_pressure_and_force=all(q['force_error_N']<1e-12 and q['peak_pressure_MPa']>0 for q in results),local_gap_complementarity=all(q['min_gap_residual_mm']>-1e-12 and q['loaded_gap_error_mm']<1e-12 for q in results))
 dump(out/'summary.json',dict(status='ACTUAL_P1_LOCAL_GAP_RESOLVED_CONTACT_CONTRAST_NOT_FINITE_BODY_RELEASE',candidate=ref(cp),inputs=ref(out/'inputs.json'),fields=ref(out/'local_contact_fields.npz'),results=results,mesh_comparisons=comparisons,checks=checks,elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_product_equilibria=0,whole_system_release=False,actual_CAD_change_files=[],limitations=['Actual CAD radii and finite overlaps; two mirror ports share scalar response only. Conditional selfweight/gamma load sensitivity, not100g operating demand.','Root half-space E/nu inherited conditionally. Rigid and identical opposing half-space are explicit contrasts, NOT Front/Rail material assignment or bracket of all physical materials.','Local normal tangent-plane compliance cannot certify actual curved normal/tangential virtual work, finite axial end free surfaces, Root/Front/Rail/clamp coupling,4port split, thread, bore, finite Baseanchor or full assembly equilibrium.','No original1percent full FEM mesh or0.1percent time/global energy qualification. Discrete gap complementarity only, not continuous between cells. Local elastic energy is not total energy.']))
 print(json.dumps(dict(checks=checks,rows=len(results),failed_mesh_comparisons=sum(not q['original_1percent_response_pass'] for q in comparisons),elapsed=time.monotonic()-start)))
if __name__=='__main__':main()
