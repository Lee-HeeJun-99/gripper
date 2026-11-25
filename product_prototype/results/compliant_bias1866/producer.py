"""Physical finite-velocity prerequisite from actual rotor/cell masses and Cable response."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha

def terms(m,I,r,w):
 a=np.cross(w,np.cross(w,r));return np.r_[m*a,np.cross(w,I@w)+np.cross(r,m*a)]
def finite_difference(m,I,r,w,h):
 Rp=Rotation.from_rotvec(w*h).as_matrix();Rm=Rotation.from_rotvec(-w*h).as_matrix();a=(Rp@r+Rm@r-2*r)/(h*h);Idot=(Rp@I@Rp.T-Rm@I@Rm.T)/(2*h);return np.r_[m*a,Idot@w+np.cross(r,m*a)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());masspath=BASE/'results/compliant_mass1860/summary.json';cablepath=BASE/'results/compliant_cable1864/summary.json';mass=json.loads(masspath.read_text());cable=json.loads(cablepath.read_text());L=.003;r=.00025;rho=1000.;hcell=L/4;mc=rho*np.pi*r*r*hcell;Ic=mc*np.diag([r*r/2,(3*r*r+hcell*hcell)/12,(3*r*r+hcell*hcell)/12]);rc=np.array([-L/8,0,0]);mr=mass['rotor_mass_kg'];Ir=np.array(mass['rotor_COM_inertia_kg_m2']);rr=np.array(mass['rotor_COM_m'])-[L,0,0];records=[]
 for rec in cable['records']:
  # At the declared initial geometry, use the independently validated actual
  # accepted velocity as a finite-speed evaluation point, not a saved Native force.
  w=np.array(rec['actual_tip_v'][3:]);b=terms(mc,Ic,rc,w)+terms(mr,Ir,rr,w);fd=[]
  for h in (.1,.05):
   estimate=finite_difference(mc,Ic,rc,w,h)+finite_difference(mr,Ir,rr,w,h);fd.append(dict(h_s=h,relative_vector_difference=float(np.linalg.norm(estimate-b)/np.linalg.norm(b))))
  pure=np.array([w[0],0,0]);bpure=terms(mc,Ic,rc,pure)+terms(mr,Ir,rr,pure)
  records.append(dict(case=rec['case'],omega_rad_s=w.tolist(),physical_bias_force_N=b[:3].tolist(),physical_bias_moment_Nm=b[3:].tolist(),finite_difference=fd,pure_axial_contrast_bias=bpure.tolist(),scope='Independent rest-geometry finite-speed wrench evaluated at actual1864velocity, not measured Native inertial force. Tiny numerical off-axis rotor COM/tensor terms retained, no floor or assumed zero.'))
 sources=[Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Mass/sofa/component/mass/UniformMass.inl'),Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Mapping.NonLinear/sofa/component/mapping/nonlinear/RigidMapping.inl')]
 d=dict(status='BLOCKED_SUPPORTED_FINITE_SPEED_FORCE_PATH',independent_wrench_FD_contract='PASS' if all(x['relative_vector_difference']<=1e-6 for rec in records for x in rec['finite_difference']) else 'FAIL_FD_REFERENCE',records=records,input_sha256={str(f):sha(f) for f in [masspath,cablepath,*sources]},source_sha256=sha(Path(__file__)),supported_native_implementation=None,scope='Generic installed UniformMass.addForce471-497 uses gravity, no velocity; RigidMapping.applyDJT is a derivative force action, not proof of convective acceleration compensation. Earlier1806/1807Native failure already demonstrates a relevant mapping limitation; do not rerun it without a new supported implementation. Pure axial torsion and mixed input have different physical bias; no claim this tiny initial bias explains full100g failure. Need documented Native coupled gyroscopic/centrifugal path or distinct mechanism. No SDK/customforcefield/state correction or Native rerun, no grasp PASS.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
