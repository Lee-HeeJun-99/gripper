"""Saved actual SOFA matrix versus same-stage AD M/C/K,free scalar DOFs only."""
import argparse,csv,json,math
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('tag')
 out=ROOT/'results'/('autonomous_film_matrix_assess_'+a.tag);out.mkdir(exist_ok=False);raw=ROOT/'results/autonomous_film_20261116_matrix_probe/1/journal.csv.matrix.csv'
 # Root has five Vec3 nodes =15SCALAR DOFs,not five scalar DOFs. Raw includes
 # some constrained rows;remove only the explicitly known boundary rows.
 rows=[v for v in csv.DictReader(raw.open())if int(v['row'])>=15 and int(v['col'])>=15]
 error=math.sqrt(sum((float(v['actual'])-float(v['expected']))**2 for v in rows)/sum(float(v['expected'])**2 for v in rows))
 result=dict(source='Actual SOFA first assembled free block vs analytical mass/damping plus same-stage AD Hessian;not full nonlinear RHS validation',raw_sha256=sha(raw),free_scalar_offset=15,relative_error=error,status='PASS'if error<1e-12 else'FAIL',nonlinear_rhs='NOT RUN',all_later_steps='NOT RUN')
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
