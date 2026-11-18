"""Independent nonlinear energy-defect scaling;NOT a film/energy Gate waiver."""
import argparse,decimal,hashlib,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
D=decimal.Decimal
def integrate(count):
 with decimal.localcontext() as ctx:
  ctx.prec=80;q=D('.5');v=D('.7');h=D('.2')/count;k=D(2);m=D(1);initial=m*v*v/2+k*q**4/4;defect=D(0);identity=D(0)
  for i in range(count):
   x=q+h*v/2
   for j in range(30):x-=(x+h*h*k*x**3/(4*m)-q-h*v/2)/(1+3*h*h*k*x*x/(4*m))
   q1=2*x-q;v1=v-h*k*x**3/m;increment=k*x*(q1-q)**3/4;measured=m*(v1*v1-v*v)/2+k*(q1**4-q**4)/4;identity=max(identity,abs(measured-increment));defect+=increment;q,v=q1,v1
  energy=m*v*v/2+k*q**4/4
  return dict(steps=count,q=q,v=v,energy=energy,signed_defect=energy-initial,analytic_cubic_increment_sum=defect,maximum_increment_identity_error=identity,cumulative_identity_error=abs(energy-initial-defect))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();data=[integrate(n) for n in (10,20,40)];pairs=[]
 for i,j in ((0,1),(0,2),(1,2)):
  relative=abs((data[i]['signed_defect']-data[j]['signed_defect'])/data[j]['signed_defect']);pairs.append(dict(steps=[data[i]['steps'],data[j]['steps']],defect_relative_percent=str(100*relative),defect_time_gate='PASS' if relative<=D('.001') else 'FAIL'))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='PASS' if max(x['cumulative_identity_error'] for x in data)<D('1e-70') else 'FAIL',scope='80-digit independent quartic oscillator midpoint identity/scaling ONLY;NOT actual film/SOFA/full energy or gate modification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),runner_sha256=sha(out/'runner.py'),physical_input='m=1,k=2,V=k*q^4/4,q0=.5,v0=.7,duration=.2;no external force/damping/contact',formula='DeltaE=V(q1)-V(q0)-(q1-q0)*Vprime(qmid)=k*qmid*(q1-q0)^3/4;global signed defect is second order',results=[{k:(str(v) if isinstance(v,D) else v) for k,v in x.items()} for x in data],pairs=pairs,interpretation='relative comparison of a truncation-error residual tending to zero can remain ~300%/1500% while physical state converges;existing ReGrip residual FAILs remain FAIL,not waived/reclassified as heat',film_cause='NOT established by this independent example;actual constitutive/momentum decomposition still required',full_energy='BLOCKED');write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
