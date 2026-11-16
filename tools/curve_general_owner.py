"""Bounded NEW exact-function moving-history adapter campaign; not grasp approval."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--gauss',action='store_true');p.add_argument('--adaptive',action='store_true');a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('simple unique tag')
 out=ROOT/'results'/('vector_history_owner_'+a.tag);out.mkdir(exist_ok=False)
 build=ROOT/'build'/('vector_history_owner_'+a.tag)
 if build.exists():raise ValueError('new build required')
 sources=[q for folder in ('models/general_vector_history','models/curved_contact','models/material_point_contact','models/contact_birth','models/contact_history','models/yield_front_history','models/conservative_beam','models/contact_kinematics','models/integrated','models/closure','models/stabilization','models/finite_rotation') for q in (ROOT/folder).rglob('*') if q.is_file()]
 sources += [ROOT/f for f in ('tests/test_general_curved.cpp','tests/test_general_history_owner.cpp','tests/test_curved_contact.cpp','tools/curve_general_owner.py')]
 before={str(q.relative_to(ROOT)):sha(q)for q in sources}
 write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=before,scope='exact finite-prefix general material history;fixed material quadrature;NOT adaptive general-history qualification'))
 for q in sources:
  dst=out/'sources'/q.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dst)
 stages={}
 commands=[('configure',['cmake','-S',ROOT/'models/general_vector_history','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DGENERAL_HISTORY_GAUSS='+('ON'if a.gauss else'OFF'),'-DGENERAL_HISTORY_ADAPTIVE='+('ON'if a.adaptive else'OFF'),'-DCMAKE_PREFIX_PATH='+str(ROOT/'.runtime/closure_sdk')]),('build',['cmake','--build',build,'--target','ReGripGeneralVectorContact','test_general_curved','test_general_history_owner','-j2']),('owner',[build/'test_general_history_owner']),('api',[build/'test_general_curved']),('ldd',['ldd',build/'libReGripGeneralVectorContact.so'])]
 for name,cmd in commands:
  stages[name]=logged(cmd,out/name,180)
  if stages[name]['exit_code']:break
 status='PASS'if len(stages)==len(commands)and all(s['exit_code']==0 for s in stages.values())else'FAIL'
 if status=='PASS':
  if before!={str(q.relative_to(ROOT)):sha(q)for q in sources}:raise ValueError('source changed during campaign')
  write_json(out/'compiled.json',dict(binary=sha(build/'libReGripGeneralVectorContact.so'),generated=sha(build/'GeneralGenerated.inc'),sources=before))
 write_json(out/'summary.json',dict(status=status,stages=stages,full_gripper='NOT RUN',adaptive_history='NOT RUN'))
 print(json.dumps(dict(out=str(out),status=status)))
if __name__=='__main__':main()
