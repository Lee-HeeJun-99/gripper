"""Implemented50mm palm layout + shared impulse reference,NOT actual grasp."""
import argparse,csv,json,shutil,subprocess,os
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for directory in ('film_three_finger','film_coupled_contact','film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
  target=archive/'models'/directory;target.mkdir(parents=True)
  for f in (ROOT/'models'/directory).glob('*.h'):shutil.copy2(f,target/f.name)
 test=archive/'tests/test_film_three_finger.cpp';test.parent.mkdir();shutil.copy2(ROOT/'tests/test_film_three_finger.cpp',test);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',test,'-o',binary],out/'compile',120);run=guarded([binary,out/'geometry.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent3film shared frame/mass/point impulse and IMPLEMENTED REST geometry;NOT actual SOFA/tendon/3finger grasp',compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},assumptions=dict(palm_radius_mm=50,finger_length_mm=100,sphere_radius_mm=30,buffer_radius_mm=30.01,sphere_mass_Ns2_per_mm=.0001,contact_material_x_mm=75,mount='fixed inward inclination chosen for reference object;not automatic adaptation',tendon_motion='NOT RUN;prescribed initial point approach',friction='none',self_collision='rest angular wedge only,NOT dynamic',material='unmeasured research model'))
 if binary.exists():result['binary_sha256']=sha(binary)
 if result['status']=='PASS':
  rows=list(csv.DictReader((out/'geometry.csv').open()));vertices=np.array([[float(s[k]) for k in ('x','y','z')] for s in rows]);os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
  fig,axes=plt.subplots(1,3,figsize=(12,4))
  for ax,(x,y) in zip(axes,((0,1),(0,2),(1,2))):
   for f in range(3):p=vertices[np.array([int(s['finger'])==f for s in rows])];ax.scatter(p[:,x],p[:,y],s=3,label='finger'+str(f));ax.set_aspect('equal');ax.set_xlabel('xyz'[x]+' [mm]');ax.set_ylabel('xyz'[y]+' [mm]');ax.grid()
  dimfile=out/'geometry.csv.layout.csv'
  if dimfile.exists():
   dims={k:float(v) for k,v in next(csv.DictReader(dimfile.open())).items()};result['layout_parameters']=dims
   for ax,coordinates in zip(axes,((0,1),(0,2),(1,2))):ax.add_patch(plt.Circle((dims[['body_x','body_y','body_z'][coordinates[0]]],dims[['body_x','body_y','body_z'][coordinates[1]]]),dims['body_radius'],color='#999',alpha=.2));ax.set_aspect('equal');ax.autoscale()
  axes[0].legend(fontsize=7);fig.suptitle('IMPLEMENTED REST reference geometry;NOT actual SOFA/deformation/grasp');fig.tight_layout();fig.savefig(out/'implemented_layout.png',dpi=170);plt.close(fig)
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],scope=result['scope'])))
if __name__=='__main__':main()
