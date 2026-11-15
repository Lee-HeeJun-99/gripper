import csv
import numpy as np
from curve_checkpoint_common import CPROOT,OUT,chunk,merge_states,merge_csv,write_json
from trial_validation import read_states
def main():
    out=CPROOT/'proof8s_v3';out.mkdir(exist_ok=False);source=OUT/'grasp/n21';parts=[out/'part1',out/'part2'];checkpoint=None;records=[]
    for part in parts:checkpoint,record=chunk(part,source,8000,input_checkpoint=checkpoint);records.append(record)
    merge_states(parts,out/'state.txt');original=[r for r in read_states(source/'state.txt')if r['time']<=8+1e-8];actual=read_states(out/'state.txt')
    if len(original)!=len(actual):raise ValueError('checkpoint merged count')
    errors={k:float(np.max(np.abs(np.array([r[k]for r in original])-np.array([r[k]for r in actual]))))for k in('X','V','R')};csv_errors={}
    for name in('contact.csv','layer0.csv','layer1.csv','layer2.csv'):
        merge_csv(parts,name,out/name)
        with(source/name).open()as f:a=[r for r in csv.DictReader(f)if float(r['time'])<=8+1e-8]
        with(out/name).open()as f:b=list(csv.DictReader(f))
        if len(a)!=len(b):raise ValueError('checkpoint CSV count '+name)
        csv_errors[name]=max(abs(float(u[k])-float(v[k]))for u,v in zip(a,b)for k in u)
    passed=all(v<1e-12 for v in errors.values())and all(v<1e-12 for v in csv_errors.values());result=dict(status='PASS'if passed else'FAIL',state_errors=errors,cumulative_history_csv_errors=csv_errors,actual_records=len(actual),chunks=records,scope='two actual4s processes versus first8s of actual uninterrupted native21node run;full q/v/time/contact/layer/cable state;initial unrestored startup frame excluded ONLY from restored chunk;not arbitrary-session automatic restart')
    write_json(out/'summary.json',result);print(passed,errors,csv_errors)
if __name__=='__main__':main()
