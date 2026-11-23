"""Installed-ABI bounded build for narrow Native Newmark factor adapter."""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'sofa/native_newmark_factors';build=BASE/'cad'/('build_'+a.tag);identity={n:sha(source/n) for n in ('Adapter.cpp','CMakeLists.txt')}
 for n in identity:(out/n).write_bytes((source/n).read_bytes())
 config=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',480);compile=guarded(['cmake','--build',build,'--parallel','1'],out/'compile',480) if config['exit_code']==0 else None;binary=build/'libReGripNewmarkFactors.so'
 if any(sha(source/n)!=v for n,v in identity.items()):raise ValueError('source changed during build')
 sdk=Path('/home/ubuntu/SOFA/v26.06.00');deps=[sdk/'include/Sofa.Component.ODESolver.Backward/sofa/component/odesolver/backward/NewmarkImplicitSolver.h',sdk/'lib/libSofa.Component.ODESolver.Backward.so.26.06.00'];result=dict(status='BUILD_PASS' if compile and compile['exit_code']==0 and binary.exists() else 'BUILD_FAIL',scope='Only two integration-factor interface overrides;Native solve is inherited. Not a new ODE/contact solver or B3 qualification.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_hashes=identity,build=str(build.relative_to(BASE.parent)),binary_sha256=sha(binary) if binary.exists() else None,SDK=str(sdk),SDK_dependency_hashes={str(f):sha(f) for f in deps},configure=config,compile=compile)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
