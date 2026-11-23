"""Independent small-strain CST algebra reference,NOT a SOFA solver or forcefield.
Uses actual coupon mesh/load; also tests exact nodal pure-bending interpolation.
No integration,contact,pressure law,or modification of Native states.
"""
import argparse,csv,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from analyse import BASE,sha
from native_bending_coupon import guarded
def elastic(E,nu):
 lam=E*nu/((1+nu)*(1-2*nu));mu=E/(2*(1+nu));D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu;return D
def element(q,D):
 X=np.column_stack([np.ones(4),q]);g=np.linalg.inv(X)[1:].T;B=np.zeros((6,12))
 for a,(x,y,z) in enumerate(g):
  B[:,3*a:3*a+3]=[[x,0,0],[0,y,0],[0,0,z],[y,x,0],[0,z,y],[z,0,x]]
 V=abs(np.linalg.det((q[1:]-q[0]).T))/6;return V,B,V*B.T@D@B
def reference(q,tet,F,E=2.5e9,nu=.3):
 D=elastic(E,nu);ii=[];jj=[];vv=[];records=[]
 for t in tet:
  V,B,K=element(q[t],D);ids=(3*t[:,None]+np.arange(3)).ravel();ii.extend(np.repeat(ids,12));jj.extend(np.tile(ids,12));vv.extend(K.ravel());records.append((t,V,B))
 K=coo_matrix((vv,(ii,jj)),shape=(q.size,q.size)).tocsc();fixed=np.flatnonzero(np.repeat(q[:,0]==0,3));free=np.setdiff1d(np.arange(q.size),fixed);u=np.zeros(q.size);u[free]=spsolve(K[free][:,free],F.ravel()[free]);reaction=K@u-F.ravel();strain=[(V,B@u.reshape(-1,3)[t].ravel()) for t,V,B in records];energy=sum(.5*V*(e@D@e) for V,e in strain);shear=sum(.5*V*(e[3:]@D[3:,3:]@e[3:]) for V,e in strain)
 # Exact 3D displacement field with epsilon_xx=-k(z-h/2),other normal0,
 # zero shear in the continuum. k=1/m,NOT a physical load test.
 ub=np.zeros_like(q);ub[:,0]=-q[:,0]*(q[:,2]-.0001);ub[:,2]=.5*q[:,0]**2;eb=[]
 for t,V,B in records:
  e=B@ub[t].ravel();eb.append((V,e))
 Ub=sum(.5*V*(e@D@e) for V,e in eb);Sb=sum(.5*V*(e[3:]@D[3:,3:]@e[3:]) for V,e in eb);exact=.5*D[0,0]*.01*.04*.0002**3/12
 return dict(u=u.reshape(-1,3),K=K,free=free,reference_tip_m=float(u.reshape(-1,3)[q[:,0]==.04,2].mean()),reference_energy_J=float(energy),reference_tip_shear_energy_fraction=float(shear/energy),reference_free_residual_N=float(abs(reaction[free]).max()),reference_root_reaction_N=reaction.reshape(-1,3)[q[:,0]==0].sum(axis=0).tolist(),volume_m3=float(sum(V for t,V,B in records)),pure_bending_interpolant_energy_ratio=float(Ub/exact),pure_bending_interpolant_shear_fraction=float(Sb/Ub))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',60)));return
 src=BASE/'results/layer_free1189';m=json.loads((src/'mesh.json').read_text());q=np.array(m['q0']);tet=np.array(m['tetrahedra']);F=np.zeros_like(q);F[q[:,0]==.04,2]=-1e-4/8;r=reference(q,tet,F)
 with (src/'layer0.csv').open() as f:rows=list(csv.DictReader(f))
 native=np.fromstring(rows[-1]['q'],sep=' ').reshape(-1,3)-q;tip=float(native[q[:,0]==.04,2].mean());res=r['K']@native.ravel()-F.ravel();E=2.5e9;EI=E*.01*.0002**3/12;euler=-5e-5*.04**3/(3*EI);summary={k:v for k,v in r.items() if k not in ('u','K','free')};summary.update(status='INDEPENDENT_CST_REFERENCE_ONLY',actual_native_tip_m=tip,approximate_Euler_tip_m=euler,native_vs_CST_tip_relative_error=abs(tip-r['reference_tip_m'])/abs(r['reference_tip_m']),actual_vs_reference_max_displacement_error_m=float(abs(native-r['u']).max()),native_in_linear_reference_free_residual_N=float(abs(res[r['free']]).max()),native_in_linear_reference_residual_relative=float(np.linalg.norm(res[r['free']])/np.linalg.norm(F.ravel()[r['free']])),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={str((src/f).relative_to(BASE)):sha(src/f) for f in ('scene.scn','mesh.json','preflight.json','layer0.csv')},scope='CST small-strain algebra reference vs actual settled Native large-FEM output. Euler is approximate beam reference,not exact3D. Pure bending field has prescribed nodal geometry ONLY as interpolation test,NOT dynamic actuation/grasp. No pressure/jamming/mesh qualification.',physical_validation='NOT QUALIFIED');np.savetxt(out/'reference_u_m.csv',r['u'],delimiter=',');(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
if __name__=='__main__':main()
