"""Stock StaticSolver/linear tetra small-load bending;no cable/contact/integration.
Euler-Bernoulli is an approximate section-theory comparison,NOT exact3D reference.
"""
import argparse,json,csv,hashlib,subprocess,sys,copy,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from mechanism_candidates import BASE,mesh,world,width
ROOT=BASE.parent;sys.path.insert(0,str(ROOT/'tools'))
from film_guarded_process import guarded
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(n,tag,**kw):return ET.SubElement(n,tag,{k:str(v) for k,v in kw.items()})
def flat(a):return ' '.join(format(float(x),'.17g') for row in a for x in row)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cfg=json.loads((BASE/'config/design_v1.json').read_text());cfg['palm']['root_angle_deg']=0;meta=json.loads((BASE/'results/default_control332/summary.json').read_text());binary=ROOT/meta['build']/'libReGripProductSequence.so'
 if sha(binary)!=meta['binary_sha256']:raise ValueError('compiled point journal identity mismatch')
 records=[];F=1e-4;E=cfg['simulation']['young_modulus_Pa']/1e6;f=cfg['finger']
 def EI(x):
  As=width(cfg,x)*f['skin_thickness'];Ar=f['rail_width']*f['rail_thickness'];zs=f['skin_thickness']/2;zr=-f['rail_thickness']/2;z=(As*zs+2*Ar*zr)/(As+2*Ar);return E*(width(cfg,x)*f['skin_thickness']**3/12+As*(zs-z)**2+2*(f['rail_width']*f['rail_thickness']**3/12+Ar*(zr-z)**2))
 reference=F*quad(lambda x:(f['length']-x)**2/EI(x),f['clamp_length'],f['length'],epsabs=1e-12)[0]
 for nx in (21,41,81):
  d=out/str(nx);d.mkdir();c=copy.deepcopy(cfg);c['simulation']['nx']=nx;v,t,s=mesh(c);q=np.array([world(c,p) for p in v])*.001;local=np.array(v);tip=np.flatnonzero(local[:,0]==100);root=ET.Element('Node',name='root',dt='1',gravity='0 0 0')
  for plugin in ('AnimationLoop','Constraint.Projective','LinearSolver.Direct','Mass','MechanicalLoad','ODESolver.Backward','SolidMechanics.FEM.Elastic','StateContainer','Topology.Container.Constant'):add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
  add(root,'RequiredPlugin',pluginName=str(binary));add(root,'DefaultAnimationLoop');node=add(root,'Node',name='coupon');add(node,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton=25,absoluteResidualStoppingThreshold=1e-12,relativeInitialStoppingThreshold=1e-12,printLog=1);add(node,'StaticSolver',newtonSolver='@newton');add(node,'SparseLDLSolver',template='CompressedRowSparseMatrixMat3x3d');add(node,'MeshTopology',position=flat(q),tetrahedra=flat(t),triangles=flat(s));add(node,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q));add(node,'UniformMass',totalMass=.001);add(node,'FixedProjectiveConstraint',indices=' '.join(map(str,np.flatnonzero(local[:,0]<=5))));add(node,'TetrahedronFEMForceField',method='small',youngModulus=cfg['simulation']['young_modulus_Pa'],poissonRatio=.3);add(node,'ConstantForceField',indices=' '.join(map(str,tip)),forces=flat([[-F/len(tip),0,0]]*len(tip)));add(node,'NativePointJournal',body='@dofs',filename=str(d/'states.csv'));ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480);errors=sum((d/'process'/x).read_text(errors='replace').count('[ERROR]') for x in ('stdout.log','stderr.log'));record=dict(nx=nx,process=process,sofa_errors=errors,scene_sha256=sha(d/'scene.scn'),status='FAIL')
  if process['exit_code']==0 and not errors:
   rows=list(csv.DictReader((d/'states.csv').open()));actual=[np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows];delta=float(-(actual[-1][tip,0]-q[tip,0]).mean()*1000);record.update(status='STATIC_STATE_ONLY_NOT_PHYSICS_CERTIFIED',tip_deflection_mm=delta,approximate_Euler_ratio=delta/reference,repeat_state_difference_m=float(abs(actual[-1]-actual[0]).max()),state_sha256=sha(d/'states.csv'))
  records.append(record)
 diffs=[dict(nx=[x['nx'],y['nx']],relative=abs(x['tip_deflection_mm']-y['tip_deflection_mm'])/max(abs(x['tip_deflection_mm']),abs(y['tip_deflection_mm']))) for i,x in enumerate(records) for y in records[i+1:] if 'tip_deflection_mm' in x and 'tip_deflection_mm' in y];result=dict(status='BLOCKED_STATIC_SOLVE' if len(diffs)!=3 else 'FAIL_MESH_PAIR_GATE' if any(r['relative']>.01 for r in diffs) else 'PASS_STATIC_PAIR_SCOPE_ONLY',scope='static linear native tetra cantilever,no guides/cables/contact;not curved/dynamic/grasp certification;approximate Euler beam is not an exact3D solution',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),sdk='/home/ubuntu/SOFA/v26.06.00',force_N=F,approximate_Euler_tip_mm=reference,mesh_gate=.01,records=records,pairs=diffs);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'config.json').write_text(json.dumps(cfg,indent=2));(out/'summary.json').write_text(json.dumps(result))
if __name__=='__main__':main()
