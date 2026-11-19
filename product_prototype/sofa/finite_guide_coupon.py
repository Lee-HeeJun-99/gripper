"""Native finite annular eyelet contact,shared CAD dimensions,not whole hardware.
No new physics solver. Manufactured orientation is an explicit NEW assumption.
"""
import argparse,copy,csv,json,sys,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from analyse import BASE,sha,rotation,cable_node
from native_bending_coupon import guarded,flat
from observer_identity import compiled_pair_rows
sys.path.insert(0,str(BASE/'cad'))
from generate import world,width,guide_normal,guide_outboard,stl

def eyelet(c,n):
    td=c['tendon'];ro=td['guide_outer_radius'];ri=td['guide_hole_radius'];length=td.get('guide_length_mm',2.)
    if not 0<ri<ro or length<=0 or n<8:raise ValueError('invalid finite eyelet')
    vertices=np.array([[x,r*np.cos(t),r*np.sin(t)] for x in (-length/2,length/2) for r in (ro,ri) for t in np.arange(n)*2*np.pi/n]);faces=[]
    def quad(a,b,c,d):faces.extend(((a,b,c),(a,c,d)))
    for k in range(n):
        j=(k+1)%n;quad(k,j,2*n+j,2*n+k);quad(n+j,n+k,3*n+k,3*n+j);quad(j,k,n+k,n+j);quad(2*n+k,2*n+j,3*n+j,3*n+k)
    m=trimesh.Trimesh(vertices,faces,process=False);m.fix_normals()
    exact=np.pi*(ro*ro-ri*ri)*length
    if not m.is_watertight or not m.is_winding_consistent or m.volume<=0:raise ValueError('nonclosed eyelet geometry')
    return m,dict(outer_radius_mm=ro,hole_radius_mm=ri,length_mm=length,length_source='shared config' if 'guide_length_mm' in td else 'existing CAD generate.py guide() h=2mm,explicit inherited assumption',segments=n,analytic_volume_mm3=exact,mesh_volume_mm3=float(m.volume),volume_relative_error=abs(float(m.volume)-exact)/exact,outer_radial_chord_error_mm=ro*(1-np.cos(np.pi/n)),watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),minimum_triangle_area_mm2=float(m.area_faces.min()))

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--segments',type=int,choices=(16,32,64),default=16);p.add_argument('--dt',type=float,choices=(.0025,.00125,.000625),default=.0025);p.add_argument('--intersection',choices=('minimum','local'),default='minimum');p.add_argument('--no-provenance',action='store_true');p.add_argument('--support',action='store_true');p.add_argument('--mapped-journal',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/force_release_clear_support375';cfg=json.loads((src/'config.json').read_text());m,geometry=eyelet(cfg,a.segments);stl(out/'eyelet_cad_mm.stl',m.vertices,m.faces);(out/'config.json').write_bytes((src/'config.json').read_bytes());template=BASE/'results/b3_direct_rows513';meta=json.loads((template/'summary.json').read_text());binary,frozen=compiled_pair_rows();old=ET.parse(src/'scene.scn');models=[];rest_error=0.
    physical=json.loads((src/'summary.json').read_text());physical_binary=BASE.parent/physical['build']/'libReGripProductSequence.so'
    if sha(physical_binary)!=meta['source_binary_sha256']:raise ValueError('physical observer binary mismatch before launch')
    for i,(finger,cable,k) in enumerate(((1,0,5),(2,1,5))):
        x=cfg['tendon']['guide_stations'][k];side=(-1,1)[cable];local=np.array([x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)]);angle=cfg['palm']['angles_deg'][finger];centre=np.array(world(cfg,local,angle));h=1e-3;ex=np.array(world(cfg,local+[h,0,0],angle))-np.array(world(cfg,local-[h,0,0],angle));ex/=np.linalg.norm(ex);ey=np.array(world(cfg,local+[0,h,0],angle))-centre;ey-=ex*(ex@ey);ey/=np.linalg.norm(ey);ez=np.cross(ex,ey);basis=np.stack((ex,ey,ez),axis=1)
        qrest=np.fromstring(old.find(f"./Node[@name='guides{finger}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)[cable*6+k];node=cable_node(old,finger,cable);reference=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)[k];rest_error=max(rest_error,float(np.max(abs(centre*.001-reference))));reference_vertices=(m.vertices@basis.T+centre)*.001;body_local=(reference_vertices-qrest[:3])@rotation(qrest[3:]);q=np.array(meta['initial_rigid_q'][i]);initial=body_local@rotation(q[3:]).T+q[:3];models.append(dict(vertices_m=initial.tolist(),body_local_vertices_m=body_local.tolist(),manufactured_basis=basis.tolist(),manufactured_center_mm=centre.tolist()))
        if a.support:
            from finite_guide_product import support
            bracket=support(cfg,x,side,angle);support_local=(bracket.vertices*.001-qrest[:3])@rotation(qrest[3:]);models[-1].update(support_vertices_m=(support_local@rotation(q[3:]).T+q[:3]).tolist(),support_body_local_vertices_m=support_local.tolist(),support_faces=bracket.faces.tolist());stl(out/f'support{i}_manufactured_mm.stl',bracket.vertices,bracket.faces)
    if rest_error>1e-12:raise ValueError('CAD/native centre mismatch')
    records=[]
    for alarm in ('1','5'):
        d=out/alarm;d.mkdir();root=ET.parse(template/alarm/'scene.scn').getroot();root.set('dt',str(a.dt))
        if a.intersection=='local':root.find('MinProximityIntersection').tag='LocalMinDistance'
        if a.no_provenance:
            for item in list(root):
                if item.tag in ('NativeResponseRows','NativeDetectionPairs','NativeConstraintJournal','NativePairRows'):root.remove(item)
        for item in root.iter():
            if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
        for i,data in enumerate(models):
            col=root.find(f"./Node[@name='guide{i}']/Node[@name='collision']");col.remove(col.find('SphereCollisionModel'));col.find('MechanicalObject').set('position',flat(data['vertices_m']));ET.SubElement(col,'MeshTopology',name='eyeletTopology',position=flat(data['vertices_m']),triangles=flat(m.faces));edges=sorted({tuple(sorted((int(f[j]),int(f[(j+1)%3])))) for f in m.faces for j in range(3)});col.find('MeshTopology').set('edges',flat(edges))
            for kind in ('Triangle','Line','Point'):ET.SubElement(col,kind+'CollisionModel',group=str(i+1))
            if a.mapped_journal:ET.SubElement(col,'NativePointJournal',body='@points',filename=str(d/f'mapped{i}_eyelet.csv'))
            if a.support:
                parent=root.find(f"./Node[@name='guide{i}']");child=ET.SubElement(parent,'Node',name='supportCollision');verts=data['support_vertices_m'];faces=data['support_faces'];edges=sorted({tuple(sorted((int(f[j]),int(f[(j+1)%3])))) for f in faces for j in range(3)});ET.SubElement(child,'MeshTopology',name='supportTopology',position=flat(verts),triangles=flat(faces),edges=flat(edges));ET.SubElement(child,'MechanicalObject',name='points',template='Vec3d',position=flat(verts));ET.SubElement(child,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords='1')
                for kind in ('Triangle','Line','Point'):ET.SubElement(child,kind+'CollisionModel',group=str(i+1))
                if a.mapped_journal:ET.SubElement(child,'NativePointJournal',body='@points',filename=str(d/f'mapped{i}_support.csv'))
        ET.ElementTree(root).write(d/'scene.scn');steps=round(.01/a.dt);process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));counts={}
        for name in ('guide0.csv','guide1.csv','detector.csv','response0.csv','response1.csv','direct0.csv','direct1.csv'):
            counts[name]=len(list(csv.DictReader((d/name).open()))) if (d/name).exists() else None
        actual=list(csv.DictReader((d/'guide0.csv').open())) if (d/'guide0.csv').exists() else [];records.append(dict(alarm_mm=int(alarm),process=process,status='RUN_COMPLETED_NOT_QUALIFIED' if process['exit_code']==0 and '[ERROR]' not in logs and counts['guide0.csv']==steps and counts['guide1.csv']==steps else 'FAIL_NATIVE_FINITE_GUIDE',scene_sha256=sha(d/'scene.scn'),journal_rows=counts,maximum_solver_error=max((float(r['solver_error']) for r in actual),default=None),maximum_solver_iterations=max((int(r['solver_iterations']) for r in actual),default=None),maximum_constraint_rows=max((int(r['object_J_rows']) for r in actual),default=None)))
    result=dict(scope='Two FREE finite eyelets,NOT rail/support/cartridge/B3/holding. Eyelet axis follows manufactured finger tangent;explicit orientation assumption missing from prior sphere CAD proxies. Support solid NOT MODELLED. Mass/inertia inherited,not newly calibrated for eyelet.',status='RUN_COMPLETED_NOT_QUALIFIED' if all(r['status']=='RUN_COMPLETED_NOT_QUALIFIED' for r in records) else 'FAIL_NATIVE_FINITE_GUIDE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_sha256=sha(Path(__file__)),source_config_sha256=sha(src/'config.json'),source_scene_sha256=sha(src/'scene.scn'),physical_binary_sha256=meta['source_binary_sha256'],row_binary_sha256=sha(binary),row_compiled_source_sha256=sha(frozen),sdk='/home/ubuntu/SOFA/v26.06.00',dt_s=a.dt,steps=round(.01/a.dt),actual_source_time_s=meta['actual_source_time_s'],initial_rigid_q=meta['initial_rigid_q'],initial_rigid_v=meta['initial_rigid_v'],geometry=geometry,CAD_native_rest_center_error_m=rest_error,models=models,records=records)
    result['intersection']=a.intersection
    result['provenance_observers']=not a.no_provenance
    result['support_included']=a.support
    result['mapped_journal']=a.mapped_journal
    if a.support:result['scope']='Two FREE compound finite eyelets+proposed convex supports;both collision surfaces ENABLED and separately identified. Same inherited TOTAL mass/inertia,not physical support mass calibration. Intended own bond overlaps;union/strength NOT VERIFIED. No FEM,cables,object or holding.'
    result['dependency_hashes']={str(f.relative_to(BASE.parent)):sha(f) for f in (BASE/'cad/generate.py',BASE/'cad/finite_guide_product.py',BASE/'sofa/analyse.py',BASE.parent/'tools/film_guarded_process.py')}
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('models','initial_rigid_q','initial_rigid_v')},indent=2))
if __name__=='__main__':main()
