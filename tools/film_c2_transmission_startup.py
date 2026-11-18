"""Independent high-precision two-DOF cubic-load transmission counterexample."""
import argparse,csv,json,shutil,subprocess
import mpmath as mp
from curve_common import ROOT,sha,write_json
def tableau(n):
 if n==2:c=[mp.mpf('.5')-mp.sqrt(3)/6,mp.mpf('.5')+mp.sqrt(3)/6]
 elif n==3:c=[mp.mpf('.5')-mp.sqrt(15)/10,mp.mpf('.5'),mp.mpf('.5')+mp.sqrt(15)/10]
 elif n==4:
  outer=mp.sqrt((3+2*mp.sqrt(mp.mpf(6)/5))/7);inner=mp.sqrt((3-2*mp.sqrt(mp.mpf(6)/5))/7);c=[(1-outer)/2,(1-inner)/2,(1+inner)/2,(1+outer)/2]
 else:raise ValueError('declared2/3/4 stage collocation only')
 A=mp.matrix(n);b=mp.matrix(n,1)
 for j in range(n):
  poly=[mp.mpf(1)]
  for k in range(n):
   if k==j:continue
   out=[mp.mpf(0)]*(len(poly)+1)
   for d,x in enumerate(poly):out[d]-=x*c[k]/(c[j]-c[k]);out[d+1]+=x/(c[j]-c[k])
   poly=out
  integrate=lambda x:mp.fsum(a*x**(d+1)/(d+1) for d,a in enumerate(poly))
  b[j]=integrate(1)
  for i in range(n):A[i,j]=integrate(c[i])
 return A,b,mp.matrix(c)
def continuous(h,terms):
 # q''+2q'+[[1,-1],[-1,1]]q=[t^3,0],q(0)=q'(0)=0.
 K=mp.matrix([[1,-1],[-1,1]]);q=[mp.matrix(2,1) for _ in range(terms+1)]
 for n in range(terms-1):q[n+2]=((mp.matrix([1,0]) if n==3 else mp.matrix(2,1))-2*(n+1)*q[n+1]-K*q[n])/((n+2)*(n+1))
 return mp.matrix([mp.fsum(q[n][i]*h**n for n in range(terms+1)) for i in range(2)])
def discrete(h,n):
 A,b,c=tableau(n);L=mp.matrix([[0,0,1,0],[0,0,0,1],[-1,1,-2,0],[1,-1,0,-2]]);B=mp.eye(4*n);rhs=mp.matrix(4*n,1)
 for i in range(n):
  for j in range(n):
   for k in range(4):
    for l in range(4):B[4*i+k,4*j+l]-=h*A[i,j]*L[k,l]
   rhs[4*i+2]+=h*A[i,j]*(h*c[j])**3
 stages=mp.lu_solve(B,rhs);endpoint=mp.matrix(4,1)
 for j in range(n):endpoint+=h*b[j]*(L*stages[4*j:4*j+4,0]+mp.matrix([0,0,(h*c[j])**3,0]))
 return endpoint,mp.norm(B*stages-rhs)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();mp.mp.dps=100;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');rows=[];coefficients={};passed=True
 for n in (2,3,4):
  A,b,c=tableau(n);cubic=mp.matrix([x**3 for x in c]);rail=(b.T*A*cubic)[0];skin=(b.T*A*A*A*cubic)[0];coefficients[str(n)]={k:mp.nstr(v,80) for k,v in dict(Rail_q_h5=rail,Skin_q_h7=skin,Rail_relative_to_exact=20*rail,Skin_relative_to_exact=840*skin).items()}
  for h in map(mp.mpf,('.01','.001','.0001')):
   exact=continuous(h,80);check=continuous(h,100);numerical,residual=discrete(h,n);agreement=mp.norm(exact-check)/mp.norm(check);passed=passed and agreement<mp.mpf('1e-70') and residual<mp.mpf('1e-90')
   rows.append(dict(stages=n,h_s=float(h),continuous_Rail=mp.nstr(exact[0],80),continuous_Skin=mp.nstr(exact[1],80),collocation_Rail=mp.nstr(numerical[0],80),collocation_Skin=mp.nstr(numerical[1],80),Rail_ratio=float(numerical[0]/exact[0]),Skin_ratio=float(numerical[1]/exact[1]),linear_stage_residual=mp.nstr(residual,80),series80_100_relative=mp.nstr(agreement,80)))
 A,b,c=tableau(2);passed=passed and abs((b.T*A*(c.apply(lambda x:x**3)))[0]-mp.mpf(1)/18)<mp.mpf('1e-90') and abs((b.T*A*A*A*(c.apply(lambda x:x**3)))[0]+mp.mpf(1)/864)<mp.mpf('1e-90')
 A,b,c=tableau(4);passed=passed and abs((b.T*A*A*A*(c.apply(lambda x:x**3)))[0]-mp.mpf(1)/840)<mp.mpf('1e-90')
 with (out/'startup.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 r=dict(status='PASS' if passed else 'FAIL',scope='independent two-unit-mass cubic-load transmission counterexample ONLY;NOT ReGrip full-FEM/SOFA cause certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),precision_decimal_digits=100,model='qdd+2qd+[[1,-1],[-1,1]]q=[t^3,0];zero initial state;direct Rail load only',continuous_reference='independent80/100-term high-precision Taylor recurrence,not a ReGrip trajectory',integration='Gauss2/3/4-stage tableau from integrated Lagrange polynomials;direct high-precision coupled linear solve,NO Newton stopping or floating double floor',leading_exact=dict(Rail_q_h5='1/20',Skin_q_h7='1/840'),leading_Gauss2=dict(Rail_q_h5='1/18',Skin_q_h7='-1/864',Skin_ratio='-35/36'),tableau_coefficients=coefficients,interpretation='Gauss2 reverses the leading indirect Skin response under cubic onset EVEN with exact linear stages;Newton is not needed for this counterexample. Full FEM still needs independent precision/order separation.',physical_changes='none to ReGrip;separate minimal mathematical system',raw_hashes={'startup.csv':sha(out/'startup.csv')});write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
