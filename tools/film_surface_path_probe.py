"""Minimal independent replay of a failed whole-surface numerical path."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case);scene=ET.parse(source/'scene.scn');saved=list(csv.DictReader((source/'event.csv.states.csv').open()))[-1]
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';archive.mkdir()
    for directory in ('models/film_impact','models/film_native_contact','models/film_rail_tendon','models/film_shell','models/film_sphere_contact'):
        dest=archive/directory;dest.mkdir(parents=True)
        for f in (ROOT/directory).glob('*.h'):shutil.copy2(f,dest/f.name)
    cpp=archive/'diagnostics/film_impact/SurfacePathProbe.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_impact/SurfacePathProbe.cpp',cpp)
    field=scene.find("Node[@name='assembly']/FilmRailTendon");owner=scene.find('FilmWholeSurfaceEventOwner');topology=scene.find('.//TriangleSetTopologyContainer');mass=scene.find('.//DiagonalMass').get('vertexMass').split();tri=topology.get('triangles').split()
    values=[field.get('nx'),field.get('guideIntervals','4'),field.get('guideOffset'),field.get('bondStiffness'),str(int(field.get('rootGuideSecondOrder','0') in ('1','true'))),scene.getroot().get('dt'),'2',saved['time'],field.get('maximumTension'),field.get('rampTime'),field.get('releaseBegin'),field.get('releaseEnd'),owner.get('radius'),owner.get('center'),str(len(mass)),str(len(tri)//3),' '.join(mass),saved['local_displacement'],saved['local_velocity'],' '.join(tri)]
    (out/'input.txt').write_text('\n'.join(values)+'\n');binary=out/'probe'
    compile_result=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
    run=guarded([binary,out/'input.txt',out/'path.csv'],out/'run',120) if compile_result['exit_code']==0 else None
    result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='completed independent diagnostic,not CCD/physics qualification',compile=compile_result,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},input_sha256=sha(out/'input.txt'),case=a.case,state_sha256=sha(source/'event.csv.states.csv'))
    if binary.exists():result['binary_sha256']=sha(binary)
    if run and run['exit_code']==0:
        rows=list(csv.DictReader((out/'path.csv').open()));lowest=min(rows,key=lambda r:float(r['minimum_gap']));result['minimum_sampled']=lowest
    write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','minimum_sampled')}))
if __name__=='__main__':main()
