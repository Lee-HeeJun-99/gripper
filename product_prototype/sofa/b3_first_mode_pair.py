import argparse,json,shutil
from pathlib import Path
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);b=json.loads((BASE/'results/b3_first_mode_base1184/trace.json').read_text());h=json.loads((BASE/'results/b3_first_mode_half1185/trace.json').read_text());pairs=[]
 for i,r in enumerate(b):
  z=h[2*i+1];assert abs(r['time_s']-z['time_s'])<1e-12;v=r['actual_modal_displacement'];w=z['actual_modal_displacement'];pairs.append(dict(time_s=r['time_s'],absolute_modal_error=abs(v-w),relative=abs(v-w)/max(abs(v),abs(w))))
 failures={}
 for case in ('b3_first_mode_base1182','b3_first_mode_half1183'):
  src=BASE/'results'/case;dst=out/'failed_originals'/case;shutil.copytree(src,dst);failures[case]=dict(status='INVALID_EXECUTION_PLUGIN_ORDER',files={str(f.relative_to(BASE)):sha(f) for f in src.rglob('*') if f.is_file()},note='1183 postprocessor encountered truncated invalid partial row;no original files modified')
 d=dict(status='FAIL_ISOLATED_MODE_TIME_PAIR',maximum_relative=max(r['relative'] for r in pairs),worst=max(pairs,key=lambda x:x['relative']),relative_gate=.001,failures=failures,physical_validation='NOT QUALIFIED',conclusion='Large time error exists in one-mode Native linear FEM without Guide/Cable/contact;matches known discrete recurrence. Not proof of all nonlinear B3 error or cure.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in (BASE/'results/b3_first_mode_base1184/trace.json',BASE/'results/b3_first_mode_half1185/trace.json')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'trace.json').write_text(json.dumps(pairs,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='failures'}))
if __name__=='__main__':main()
