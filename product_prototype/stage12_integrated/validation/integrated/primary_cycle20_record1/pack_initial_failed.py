import sys,json,shutil,numpy as np
from pathlib import Path
sys.path.insert(0,'product_prototype/stage12_integrated/scripts')
from baseline_registry import ROOT,REPO,ref,dump,sha
out=ROOT/'validation/integrated/primaryP1_conic_ritz_newton1';s=json.loads((out/'summary.json').read_text());p=REPO/s['output']['path'];a=dict(np.load(p));raw=ROOT/'build/raw/primary_cycle20';raw.mkdir(parents=True,exist_ok=False);shutil.copyfile(out/'summary.json',out/'initial_serialization_summary.json');old=ref(p);p.rename(raw/'ritz_original.npz');v=a.pop('V');basis=[]
for j,(lo,hi) in enumerate([(0,65),(65,130)]):
 f=out/f'basis_columns{j}.npz';np.savez_compressed(f,V=v[:,lo:hi]);basis.append(ref(f))
np.savez_compressed(p,**a);assert all(np.array_equal(a[k],np.load(p)[k]) for k in a);assert np.array_equal(v,np.column_stack([np.load(REPO[r['path']])['V'] for r in basis]));s['output']=ref(p);s['basis_columns']=basis;s['original_serialization_snapshot']=ref(out/'initial_serialization_summary.json');s['lossless_storage_manifest']=dict(original_output=old,preserved_original_raw=ref(raw/'ritz_original.npz'),array_values_changed=False,reason='Dense float64 Ritz basis split by columns for existing per-file50MB save rule. Original oversized bytes preserved in ignored build/raw; numerical entries bitwise unchanged.');dump(out/'summary.json',s)
# Preserve exact producer-time source summary, then point final evidence to the
# lossless representation. Original summary hash remains independently recorded.
for name in ['primaryP1_ritz_feasible1','primaryP1_ritz_feasible2','primaryP1_conic_ritz_audit1']:
 d=ROOT/'validation/integrated'/name;doc=json.loads((d/'summary.json').read_text());shutil.copyfile(d/'summary.json',d/'initial_serialization_summary.json');doc['execution_source_snapshot']=ref(out/'initial_serialization_summary.json');doc['source']=ref(out/'summary.json');doc['lossless_source_repack']=s['lossless_storage_manifest'];dump(d/'summary.json',doc)
print('Lossless basis archived and split; all array bits preserved')
