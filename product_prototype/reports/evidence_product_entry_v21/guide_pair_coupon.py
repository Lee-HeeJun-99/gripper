"""Native two-free-guide collision extracted at375 pre-overlap;not attached FEM."""
import argparse,copy,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha,rotation
from native_bending_coupon import guarded,flat

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--dt',type=float,choices=(.0025,.00125,.000625),default=.0025);p.add_argument('--velocity-first',action='store_true');p.add_argument('--contact-audit',action='store_true');p.add_argument('--row-binary',type=Path);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results/force_release_clear_support375';tree=ET.parse(source/'scene.scn');old=tree.getroot();index=954 # actual2.3875s frame,not a checkpoint claim
    specs=[]
    for f,j,k in ((1,0,5),(2,1,5)):
        rows=list(csv.DictReader((source/f'finger{f}.csv').open()));frames=list(csv.DictReader((source/f'guide_frames{f}.csv').open()));assert abs(float(rows[index]['time_s'])-2.3875)<1e-12
        q=np.fromstring(frames[index]['rigid_q'],sep=' ').reshape(-1,7)[j*6+k];v=np.fromstring(frames[index]['rigid_v'],sep=' ').reshape(-1,6)[j*6+k];point=np.fromstring(rows[index][f'guide{j}_q_m'],sep=' ').reshape(-1,3)[k];specs.append((q,v,point))
    identity=json.loads((source/'summary.json').read_text())
    if sha(BASE.parent/identity['build']/'libReGripProductSequence.so')!=identity['binary_sha256']:raise ValueError('frozen native journal binary mismatch')
    if a.row_binary:
        from observer_identity import compiled_pair_rows
        binary,compiled_source=compiled_pair_rows()
        if sha(a.row_binary)!=sha(binary):raise ValueError('unqualified row binary')
    records=[];radius=float(old.find("./Node[@name='guides1']/Node[@name='cable0']/SphereCollisionModel").get('radius'));mass=1e-5;dt=a.dt;steps=round(.01/dt)
    for alarm in (.001,.005):
        d=out/str(int(alarm*1000));d.mkdir();root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
        for n in old:
            if n.tag in ('RequiredPlugin','FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','CollisionPipeline','BruteForceBroadPhase','BVHNarrowPhase','MinProximityIntersection','CollisionResponse','EulerImplicitSolver','SparseLDLSolver','GenericConstraintCorrection'):root.append(copy.deepcopy(n))
        root.find('MinProximityIntersection').set('alarmDistance',str(alarm))
        if a.velocity_first:root.find('FreeMotionAnimationLoop').set('solveVelocityConstraintFirst','1')
        for i,(q,v,point) in enumerate(specs):
            node=ET.SubElement(root,'Node',name=f'guide{i}');ET.SubElement(node,'MechanicalObject',name='frames',template='Rigid3d',position=flat(q[None,:]),velocity=flat(v[None,:]));ET.SubElement(node,'UniformMass',template='Rigid3d',vertexMass='.00001 1e-8 1e-6 0 0 0 1e-6 0 0 0 1e-6')
            child=ET.SubElement(node,'Node',name='collision');ET.SubElement(child,'MechanicalObject',name='points',template='Vec3d',position=flat(point[None,:]));ET.SubElement(child,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords='1');ET.SubElement(child,'SphereCollisionModel',radius=str(radius),group=str(i+1));ET.SubElement(node,'NativeRigidJournal',body='@frames',solver='@../constraints',auditMass='1',filename=str(d/f'guide{i}.csv'))
        if a.contact_audit:
            narrow=root.find('BVHNarrowPhase');manager=root.find('CollisionResponse')
            ET.SubElement(root,'NativeDetectionPairs',narrow='@'+narrow.get('name'),filename=str(d/'detector.csv'))
            ET.SubElement(root,'NativeConstraintJournal',solver='@constraints',filename=str(d/'constraints.csv'))
            for i in (0,1):
                ET.SubElement(root,'NativeResponseRows',manager='@'+manager.get('name'),body=f'@guide{i}/frames',solver='@constraints',filename=str(d/f'response{i}.csv'))
        if a.row_binary:
            ET.SubElement(root,'RequiredPlugin',pluginName=str(a.row_binary.resolve()))
            for i in (0,1):ET.SubElement(root,'NativePairRows',body=f'@guide{i}/frames',solver='@constraints',filename=str(d/f'direct{i}.csv'))
        ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/x).read_text() for x in ('stdout.log','stderr.log'));r=dict(alarm_mm=alarm*1000,process=process,status='FAIL_NATIVE_COUPON',scene_sha256=sha(d/'scene.scn'))
        if process['exit_code']==0 and '[ERROR]' not in logs:
            rows=[list(csv.DictReader((d/f'guide{i}.csv').open())) for i in (0,1)];points=[];vel=[]
            for i,data in enumerate(rows):
                local=rotation(specs[i][0][3:]).T@(specs[i][2]-specs[i][0][:3]);q=np.array([np.fromstring(x['rigid_q'],sep=' ').reshape(7) for x in data]);points.append(np.array([x[:3]+rotation(x[3:])@local for x in q]));vel.append(np.array([np.fromstring(x['rigid_v'],sep=' ')[:3] for x in data]))
            gaps=(np.linalg.norm(points[0]-points[1],axis=1)-2*radius)*1000;momentum=mass*(vel[0]+vel[1]-specs[0][1][:3]-specs[1][1][:3]);r.update(status='NATIVE_FREE_PAIR_DIAGNOSTIC_ONLY',gap_mm=gaps.tolist(),minimum_gap_mm=float(gaps.min()),linear_momentum_max_error_Ns=float(np.max(abs(momentum))),frames=len(rows[0]))
        records.append(r)
    result=dict(scope='Two FREE guides at extracted position/velocity;NO rail attachments,FEM,cables,gravity.Independent Native detection contrast,NOT source trajectory restart or grasp fix.',velocity_first=a.velocity_first,dt_s=dt,steps=steps,source_scene_sha256=sha(source/'scene.scn'),source_binary_sha256=json.loads((source/'summary.json').read_text())['binary_sha256'],producer_sha256=sha(Path(__file__)),actual_source_time_s=2.3875,initial_gap_mm=float((np.linalg.norm(specs[0][2]-specs[1][2])-2*radius)*1000),records=records)
    result['contact_audit']=a.contact_audit
    result['initial_rigid_q']=[q.tolist() for q,v,p in specs];result['initial_rigid_v']=[v.tolist() for q,v,p in specs]
    result['source_commit']=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip()
    result['sdk']='/home/ubuntu/SOFA/v26.06.00'
    if a.row_binary:
        result['row_binary_sha256']=sha(a.row_binary)
        result['row_binary_path']=str(a.row_binary.resolve())
        result['row_compiled_source_sha256']=sha(compiled_source)
        (out/'Observer.cpp').write_bytes(compiled_source.read_bytes())
        (out/'CMakeLists.txt').write_bytes((BASE/'sofa/native_pair_rows/CMakeLists.txt').read_bytes())
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
