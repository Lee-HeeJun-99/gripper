"""Installed API axial-strain path;PRIVATE diagnostic poses,not equilibria."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,sha,guarded
from observer_identity import compiled_strain_observer,compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    binary,compiled=compiled_strain_observer();compiled_observer('451')
    for name in ('Observer.cpp','CMakeLists.txt'):(out/name).write_bytes((compiled.parent/name).read_bytes())
    (out/'CMakeCache.txt').write_bytes((binary.parent/'CMakeCache.txt').read_bytes());(out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
    sdk=Path('/home/ubuntu/SOFA/v26.06.00/plugins/BeamAdapter');headers=['component/forcefield/AdaptiveBeamForceFieldAndMass.inl','component/BaseBeamInterpolation.inl','component/BeamInterpolation.inl'];header_hashes={name:sha(sdk/'include/BeamAdapter'/name) for name in headers}
    records=[]
    for nx in (41,81):
        baseline=None;baseline_force=None
        for variant in ('base','plus','minus'):
            source=BASE/'results/native_beam_ulp_probe455'/f'{nx}_{variant}';d=out/f'{nx}_{variant}';d.mkdir();tree=ET.parse(source/'scene.scn');root=tree.getroot();node=root.find('./Node');old=node.find('NativeRigidTangentObserver');private=old.get('privatePositions');old.set('filename',str(d/'force'))
            root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(node,'NativeBeamStrainObserver',dict(body='@dofs',interpolation='@interpolation',filename=str(d/'PRIVATE_native_strain.csv'),privatePositions=private));node.find('./Node/NativePointJournal').set('filename',str(d/'ACTUAL_UNLOADED.csv'));tree.write(d/'scene.scn')
            process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
            logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
            if process['exit_code']!=0 or any(s in logs for s in ('[ERROR]','Unused Attribute','Line search failed','failed to converge')):raise RuntimeError('native strain query rejected;Raw preserved')
            rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader((d/'PRIVATE_native_strain.csv').open())];axial=np.zeros((nx,3));native=np.array([[float(r[k]) for k in ('fx_N','fy_N','fz_N')] for r in csv.DictReader((d/'force.probe.csv').open())]);previous=np.array([[float(r[k]) for k in ('fx_N','fy_N','fz_N')] for r in csv.DictReader((source/'native.probe.csv').open())])
            for r in rows:
                f=r['axial0_N']*np.array([r[k] for k in ('axis_x','axis_y','axis_z')]);axial[int(r['node0'])]+=f;axial[int(r['node1'])]-=f
            free=np.ones(nx,dtype=bool);free[np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int)]=False
            q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)[:,:3];actual=list(csv.DictReader((d/'ACTUAL_UNLOADED.csv').open()));error=max(float(np.max(abs(np.fromstring(r['q'],sep=' ').reshape(-1,3)-q0))) for r in actual)
            if variant=='base':baseline=axial.copy();baseline_force=native.copy()
            records.append(dict(nx=nx,variant=variant,process=process,scene_sha256=sha(d/'scene.scn'),source_scene_sha256=sha(source/'scene.scn'),actual_position_error_m=error,actual_frames=len(actual),native_force_reproduction_error_N=float(np.linalg.norm(native-previous)),
                axial_reconstructed_change_N=float(np.linalg.norm((axial-baseline)[free])),native_force_change_N=float(np.linalg.norm((native-baseline_force)[free])),change_reconstruction_error_N=float(np.linalg.norm(((axial-baseline)-(native-baseline_force))[free])),
                absolute_vs_relative_projection_max_m=max(abs(r['absolute_projected_m']-r['relative_projected_m']) for r in rows),
                baseline_global_axial_difference_N=float(np.linalg.norm((axial-native)[free,0])),status='PRIVATE_STRAIN_PATH_ONLY' if error==0 and len(actual)==2 else 'FAIL_STATE'))
    result=dict(scope='Installed native interpolation strain diagnosis;NOT corrected force,accepted equilibrium,mesh/time or grasp PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),producer_sha256=sha(Path(__file__)),binary_sha256=sha(binary),compiled_source_sha256=sha(out/'Observer.cpp'),beamadapter_binary_sha256=sha(sdk/'lib/libBeamAdapter.so'),sdk='/home/ubuntu/SOFA/v26.06.00',header_sha256=header_hashes,assumptions='straight geometric rest,reinforceLength=false,shearStressComputation=true,no end offsets;reconstructed axial component only,not full native force',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
