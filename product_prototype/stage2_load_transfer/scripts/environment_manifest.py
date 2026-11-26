"""Recreation-environment fingerprint, separate OCC owners in separate processes."""
import argparse,hashlib,importlib.metadata as md,json,platform,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
p=argparse.ArgumentParser();p.add_argument('--family',choices=['cad','fem','analytical'],required=True);p.add_argument('--tag',required=True);a=p.parse_args()
out=ROOT/'models/analytical'/a.tag;out.mkdir(parents=True,exist_ok=False)
packages=[];binaries=[]
if a.family=='cad':
    import OCP
    packages=['cadquery-ocp','vtk'];binaries=list(Path(OCP.__file__).parent.rglob('*.so'))
elif a.family=='fem':
    import gmsh,osqp.ext_builtin
    packages=['gmsh','numpy','scipy','scikit-fem','meshio','pyamg','osqp'];binaries=[Path(gmsh.libpath),Path(osqp.ext_builtin.__file__)]
else:packages=['numpy','scipy']
result=dict(scope='CURRENT RECREATION ENVIRONMENT; NOT RETROACTIVE PROOF OF UNRECORDED HISTORICAL PROCESS ENVIRONMENT',family=a.family,
    executable=sys.executable,python=platform.python_version(),platform=platform.platform(),
    versions={name:md.version(name) for name in packages},binary_SHA256={str(path):digest(path) for path in binaries},
    source_SHA256=digest(Path(__file__)),command='python scripts/environment_manifest.py --family '+a.family+' --tag '+a.tag)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
