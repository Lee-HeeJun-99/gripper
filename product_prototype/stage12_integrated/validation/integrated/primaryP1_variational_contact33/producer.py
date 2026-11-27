"""Actual P1 curved pin interface: variational local enrichment candidate.
Finite axial traction domain is retained. The elastic kernel remains a local
halfspace, explicitly NOT a finite-body/end-free-surface solution.
"""
import json,sys,time,shutil
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_pin_contact32 import kernel,qp

def radial_gap(t,r,R):
 c=R-r;rho=np.sqrt(R*R-4*c*r*np.sin(t/(2*r))**2)
 return 4*c*r*np.sin(t/(2*r))**2/(R+rho)

def averaged_kernel(nx,ny,dx,dy,q):
 # Galerkin target/source cell averaging; source integral is analytic.
 z,w=leggauss(q);ix,iy=np.meshgrid(np.arange(nx),np.arange(ny),indexing='ij');D=np.zeros((nx,ny))
 for u,wu in zip(z,w):
  for v,wv in zip(z,w):D+=wu*wv/4*kernel(ix*dx+u*dx/2,iy*dy+v*dy/2,dx,dy)/(dx*dy)
 ids=np.c_[ix.ravel(),iy.ravel()];return D[abs(ids[:,None,0]-ids[:,0]),abs(ids[:,None,1]-ids[:,1])]

def patch_map(x,t,r,R,yc,zc):
 # Arc measure dx dt on the actual pin cylinder. Bore point is its exact
 # radial closest point in the seated configuration, not a vertical pairing.
 c=R-r;theta=t/r;p=np.c_[x,yc+c+r*np.cos(theta),zc+r*np.sin(theta)]
 a=p-np.array([0,yc,zc]);a[:,0]=0;rho=np.linalg.norm(a,axis=1);n=a/rho[:,None];b=p+(R-rho)[:,None]*n
 J=np.c_[-n,-np.cross(p,n),n,np.cross(b,n)]
 return p,b,n,J

def map_cell_averages(x,t,dx,dt,r,R,yc,zc,q=8):
 z,w=leggauss(q);J=np.zeros((len(x),12))
 for a,wa in zip(z,w):
  for b,wb in zip(z,w):J+=wa*wb/4*patch_map(x+a*dx/2,t+b*dt/2,r,R,yc,zc)[3]
 return J

