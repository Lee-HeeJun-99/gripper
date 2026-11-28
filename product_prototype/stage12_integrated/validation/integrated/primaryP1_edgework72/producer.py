"""Actual finite socket material-edge analytic derivative vs complex-step virtual work.
Dropping axial trim or helical end motion are deliberate rejected controls.
"""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_keeper_coupled71 import faces,rot
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(sp.read_text());cp=REPO/s['candidate']['path'];assert sha(cp)==s['candidate']['SHA256'];cad=json.loads(cp.read_text());a=np.load(REPO/s['field']['path']);keys=json.loads((REPO/s['contact_keys']['path']).read_text());pos=a['points_mm']+a['displacement_mm'];ang=np.array(s['bolt_reference_spin_rad'])+a['bolt_spin_increment_rad'];settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];pitch=.5/(2*np.pi);walls=[];centers=[]
for q in settings:
 c=np.array([q['x'],q['y'],0.]);centers.append(c);ww=[]
 for f in faces(read(REPO/cad['part_references'][q['bolt']]['path'])):
  ad=BRepAdaptor_Surface(f)
  if ad.GetType()!=GeomAbs_Plane:continue
  pl=ad.Plane();o=pl.Location();ax=pl.Axis().Direction();o=np.array([o.X(),o.Y(),o.Z()]);n=np.array([ax.X(),ax.Y(),ax.Z()]);bb=bounds(f)
  if abs(n[2])<1e-7 and np.linalg.norm((np.array(bb[:3])+bb[3:])[:2]/2-c[:2])<2:
   if n@(c-o)<0:n=-n
   ww.append((o,n))
 assert len(ww)==6;walls.append(ww)
rows=[]
for ri,k in enumerate(keys):
 if k[2]!='e':continue
 bi,wi,_,aa,bb,end=k;c=centers[bi];o0,n0=walls[bi][wi];y=np.r_[pos[aa],pos[bb],ang[bi]]
 def gap(y):
  theta=y[6];co,si=np.cos(theta),np.sin(theta);R=np.array([[co,-si,0],[si,co,0],[0,0,1]]);n=R@n0;o=R@(o0-c)+c+np.array([0,0,pitch*theta]);d=y[3:6]-y[:3];z=pitch*theta+(-1.3 if end==0 else 0);tau=(z-y[2])/d[2];pt=y[:3]+tau*d;return n@(pt-o)
 d=y[3:6]-y[:3];tau=(pitch*y[6]+(-1.3 if end==0 else 0)-y[2])/d[2];n=rot(y[6])@n0;pt=y[:3]+tau*d;g=n.copy();g[2]-=n@d/d[2];spin=-n@np.cross([0,0,1],pt-c)+(n@d/d[2])*pitch;analytic=np.r_[(1-tau)*g,tau*g,spin];cs=[]
 for j in range(7):
  yy=y.astype(complex);yy[j]+=1e-20j;cs.append(float(gap(yy).imag/1e-20))
 cs=np.array(cs);bad=analytic.copy();bad[[2,5]]=0;badspin=analytic.copy();badspin[-1]-=(n@d/d[2])*pitch
 rows.append(dict(row=ri,edge_nodes=[aa,bb],end=end,tau=float(tau),analytic=analytic.tolist(),complex_step=cs.tolist(),maximum_error=float(abs(cs-analytic).max()),omitted_material_trim_error=float(abs(cs-bad).max()),omitted_helical_end_motion_error=float(abs(cs-badspin).max())))
checks=dict(all_exact_edge_derivatives=max(q['maximum_error'] for q in rows)<1e-10,missing_material_trim_rejected=max(q['omitted_material_trim_error'] for q in rows)>1e-3,missing_helical_trim_rejected=max(q['omitted_helical_end_motion_error'] for q in rows)>1e-3)
dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_EDGE_VIRTUAL_WORK_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_FINITE_EDGE_DERIVATIVE_FAIL',producer=ref(out/'producer.py'),candidate=ref(cp),source=ref(sp),checks=checks,rows=rows,whole_system_release=False,newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0));print(json.dumps(dict(checks=checks,maximum_derivative_error=max(q['maximum_error'] for q in rows),omitted_material_trim_error=max(q['omitted_material_trim_error'] for q in rows),omitted_helical_trim_error=max(q['omitted_helical_end_motion_error'] for q in rows))))
sys.exit(0 if all(checks.values()) else 2)
