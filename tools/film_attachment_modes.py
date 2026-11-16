"""Independent frozen-energy tangent diagnostic, not a new dynamics solver."""
import argparse,csv,json,struct,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);inputs={};states=[]
 for name in ('rail_low3200_99','rail_low6400_100'):
  file=ROOT/'results'/('autonomous_film_20261116_'+name)/'1/journal.csv';inputs[str(file.relative_to(ROOT))]=sha(file);r=list(csv.DictReader(file.open()));selected=min(r,key=lambda s:abs(float(s['time'])-1.12875));states.append(np.fromstring(selected['x'],sep=' ').reshape(-1,3))
 rest=[];w=(439.3397917746089/3-120)/(20)
 for ny,width,y,z in ((5,24,0,0),(3,w,0,-.075),(3,w,24-w,-.075)):
  rest.extend([[100*i/20,y+width*j/(ny-1),z] for i in range(21) for j in range(ny)])
 with (out/'state.bin').open('xb') as f:f.write(struct.pack('Q',231));f.write(np.asarray(states[1]-rest,dtype=np.float64).tobytes());f.write(np.asarray(states[0]-states[1],dtype=np.float64).tobytes())
 src=ROOT/'diagnostics/film_rail_tendon/AttachmentModes.cpp';shutil.copy2(src,out/'AttachmentModes.cpp');stages={};stages['build']=logged(['g++','-std=c++17','-O2','-ffp-contract=off','-I/usr/include/eigen3',src,'-o',out/'modes'],out/'build',180)
 if stages['build']['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stages=stages));return
 stages['math']=logged([out/'modes',out/'state.bin'],out/'math',60)
 if stages['math']['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stages=stages));return
 records=list(csv.DictReader((out/'math/stdout.log').open()));positive=[{k:float(v) for k,v in r.items()} for r in records if float(r['eigenvalue'])>0];positive.sort(key=lambda r:abs(r['error_quadratic_energy']),reverse=True)
 write_json(out/'summary.json',dict(status='PASS',scope='independent instantaneous stored-energy tangent only;no tendon geometric stiffness or modal dynamics certificate',inputs=inputs,stages=stages,time=1.12875,negative_eigenvalues=sum(float(r['eigenvalue'])<0 for r in records),maximum_frequency=max(r['omega_rad_s'] for r in positive),largest_error_modes=positive[:12],binary_sha256=sha(out/'modes'),source_sha256=sha(src)));print(json.dumps(dict(maximum_frequency=max(r['omega_rad_s'] for r in positive),largest_error_modes=positive[:4])))
if __name__=='__main__':main()