def main():
 tag=sys.argv[1];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');start=time.monotonic();assert not(ROOT/'runtime/STOP').exists()
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==78
 assert all(sha(REPO/v['path'])==v['SHA256'] for v in cad['part_references'].values())
 gp=ROOT/'validation/integrated/primaryP1_gamma_attachment29/pin_hole_geometry.json';geos=json.loads(gp.read_text());sp=ROOT/'validation/integrated/primaryP1_pin_mode29/summary.json';total=next(v['total_necessary_pin_reaction_N'] for v in json.loads(sp.read_text())['results'] if v['case']=='tilt_minus')
 E=200000.;nu=.3;factor=2.;c=factor*(1-nu*nu)/(np.pi*E);P=total/4
 dump(out/'inputs.json',dict(candidate=ref(cp),geometry=ref(gp),load_source=ref(sp),load_N=P,load_rule='Each port independently receives total/4 ONLY as conditional contrast. Actual split NOT solved.',conditional_E_MPa=E,conditional_nu=nu,opposing_compliance_factor=factor,material_source=ref(ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/h2_fivebody_reference.npz'),kernel_source=ref(ROOT/'scripts/primary_pin_contact32.py'),material_minimum_qualified=False,producer=ref(out/'producer.py')))
 fields={};rows=[]
 for gi in [0,2]:
  g=geos[gi];r=g['pin']['radius_mm'];R=g['hole']['radius_mm'];L=g['finite_axial_overlap_mm'];lo=max(g['pin']['bounds_mm'][0],g['hole']['bounds_mm'][0]);yc,zc=g['hole']['axis_point_mm'][1:];a=np.sqrt(4*P/(1/r-1/R)/(np.pi*L*(E/(1-nu*nu)/factor)));width=2.5*a
  for nx,ny in [(4,24),(8,24),(16,24),(8,48),(8,96)]:
   dx=L/nx;dt=2*width/ny;xx,tt=np.meshgrid(lo+(np.arange(nx)+.5)*dx,(np.arange(ny)+.5)*dt-width,indexing='ij');x=xx.ravel();t=tt.ravel();z,w=leggauss(48);gbar=sum(wi/2*radial_gap(t+zi*dt/2,r,R) for zi,wi in zip(z,w));scale=P*c/L
   for q in [12,24,48]:
    assert not(ROOT/'runtime/STOP').exists();K=c*averaged_kernel(nx,ny,dx,dt,q);f,delta,kkt,it=qp(K*P/scale,gbar/scale);f*=P;delta*=scale;u=K@f;J=map_cell_averages(x,t,dx,dt,r,R,yc,zc);W=J.T@f;res=gbar+u-delta;active=f>P*1e-12;key=f'p{gi}_{nx}_{ny}_q{q}'
    # Independent point-gap audit uses exact source integration, no averaging.
    probes=[]
    for ox,ot in [(-.45,-.45),(-.25,.25),(0.,0.),(.25,-.25),(.45,.45)]:
     xp=x+ox*dx;tp=t+ot*dt;up=c*kernel(xp[:,None]-x,tp[:,None]-t,dx,dt)/(dx*dt)@f;rr=radial_gap(tp,r,R)+up-delta;probes.append(dict(offset=[ox,ot],minimum_gap_mm=float(rr.min()),loaded_gap_relative_error=float(abs(rr[active]).max()/delta)))
    fields[key+'_force_N']=f;fields[key+'_x_t_mm']=np.c_[x,t];fields[key+'_J']=J;fields[key+'_average_gap_mm']=gbar;fields[key+'_average_displacement_mm']=u
    rows.append(dict(key=key,port=gi,part=g['part'],nx=nx,ny=ny,target_gauss_order=q,dx_mm=dx,dt_mm=dt,r_mm=r,R_mm=R,axis_yz_mm=[yc,zc],interval_mm=[lo,lo+L],conditional_load_N=P,indentation_mm=delta,energy_Nmm=float(f@u/2),peak_pressure_MPa=float(f.max()/(dx*dt)),force_error_N=float(abs(f.sum()-P)),average_KKT_normalized=kkt,average_gap_min_mm=float(res.min()),average_loaded_gap_error_mm=float(abs(res[active]).max()),iterations=it,body_wrench_N_Nmm=W.tolist(),pair_force_error_N=float(np.linalg.norm(W[:3]+W[6:9])),pair_moment_error_Nmm=float(np.linalg.norm(W[3:6]+W[9:])),offcell=probes,actual_four_port_split_solved=False,finite_body_end_correction_implemented=False))
 np.savez_compressed(out/'fields.npz',**fields)
 comparisons=[]
 for gi in [0,2]:
  by={(v['nx'],v['ny'],v['target_gauss_order']):v for v in rows if v['port']==gi}
  for variable,A,B in [('axial',(4,24,48),(8,24,48)),('axial',(8,24,48),(16,24,48)),('transverse',(8,24,48),(8,48,48)),('transverse',(8,48,48),(8,96,48))]+[('integration',(nx,ny,24),(nx,ny,48)) for nx,ny in [(4,24),(8,24),(16,24),(8,48),(8,96)]]:
   rel={k:abs(by[B][k]/by[A][k]-1) for k in ['indentation_mm','energy_Nmm','peak_pressure_MPa']};comparisons.append(dict(port=gi,variable=variable,coarse=A,fine=B,relative_change=rel,original_1percent_response_pass=all(v<=.01 for v in rel.values())))
 checks=dict(nonnegative_load_and_force=all(v['force_error_N']<1e-12 for v in rows),average_contact_KKT=all(v['average_KKT_normalized']<1e-8 for v in rows),pair_force_and_torque=all(v['pair_force_error_N']<1e-12 and v['pair_moment_error_Nmm']<1e-12 for v in rows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_VARIATIONAL_CURVED_INTERFACE_CONTRAST_NOT_FINITE_BODY_CONTACT',candidate=ref(cp),inputs=ref(out/'inputs.json'),fields=ref(out/'fields.npz'),results=rows,comparisons=comparisons,checks=checks,elapsed_s=time.monotonic()-start,actual_CAD_change_files=[],newly_qualified_system_gate_ids=[],accepted_product_equilibria=0,whole_system_release=False,limitations=['Actual78part product interfaces only; unchanged actual assembly/BOM. No new CAD or assembly qualification.','Galerkin cell-average gap law is NOT pointwise complementarity. Independent probes retain failures.','Scalar local tangent-plane halfspace compliance with exact radial CAD gap and vector wrench pullback. Not the curved finite-body Green tensor; no actual free-end boundary condition.','Both material halves conditional same E/nu, not actual Front/Rail source qualification. Each port independently total/4, not load split.','Clamps, four-port coupling, thread/bore, real Baseanchor, full sourcefield/globalenergy/mesh/time/system gates unresolved.']))
 print(json.dumps(dict(checks=checks,rows=len(rows),failed_comparisons=sum(not v['original_1percent_response_pass'] for v in comparisons),max_offcell_relative=max(p['loaded_gap_relative_error'] for v in rows for p in v['offcell']),elapsed_s=time.monotonic()-start)))
if __name__=='__main__':main()
