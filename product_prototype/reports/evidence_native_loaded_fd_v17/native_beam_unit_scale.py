"""Equivalent native static Rail units;SI force/torque/state qualification only.
No mass/dynamic/gravity model;N-mm-s uses a different unused mass unit.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,flat,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--length-unit',choices=['m','mm'],default='mm');p.add_argument('--nx',nargs='+',type=int,default=[21,41,81]);a=p.parse_args()
    if any(n not in (21,41,81) for n in a.nx):raise ValueError('canonical meshes required')
    scale=1000. if a.length_unit=='mm' else 1.;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);binary,compiled_source=compiled_observer('456')
    (out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
    (out/'Observer.cpp').write_bytes(compiled_source.read_bytes())
    (out/'CMakeLists.txt').write_bytes((compiled_source.parent/'CMakeLists.txt').read_bytes())
    (out/'CMakeCache.txt').write_bytes((BASE/'cad/build_unit_observer456/CMakeCache.txt').read_bytes());records=[]
    for nx in a.nx:
        case='native_rectangular_centered448' if nx==21 else 'native_rectangular_centered_refine449';source=BASE/'results'/case/str(nx)/'scene.scn';tree=ET.parse(source);root=tree.getroot();node=root.find('./Node');d=out/str(nx);d.mkdir()
        body=node.find('MechanicalObject');q0=np.fromstring(body.get('position'),sep=' ').reshape(-1,7);native=q0.copy();native[:,:3]*=scale;body.set('position',flat(native))
        interpolation=node.find('BeamInterpolation')
        for key in ('lengthY','lengthZ'):interpolation.set(key,' '.join(format(x*scale,'.17g') for x in np.fromstring(interpolation.get(key),sep=' ')))
        interpolation.set('defaultYoungModulus',' '.join(format(x/scale**2,'.17g') for x in np.fromstring(interpolation.get('defaultYoungModulus'),sep=' ')))
        root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(node,'NativeRigidAcceptedObserver',dict(body='@dofs',elastic='@elastic',filename=str(d/'NATIVE_EVENT_SI.csv'),lengthToM=str(1/scale)))
        node.find('./Node/NativePointJournal').set('filename',str(d/'RAW_NATIVE_UNITS.csv'));tree.write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'));clean=process['exit_code']==0 and not any(s in logs for s in ('[ERROR]','Line search failed','failed to converge','Unused Attribute'))
        r=dict(nx=nx,process=process,source_scene_sha256=sha(source),scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_SOLVE',geometry_roundtrip_error_m=float(np.max(abs(native[:,:3]/scale-q0[:,:3]))))
        fixed=np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int);free=np.ones(nx,dtype=bool);free[fixed]=False
        if (d/'NATIVE_EVENT_SI.csv').exists():
            rows=list(csv.DictReader((d/'NATIVE_EVENT_SI.csv').open()));frames=[]
            for step in (1,2):
                rr=[row for row in rows if int(row['step'])==step]
                if len(rr)!=nx:continue
                q=np.array([[float(row[k]) for k in ('x_m','y_m','z_m')] for row in rr]);quat=np.array([[float(row[k]) for k in ('qx','qy','qz','qw')] for row in rr]);f=np.array([[float(row[k]) for k in ('fx_N','fy_N','fz_N','tx_Nm','ty_Nm','tz_Nm')] for row in rr]);F=np.zeros_like(f);F[-1,2]=-1e-8;res=f+F
                frames.append(dict(step=step,force_residual_N=float(np.linalg.norm(res[free,:3])),torque_residual_Nm=float(np.linalg.norm(res[free,3:])),tip_m=float(-q[-1,2]),quaternion_norm_error=float(np.max(abs(np.linalg.norm(quat,axis=1)-1)))))
            r['frames_SI']=frames
            if nx==21 and clean:
                actual=list(csv.DictReader((d/'RAW_NATIVE_UNITS.csv').open()));control=list(csv.DictReader((BASE/'results/native_rectangular_centered448/21/states.csv').open()))
                r['SI_control_errors']={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')/scale-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,control)) for k in ('q','v')}
            valid=len(frames)==2 and all(f['force_residual_N']<=1e-12 and f['torque_residual_Nm']<=1e-12 and f['quaternion_norm_error']<=1e-12 for f in frames)
            if clean:r['status']='PASS_STATIC_FORCE_ONLY' if valid and all(e<=1e-12 for e in r.get('SI_control_errors',{}).values()) else 'FAIL_SI_FORCE_OR_API'
        records.append(r)
    result=dict(scope='Equivalent-unit STATIC Rail diagnostics;not dynamic/time/Skin/B3 certification',producer_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),binary_sha256=sha(binary),observer_source_sha256=sha(out/'Observer.cpp'),sdk='/home/ubuntu/SOFA/v26.06.00',native_length_unit=a.length_unit,length_to_m=1/scale,force_unit='N',native_torque_unit='N '+a.length_unit,
        young_modulus_native=250e6/scale**2,young_modulus_SI_Pa=250e6,force_gate_SI_N=1e-12,torque_gate_SI_Nm=1e-12,
        criterion_note='Native mixed force/torque residual is not unit invariant;mm imposes stricter native torque component. Independent SI gates unchanged.',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
