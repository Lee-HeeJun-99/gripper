"""Independent asinh rectangle-integral and off-collocation physical audit."""
import json,sys,shutil
from decimal import Decimal,localcontext
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def F(x,y):
 a=np.zeros(np.broadcast_shapes(x.shape,y.shape));xx=np.broadcast_to(x,a.shape);yy=np.broadcast_to(y,a.shape);np.multiply(xx,np.arcsinh(np.divide(yy,abs(xx),out=np.zeros_like(a),where=xx!=0)),out=a);a+=yy*np.arcsinh(np.divide(xx,abs(yy),out=np.zeros_like(a),where=yy!=0));return a
def integ(x,y,hx,hy):return F(x+hx,y+hy)-F(x-hx,y+hy)-F(x+hx,y-hy)+F(x-hx,y-hy)
def exactgap(y):
 with localcontext() as c:
  c.prec=55;r=Decimal(1);R=Decimal('1.05');s=Decimal(str(float(y)));return float((R*R-s*s).sqrt()-(r*r-s*s).sqrt()-(R-r))
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated/primaryP1_pin_local_contact32/summary.json';s=json.loads(src.read_text());inp=json.loads((REPO/s['inputs']['path']).read_text());a=np.load(REPO/s['fields']['path']);rows=[];E=inp['conditional_Root_E_MPa'];nu=inp['conditional_Root_nu'];assert sha(REPO/s['candidate']['path'])==s['candidate']['SHA256'];assert all(s['checks'].values())
 for q in s['results']:
  key=q['key'];xy=a[key+'_x_y_mm'];x,y=xy.T;f=a[key+'_forces_N'];nx,ny=q['nx'],q['ny'];L=q['axial_interval_mm'][1]-q['axial_interval_mm'][0];dx=L/nx;dy=float(np.unique(y)[1]-np.unique(y)[0]);c=q['opposing_compliance_factor']*(1-nu*nu)/(np.pi*E);K=c*integ(x[:,None]-x,y[:,None]-y,dx/2,dy/2)/(dx*dy);u=K@f;g=np.array([exactgap(v) for v in y]);res=g+u-q['indentation_mm'];active=f>q['conditional_load_N']*1e-12;scale=q['indentation_mm'];off=[]
  for sx,sy in [(-.25,-.25),(-.25,.25),(.25,-.25),(.25,.25)]:
   assert not(ROOT/'runtime/STOP').exists();tx=x+sx*dx;ty=y+sy*dy;uu=c*integ(tx[:,None]-x,ty[:,None]-y,dx/2,dy/2)@f/(dx*dy);rr=np.array([exactgap(v) for v in ty])+uu-scale;off.append(dict(offset_cell=[sx,sy],minimum_gap_mm=float(rr.min()),loaded_gap_maxabs_mm=float(abs(rr[active]).max()),relative_loaded_gap_error=float(abs(rr[active]).max()/scale),penetration_sample_count=int((rr < -1e-10).sum())))
  rows.append(dict(key=key,independent_displacement_error_mm=float(abs(u-a[key+'_displacement_mm']).max()),high_precision_gap_error_mm=float(abs(g-a[key+'_gap_mm']).max()),independent_energy_relative_error=float(abs(float(f@u/2)/q['local_elastic_energy_Nmm']-1)),loaded_discrete_gap_error_mm=float(abs(res[active]).max()),minimum_discrete_gap_mm=float(res.min()),force_error_N=float(abs(f.sum()-q['conditional_load_N'])),normal_direction_max_difference=float(np.max(np.sqrt(2-2*np.sqrt(1-y*y)))),off_collocation=off,continuous_contact_certified=False))
 checks=dict(independent_center_displacement=all(r['independent_displacement_error_mm']<1e-12 for r in rows),high_precision_CAD_gap=all(r['high_precision_gap_error_mm']<1e-18 for r in rows),discrete_complementarity=all(r['loaded_discrete_gap_error_mm']<1e-12 and r['minimum_discrete_gap_mm']>-1e-12 for r in rows),force=all(r['force_error_N']<1e-12 for r in rows),local_energy_reconstruction=all(r['independent_energy_relative_error']<1e-7 for r in rows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_INDEPENDENT_LOCAL_CONTACT_AND_OFF_CELL_AUDIT_NOT_RELEASE',candidate=s['candidate'],source=ref(src),verifier=ref(out/'verifier.py'),checks=checks,results=rows,newly_qualified_system_gate_ids=[],accepted_product_equilibria=0,whole_system_release=False,off_cell_is_diagnostic_not_new_acceptance_tolerance=True,limitations=['Independent rectangle integral checks the same half-space approximation, not finite-body physical validity.','55digit CAD gap checks seated cylinder geometry without subtractive cancellation.','Off-center loaded gap errors and penetration retained; center collocation does not certify continuous complementarity.','Finite end surfaces, curved-vector traction/work, otherbody materials and global coupling unresolved. No force/energy/strength/release gate PASS.']))
 print(json.dumps(dict(checks=checks,max_offcell_relative=max(v['relative_loaded_gap_error'] for r in rows for v in r['off_collocation']),max_offcell_penetration_mm=min(v['minimum_gap_mm'] for r in rows for v in r['off_collocation']))))
if __name__=='__main__':main()
