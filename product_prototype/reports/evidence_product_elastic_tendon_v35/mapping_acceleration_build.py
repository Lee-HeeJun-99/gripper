"""Bounded build of read-only Native mapping acceleration probe."""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'sofa/native_mapping_acceleration';build=BASE/'cad'/('build_'+a.tag);identity={name:sha(source/name) for name in ('Observer.cpp','CMakeLists.txt')}
 for name in identity:(out/name).write_bytes((source/name).read_bytes())
 config=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',480);compile_result=guarded(['cmake','--build',build,'--parallel','1'],out/'compile',480) if config['exit_code']==0 else None;binary=build/'libReGripMappingAcceleration.so';passed=compile_result is not None and compile_result['exit_code']==0 and binary.is_file()
 if any(sha(source/name)!=value for name,value in identity.items()):raise ValueError('source changed during build')
 result=dict(status='BUILD_PASS_READ_ONLY_PROBE' if passed else 'BUILD_FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_hashes=identity,build=str(build.relative_to(BASE.parent)),binary_sha256=sha(binary) if passed else None,configure=config,compile=compile_result,SDK='/home/ubuntu/SOFA/v26.06.00',scope='Read-only observer,NOT a physics model or SDK modification')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
