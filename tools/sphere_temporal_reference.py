"""Exact changing-normal GREAT-CIRCLE sliding reference, NOT general vector law.

For a straight sphere chord p=b_vector+u*vhat, r=sqrt(b²+u²),
the tangential arc increment is b/r du. With c=a(R-r), e=c/k in
the transported tangent direction, dp=(b+a*u/k)/r du. Thus
D=a*[R*b*asinh(u/b)+R*a*r/k-b*u-a*u²/(2*k)] at the limits.
The positive-slip inequality is CHECKED, not assumed for arbitrary paths.
This resolves work quadrature for this special case; it does not supply the
endpoint tangent for off-plane perturbations/general history or new SOFA law.
"""
import argparse,json,subprocess
import mpmath as mp
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('tag')
 out=ROOT/'results'/('autonomous_temporal_exact_'+a.tag);out.mkdir(exist_ok=False);mp.mp.dps=70
 R=mp.mpf('1.02');k=mp.mpf('.001');friction=mp.mpf('.0003');start=[mp.mpf(0),mp.mpf('1.021'),mp.mpf(0)];velocity=list(map(mp.mpf,['.2','-.2','.1']));speed=mp.sqrt(sum(v*v for v in velocity));direction=[v/speed for v in velocity];u0=sum(x*v for x,v in zip(start,direction));b=mp.sqrt(sum(x*x for x in start)-u0*u0);birth=-mp.sqrt(R*R-b*b)
 if b<=0 or k*b+friction*birth<=0:raise ValueError('not the positive great-circle sliding branch')
 def exact(t):
  u=u0+speed*mp.mpf(t)
  if u<=birth:return mp.mpf(0),mp.mpf(0),mp.mpf(0)
  r=mp.sqrt(b*b+u*u)
  if r>=R:raise ValueError('death requires separate inventory')
  primitive=lambda z:friction*(R*b*mp.asinh(z/b)+R*friction*mp.sqrt(b*b+z*z)/k-b*z-friction*z*z/(2*k))
  D=primitive(u)-primitive(birth);W=friction*b*(R*(mp.asinh(u/b)-mp.asinh(birth/b))-(u-birth));U=(friction*(R-r))**2/(2*k)
  # Independent high-precision integration of c * plastic arc derivative.
  integral=mp.quad(lambda z:friction*(R-mp.sqrt(b*b+z*z))*(b+friction*z/k)/mp.sqrt(b*b+z*z),[birth,u])
  if abs(integral-D)>mp.mpf('1e-60')or D<0 or abs(W-U-D)>mp.mpf('1e-60'):raise ValueError('exact changing-normal work identity')
  return D,W,U
 records={}
 for steps in (20,40,80):records[steps]=[exact(mp.mpf('.02')*i/steps)[0]for i in range(1,steps+1)]
 comparisons=[]
 for c,f in ((20,40),(20,80),(40,80)):
  previous0=previous1=mp.mpf(0);errors=[]
  for i,D in enumerate(records[c]):
   other=records[f][(i+1)*(f//c)-1];d0=D-previous0;d1=other-previous1
   if d1:errors.append(abs(d0-d1)/d1)
   elif d0:raise ValueError('undefined phase error')
   previous0=D;previous1=other
  comparisons.append(dict(steps=[c,f],max_phase_relative=float(max(errors,default=0))))
 D,W,U=exact(mp.mpf('.02'));result=dict(source='Independent analytical changing-normal sphere great-circle,verified70-digit quadrature;NOT SOFA/general vector tangent',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(ROOT/'tools/sphere_temporal_reference.py'),parameters=dict(R=str(R),k=str(k),mu_kn=str(friction),impact=str(b),birth_time=str((birth-u0)/speed)),D=str(D),W=str(W),U=str(U),comparisons=comparisons,status='PASS'if all(v['max_phase_relative']<=.001 for v in comparisons)else'FAIL',general_vector_tangent='NOT IMPLEMENTED',old_sofa_time='FAIL;not replaced by analytical reference')
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
