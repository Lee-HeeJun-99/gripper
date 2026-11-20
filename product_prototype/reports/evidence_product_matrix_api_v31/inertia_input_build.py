"""Bounded installed-SDK build;not a replacement integration/contact solver."""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'sofa/native_inertia_input';build=BASE/'cad'/('build_'+a.tag);identity={n:sha(source/n) for n in ('Observer.cpp','CMakeLists.txt')}
 for n in identity:(out/n).write_bytes((source/n).read_bytes())
 configure=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',480);compile_result=guarded(['cmake','--build',build,'--parallel','1'],out/'compile',480) if configure['exit_code']==0 else None;binary=build/'libReGripInertiaInput.so';passed=compile_result is not None and compile_result['exit_code']==0 and binary.is_file()
 if any(sha(source/n)!=v for n,v in identity.items()):raise ValueError('source changed during build')
 result=dict(status='BUILD_PASS' if passed else 'BUILD_FAIL',scope='Sampled missing-inertia input candidate ONLY;NO solver/SDK change',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_hashes=identity,build=str(build.relative_to(BASE.parent)),binary_sha256=sha(binary) if passed else None,configure=configure,compile=compile_result,SDK='/home/ubuntu/SOFA/v26.06.00');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
