"""Combine compatible static mesh results for comparison, never grant release.
Physical/numerical constraint kernels must match despite checkpoint-I/O changes.
"""
import argparse,ast,hashlib,json,shutil
from pathlib import Path
from baseline_registry import ROOT,REPO,ref,dump,sha
FUNCTIONS={'geometry','point','distances','energy','gradient','constraints'}
PARAMETERS={'h','theta','R','M','shift','fc','fr','EI','scale'}
def kernel(source):
    tree=ast.parse(source);solve=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='solve');nodes=[]
    for n in solve.body:
        if isinstance(n,ast.FunctionDef) and n.name in FUNCTIONS:nodes.append(n)
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in PARAMETERS for t in n.targets):nodes.append(n)
    if {n.name for n in nodes if isinstance(n,ast.FunctionDef)}!=FUNCTIONS:raise ValueError('Missing explicit model/constraint kernel')
    return hashlib.sha256('\n'.join(ast.dump(n,include_attributes=False) for n in nodes).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',nargs='+',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    data=[];records=[];kernels=[]
    for tag in a.inputs:
        path=ROOT/'validation/finger'/tag/'summary.json';d=json.loads(path.read_text());source=path.parent/'producer.py';assert sha(source)==d['producer']['SHA256']
        data.append(d);kernels.append(kernel(source.read_text()));records.append(dict(result=ref(path),source=ref(source),kernel_SHA256=kernels[-1]));
    if len(set(kernels))!=1 or any(d['candidate']!=data[0]['candidate'] or d['PET_free_length_m']!=data[0]['PET_free_length_m'] for d in data):raise ValueError('Different physical/constraint model cannot be compared as mesh refinement')
    rows=[r for d in data for r in d['rows']];keys=[(r['n'],r['fixture_angle_deg']) for r in rows]
    if len(set(keys))!=len(keys):raise ValueError('Duplicate mesh/pose evidence')
    source=(ROOT/'validation/finger'/a.inputs[0]/'producer.py').read_text()
    if kernel(source)==kernel(source.replace('.0003**3','.00031**3')):raise ValueError('Negative material/thickness change not detected')
    result=dict(status='COMPATIBLE_RESULTS_FOR_COMPARISON_ONLY',rows=rows,PET_free_length_m=data[0]['PET_free_length_m'],candidate=data[0]['candidate'],inputs=records,
        scope='STATIC MESH COMPARISON; NO DYNAMIC CHUNK EQUIVALENCE OR PRODUCT RELEASE',
        model_change_negative_control_rejected=True,producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],meshes=[r['n'] for r in rows],kernel_SHA256=kernels[0],material_change_rejected=True)))
if __name__=='__main__':main()
