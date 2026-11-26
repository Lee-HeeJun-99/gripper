"""Execute the ACTUAL archived working-set branch on a known contact QP.

The test extracts code, not a copied implementation. Synthetic control only.
"""
import argparse,ast,copy,json
import numpy as np
from scipy.optimize import minimize
from baseline_registry import ROOT,ref,dump

def branch(source,broken=False):
    solve=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='solve')
    outer=next(n for n in solve.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='exchange')
    code=copy.deepcopy(next(n for n in outer.body if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='working_set').body)
    if broken:
        for node in ast.walk(ast.Module(body=code,type_ignores=[])):
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='missing' for t in node.targets):node.value=ast.Call(func=ast.Name(id='set',ctx=ast.Load()),args=[],keywords=[])
    args=ast.arguments(posonlyargs=[],args=[ast.arg(arg=n) for n in ('energy','gradient','constraints','constraint_derivatives','q','save_guess')],kwonlyargs=[],kw_defaults=[],defaults=[])
    body=ast.parse('working_history=[]').body+code+ast.parse('return q,working_history').body
    module=ast.fix_missing_locations(ast.Module(body=[ast.FunctionDef(name='run',args=args,body=body,decorator_list=[])],type_ignores=[]))
    env=dict(np=np,minimize=minimize);exec(compile(module,'<actual archived static branch>','exec'),env);return env['run']

def main():
    p=argparse.ArgumentParser();p.add_argument('--producer',required=True);p.add_argument('--tag',required=True);a=p.parse_args();source=ROOT/a.producer
    out=ROOT/'validation/contact'/a.tag;out.mkdir(parents=True,exist_ok=False)
    target=np.array([.5,-2.]);energy=lambda q:float(np.sum((q-target)**2));gradient=lambda q:2*(q-target)
    constraints=lambda q:np.array([q[0],q[1]+1]);J=lambda q:np.eye(2)
    actual,history=branch(source.read_text())(energy,gradient,constraints,J,np.zeros(2),lambda q:None)
    broken,_=branch(source.read_text(),True)(energy,gradient,constraints,J,np.zeros(2),lambda q:None)
    expected=np.array([.5,-1.]);error=float(np.linalg.norm(actual-expected));negative_rejected=bool(constraints(broken).min() < -1e-5)
    ok=error<1e-6 and any(r['new_violated_rows'] for r in history) and constraints(actual).min()>=-1e-5 and negative_rejected
    result=dict(status='PASS' if ok else 'FAIL',scope='SYNTHETIC ACTUAL-CODE CONSTRAINT-GENERATION CONTROL ONLY',actual=actual.tolist(),expected=expected.tolist(),error=error,working_history=history,negative_disabled_cut_rejected_by_full_guard=negative_rejected,mutant=broken.tolist(),source=ref(source),producer=ref(__import__('pathlib').Path(__file__)),hardware_measured=False,product_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
