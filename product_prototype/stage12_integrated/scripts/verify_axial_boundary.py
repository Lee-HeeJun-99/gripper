"""Independent complex-step checks of actual archived boundary-contrast states."""
import json
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from extensible_rod_reference import section
out=ROOT/'validation/finger/axial_boundary1_verification2';out.mkdir(exist_ok=False)
src=ROOT/'validation/finger/axial_boundary1/summary.json';doc=json.loads(src.read_text());rows=[]
for r in doc['rows']:
 for d in r['refinements']:
  n=d['n'];L=r['L_m'];h=L/n;F=r['force_N'];EA,EI=section(r['body'],(np.arange(n)+.5)*h)
  e=np.array(d['strain']);theta=np.array(d['theta_rad']);N=d['axial_reaction_N']
  z=np.r_[e,theta[1:]]
  def energy(z):
   strain=z[:n];t=np.r_[0,z[n:]];a=(t[:-1]+t[1:])/2
   x=np.sum(h*(1+strain)*np.cos(a));y=np.sum(h*(1+strain)*np.sin(a))
   return np.sum(h*EA*strain**2/2+EI*np.diff(t)**2/(2*h))-F*y-N*(x-L)
  g=[]
  for k in range(len(z)):
   v=z.astype(complex);v[k]+=1e-25j;g.append(energy(v).imag/1e-25)
  a=(theta[:-1]+theta[1:])/2
  xy=np.sum(h*(1+e)[:,None]*np.column_stack((np.cos(a),np.sin(a))),axis=0)
  U=float(np.sum(h*EA*e**2/2+EI*np.diff(theta)**2/(2*h)))
  identity=max(abs(np.array(g[n:])))
  reproduction=abs(identity-d['residual_Nm'])<=1e-15 and max(abs(xy-np.array(d['tip_m'])))<=1e-14 and abs(U-d['stored_energy_J'])<=1e-14
  equilibrium=max(abs(np.array(g)))<=1e-10 and abs(xy[0]-L)<=1e-10
  rows.append(dict(body=r['body'],force_N=F,n=n,reconstruction_pass=bool(reproduction),independent_equilibrium_pass=bool(equilibrium),gradient_max=float(max(abs(np.array(g)))),axial_gap_m=float(xy[0]-L)))
inputs=json.loads((src.parent/'inputs.json').read_text())['inputs'];hashes=all(sha(REPO/x['path'])==x['SHA256'] for x in inputs)
passed=all(r['reconstruction_pass'] for r in rows) and hashes
# Verification PASS certifies reproduction, explicitly not failed equilibrium states.
dump(out/'summary.json',dict(status='REPRODUCTION_PASS' if passed else 'FAIL',scope='Independent saved-state reproduction; equilibrium failures retained',rows=rows,input_hashes_verified=hashes,source=ref(src),producer=ref(Path(__file__)),equilibrium_pass_count=sum(r['independent_equilibrium_pass'] for r in rows),whole_system_release=False))
print('reproduction',passed,'equilibrium',sum(r['independent_equilibrium_pass'] for r in rows),'/',len(rows))
raise SystemExit(0 if passed else 2)
