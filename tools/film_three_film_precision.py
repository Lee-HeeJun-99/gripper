"""Exact-double-input triangle distance,independent Decimal80/120 observer.

Never modifies physical rows or old failed trials.
"""
import argparse,csv,json,shutil,subprocess
from decimal import Decimal,localcontext
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def distance(points,radius,precision):
 with localcontext() as context:
  context.prec=precision;x=[[Decimal.from_float(float(v)) for v in p] for p in points];r=Decimal.from_float(float(radius));sub=lambda a,b:[i-j for i,j in zip(a,b)];dot=lambda a,b:sum(i*j for i,j in zip(a,b));cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];candidates=[]
  for i,j in ((0,1),(0,2),(1,2)):
   edge=sub(x[j],x[i]);den=dot(edge,edge)
   if den<=0:raise ValueError('degenerate exact-input edge')
   t=max(Decimal(0),min(Decimal(1),-dot(x[i],edge)/den));p=[a+t*b for a,b in zip(x[i],edge)];candidates.append(dot(p,p))
  ab=sub(x[1],x[0]);ac=sub(x[2],x[0]);normal=cross(ab,ac);nn=dot(normal,normal)
  if nn<=0:raise ValueError('degenerate exact-input triangle')
  projected=[v*dot(normal,x[0])/nn for v in normal];ap=sub(projected,x[0]);aa=dot(ab,ab);bb=dot(ab,ac);cc=dot(ac,ac);den=aa*cc-bb*bb;u=(cc*dot(ab,ap)-bb*dot(ac,ap))/den;v=(aa*dot(ac,ap)-bb*dot(ab,ap))/den
  if u>=0 and v>=0 and u+v<=1:candidates.append(dot(projected,projected))
  return min(candidates).sqrt()-r
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);sm=json.loads((src/'summary.json').read_text());rejected=src/'state.csv.rejected.csv'
 if sm['status']!='FAIL' or not rejected.is_file():raise ValueError('preserved actual rejected independent trial required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/RejectedGeometry.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/RejectedGeometry.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,rejected,out/'geometry.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='independent precision of recorded exact-double geometry ONLY;NOT physical contact or SOFA certification',case=a.case,compile=compile,run=run,rejected_sha256=sha(rejected),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if run and run['exit_code']==0:
  metrics=[]
  for row in csv.DictReader((out/'geometry.csv').open()):
   coordinates=row['relative_points'].split();points=[coordinates[3*i:3*i+3] for i in range(3)];d80=distance(points,row['radius'],80);d120=distance(points,row['radius'],120);metrics.append(dict(triangle=int(row['triangle']),double_gap=float(row['double_gap']),double_feature=int(row['double_feature']),gap80=str(d80),gap120=str(d120),precision_difference=str(abs(d80-d120))))
  result.update(status='PASS' if all(Decimal(m['precision_difference'])<Decimal('1e-60') for m in metrics) else 'FAIL',metrics=metrics,closest_triangle=min(metrics,key=lambda m:Decimal(m['gap120']))['triangle'],signed_gap_difference=str(Decimal(metrics[0]['gap120'])-Decimal(metrics[1]['gap120'])),binary_sha256=sha(binary))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','metrics','closest_triangle','signed_gap_difference')},indent=2))
if __name__=='__main__':main()
