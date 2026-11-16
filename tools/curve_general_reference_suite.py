"""Fresh bounded mathematical regression of general-history prerequisites."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
TESTS=('general_history_owner','general_history_frames','general_material_rule','general_rule_geometry','general_capacity_work','general_temporal_yield')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('simple unique tag')
 out=ROOT/'results'/('vector_history_general_suite_'+a.tag);out.mkdir(exist_ok=False)
 sources=list((ROOT/'models').rglob('*.h'))+[ROOT/'tests'/('test_'+n+'.cpp')for n in TESTS]+[ROOT/'tools/curve_general_reference_suite.py']
 before={str(p.relative_to(ROOT)):sha(p)for p in sources}
 write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=before,scope='independent mathematics,NOT SOFA/grasp'))
 for p in sources:
  d=out/'sources'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
 stages={}
 for n in TESTS:
  binary=out/(n+'.bin');stages[n+'_build']=logged(['g++','-std=c++17','-O2','-ffp-contract=off',ROOT/'tests'/('test_'+n+'.cpp'),'-o',binary],out/(n+'_build'),120)
  if stages[n+'_build']['exit_code']:continue
  stages[n]=logged([binary],out/n,180);stages[n]['binary_sha256']=sha(binary)
 if before!={str(p.relative_to(ROOT)):sha(p)for p in sources}:raise ValueError('source changed during reference suite')
 write_json(out/'summary.json',dict(status='PASS'if len(stages)==2*len(TESTS)and all(s['exit_code']==0 for s in stages.values())else'FAIL',stages=stages,sofa='NOT RUN'))
 print(json.dumps(dict(out=str(out))))
if __name__=='__main__':main()
