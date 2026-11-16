"""Actual experimental film + separate flexible rails + routed-tendon dynamics.
Not tapered geometry, jamming, free-object contact or qualified grasp.
"""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,default=20);p.add_argument('--duration',type=float,default=.2);p.add_argument('--tension',type=float,default=.001);p.add_argument('--reuse',help='Immutable compiled assembly campaign;do not rerun its unit tests');a=p.parse_args()
    if not a.tag.replace('_','').isalnum() or not 1<=a.steps<=1000 or not 0<a.duration<=6 or not 0<=a.tension<=.02:raise ValueError('bounded prototype run')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('film_rail_'+a.tag)
    sources=list((ROOT/'models/film_rail_tendon').glob('*'))+list((ROOT/'models/film_shell').glob('*.h'))+list((ROOT/'tests').glob('test_film_rail*.cpp'))+[ROOT/'tools/film_rail_run.py']
    hashes={str(f.relative_to(ROOT)):sha(f) for f in sources if f.is_file()}
    for f in sources:
        if f.is_file():destination=out/'sources'/f.relative_to(ROOT);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,destination)
    stages={}
    if a.reuse:
        if not a.reuse.replace('_','').isalnum():raise ValueError('reuse tag')
        previous=ROOT/'results'/('autonomous_film_'+a.reuse);previous_identity=json.loads((previous/'identity.json').read_text());previous_summary=json.loads((previous/'summary.json').read_text())
        if previous_summary['status']!='PASS':raise RuntimeError('cannot reuse failed physics build')
        build=ROOT/'build'/('film_rail_'+a.reuse)
        if sha(build/'libReGripFilmRailTendon.so')!=previous_identity['binary_sha256']:raise RuntimeError('assembly binary changed')
        for rel,digest in previous_identity['sources'].items():
            if rel.startswith('models/') and sha(ROOT/rel)!=digest:raise RuntimeError('assembly model drift')
    commands=[] if a.reuse else [('configure',['cmake','-S',ROOT/'models/film_rail_tendon','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(ROOT/'.runtime/closure_sdk')]),('build',['cmake','--build',build,'-j2']),('kernel',[build/'test_film_rail_tendon']),('api',[build/'test_film_rail_tendon_api']),('ldd',['ldd',build/'libReGripFilmRailTendon.so'])]
    for name,cmd in commands:
        stages[name]=logged(cmd,out/name,180)
        if stages[name]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,stages=stages));return
    if hashes!={str(f.relative_to(ROOT)):sha(f) for f in sources if f.is_file()}:raise RuntimeError('source drift during build')
    nx=21;layout=[(0,5,24.,.05,0.,0.),(5*nx,3,1.322329862910148,.1,0.,-.075),(8*nx,3,1.322329862910148,.1,24-1.322329862910148,-.075)]
    # Compute width from the same declared equal-volume constraint, not a fit.
    rail_w=(439.3397917746089/3-100*24*.05)/(2*100*.1)
    layout=[(0,5,24.,.05,0.,0.),(5*nx,3,rail_w,.1,0.,-.075),(8*nx,3,rail_w,.1,24-rail_w,-.075)]
    n=11*nx;zero=' '.join(['0 0 0']*n);rest=[];triangles=[];masses=[];fixed=[];redundant=[]
    volume=439.3397917746089/3
    for offset,ny,width,thickness,y,z in layout:
        fixed.extend(range(offset,offset+ny));redundant.extend(range(offset+ny,offset+2*ny))
        for i in range(nx):
            for j in range(ny):rest.extend([100*i/(nx-1),y+width*j/(ny-1),z]);masses.append(1e-6*(100*width*thickness/volume)/(nx*ny))
        for i in range(nx-1):
            for j in range(ny-1):triangles.extend([offset+i*ny+j,offset+(i+1)*ny+j,offset+i*ny+j+1,offset+(i+1)*ny+j+1,offset+i*ny+j+1,offset+(i+1)*ny+j])
    sdk=ROOT/'build/grasp_20261115/sofa_patched';engine=ROOT/'build/film_shell_20261116_trapezoid_reference69/libReGripFilmShell.so';plugin=build/'libReGripFilmRailTendon.so';dt=a.duration/a.steps
    engine_manifest=json.loads((ROOT/'results/autonomous_film_20261116_trapezoid_reference69/compiled.json').read_text())
    if sha(engine)!=engine_manifest['binary_sha256']:raise RuntimeError('integration plugin drift')
    case=out/'1';case.mkdir();join=lambda x:' '.join(map(str,x))
    scene=f'''<Node name="experimental_film_rail" dt="{dt:.17g}" gravity="0 0 0"><RequiredPlugin pluginName="{engine}"/><RequiredPlugin pluginName="Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass Sofa.Component.ODESolver.Backward Sofa.Component.LinearSolver.Direct Sofa.Component.Constraint.Projective Sofa.Component.Topology.Container.Dynamic"/><DefaultAnimationLoop/><NewtonRaphsonSolver name="newton" maxNbIterationsNewton="30" maxNbIterationsLineSearch="12" absoluteResidualStoppingThreshold="1e-15" relativeInitialStoppingThreshold="1e-7" relativeSuccessiveStoppingThreshold="0"/><ReGripBDFSolver order="1" theta=".5" newtonSolver="@newton" rayleighMass="2" rayleighStiffness="0" profileFilename="{case/'profile.csv'}"/><ReGripMatrixLinearSystem name="system"/><EigenSparseLU linearSystem="@system" template="CompressedRowSparseMatrixd"/><MechanicalObject name="dofs" template="Vec3d" position="{zero}"/><FixedProjectiveConstraint indices="{join(fixed)}"/><PartialFixedProjectiveConstraint indices="{join(redundant)}" fixedDirections="0 0 1"/><Node name="assembly"><MechanicalObject name="surface" template="Vec3d" position="{zero}"/><DiagonalMass vertexMass="{join(masses)}" topology="@actual/topology" geometryState="@actual/world"/><FilmRailTendon nx="21" maximumTension="{a.tension:.17g}" rampTime="1" releaseBegin="1" releaseEnd="2" bondStiffness=".001" guideOffset=".2" filename="{case/'journal.csv'}"/><FilmAssemblyRootMapping nx="21" input="@../dofs" output="@surface" mapMasses="1"/><Node name="actual"><MechanicalObject name="world" template="Vec3d" position="{join(rest)}" rest_position="{join(rest)}"/><TriangleSetTopologyContainer name="topology" nbPoints="{n}" position="{join(rest)}" triangles="{join(triangles)}"/><FilmAssemblyWorldMapping nx="21" input="@../surface" output="@world" mapMasses="0"/></Node></Node></Node>'''
    (case/'scene.scn').write_text(scene)
    write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=hashes,binary_sha256=sha(plugin),integration_binary_sha256=sha(engine),driver_sha256=sha(sdk/'bin/graph_probe'),scene_sha256=sha(case/'scene.scn'),
        reused_build=a.reuse,binary_source_identity=previous_identity if a.reuse else None,
        geometry='rectangular equal-core-volume experimental single finger;not tapered concept_v2',core_volume_mm3=volume,total_model_mass=1e-6,layout=layout,material=dict(E=250,nu=0,measured=False),dt=dt,tension_per_rail=a.tension,bond_stiffness=.001,guide_offset=.2,
        force_model='five objective point attachments per rail;five eccentric actual-normal-offset guides;independent flexible strips',energy_scope='tendon generator is not cable stored energy;mechanical tendon work is separately approximated',command=__import__('sys').argv))
    stages['physics']=logged([sdk/'bin/graph_probe',sdk,case/'scene.scn',str(a.steps),'0',plugin],case/'process',480)
    log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text();rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else []
    finite=all(__import__('math').isfinite(float(v)) for r in rows for k,v in r.items() if k!='x')
    status='PASS' if stages['physics']['exit_code']==0 and len(rows)==a.steps and '[ERROR]' not in log and 'Unused Attribute' not in log and finite and 'Newton-Raphson method failed to converge' not in log else 'FAIL'
    write_json(out/'summary.json',dict(status=status,scope='experimental assembly execution only;NOT convergence/contact/grasp approval',stages=stages,rows=len(rows),expected_rows=a.steps,newton_failed_steps=log.count('Newton-Raphson method failed to converge'),finite=finite,last={k:v for k,v in rows[-1].items() if k!='x'} if rows else None,contact='NOT RUN',grasp='NOT RUN',coupled_energy='BLOCKED'))
    print(json.dumps(dict(status=status,rows=len(rows),last={k:v for k,v in rows[-1].items() if k!='x'} if rows else None)))

if __name__=='__main__':main()
