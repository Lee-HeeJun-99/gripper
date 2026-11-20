"""Fixed proposed wheel vs OLD accepted first-Eyelet motion;not new dynamics."""
import argparse,csv,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,sha
sys.path.insert(0,str(BASE/'sofa'))
from analyse import rotation

def tangent(point,radius,reference):
 p=np.asarray(point);d2=p@p
 if radius<=0 or d2<=radius**2:raise ValueError('no external circle tangent')
 base=radius**2*p/d2;offset=radius*np.sqrt(d2-radius**2)*np.array([-p[1],p[0]])/d2
 candidates=[base+offset,base-offset]
 return min(candidates,key=lambda x:np.linalg.norm(x-reference))

def side_envelope(point,touch):
 d=touch-point[:2];A=d@d;B=2*(point[:2]@d);C=point[:2]@point[:2]-9.
 roots=np.roots([A,B,C]);valid=[float(t.real) for t in roots if t.imag==0 and 0<=t.real<=1]
 if not valid:raise ValueError('first guide must lie outside flange OD6')
 # At first entrance into radialR3 the oblique line has its maximum axial
 # offset over the approach to the tangentpoint (axialzero at endpoint).
 return abs(point[2])*(1-min(valid))+.25

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 old=BASE/'results/b3_alarm_window485';src=BASE/'meshes/b3_root_fork_v31/assembly_recipe.json';routefile=BASE/'results/product_root_fork780/summary.json';files=[Path(__file__),src,routefile,old/'scene.scn',BASE/'sofa/analyse.py',*[old/f'guide_frames{f}.csv' for f in range(3)]];hashes={str(x.relative_to(BASE)):sha(x) for x in files}
 parts=json.loads(src.read_text())['parts'];routes=json.loads(routefile.read_text())['records'];tree=ET.parse(old/'scene.scn');records=[]
 # Independent right-angle tangent reference;not a measured state.
 t=tangent(np.array([4.,0]),2.,np.array([1.,2.]));assert abs(t@t-4)<1e-13 and abs(t@(t-[4,0]))<1e-13
 for f in range(3):
  rows=list(csv.DictReader((old/f'guide_frames{f}.csv').open()));rest=np.fromstring(tree.find(f"./Node[@name='guides{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
  for c in range(2):
   wheel=next(p for p in parts if p['name']==f'f{f}_c{c}_root_redirect');M=np.array(wheel['shape']['matrix']);route=np.array(next(r for r in routes if r['part']==wheel['name'])['route_mm']);reference=(M[:3,:3].T@(route[1]-M[:3,3]))[:2];centre=route[0];i=6*c;values=[]
   for row in rows:
    q=np.fromstring(row['rigid_q'],sep=' ').reshape(-1,7)[i];R=rotation(q[3:])@rotation(rest[i,3:]).T;current=R@(centre-rest[i,:3]*1000)+q[:3]*1000;local=M[:3,:3].T@(current-M[:3,3]);touch=tangent(local[:2],2.,reference);bound=side_envelope(local,touch)
    values.append(dict(time_s=float(row['time_s']),axial_bound_mm=float(bound),first_guide_axial_mm=float(local[2])))
   worst=max(values,key=lambda x:x['axial_bound_mm']);records.append(dict(wheel=wheel['name'],saved_frames=len(rows),worst=worst,nominal_flange_inner_half_width_mm=.4,saved_frames_not_certified_by_side_bound=sum(r['axial_bound_mm']>=.4 for r in values)))
 if hashes!={str(x.relative_to(BASE)):sha(x) for x in files}:raise ValueError('source identity changed')
 d=dict(status='OLD_MOTION_NOMINAL_ROOT_ALIGNMENT_SCREEN_NOT_NATIVE_ADOPTION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,scope='Actual OLD485 firstEyelet rigid motion with CAD centre offset and proposed FIXED root wheel;piecewise straight tangent approach plusideal circular groove assumption. Conservative axial wire radius.25 at entryradialR3. Bound below.4 suffices only nominal side opening in this approach;failure of bound is NOT proof of collision. No new forces/friction/cloth/FEM/dynamics/continuousCCD or fullassembly qualification. Incoming line/groove tangent direction can kink axially;no smooth3Dwire elasticity assumed.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
