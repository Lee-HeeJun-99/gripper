"""Native tension-only elastic-wire candidate, distinct from prescribed tension.

Unilateral spring against fixed anchor, exact taut/release/free-flight reference.
No custom force/ODE/contact; no SDK changes; stiffness is a research assumption.
"""
import argparse
import csv
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

from analyse import BASE, sha
from native_bending_coupon import guarded

SDK = Path('/home/ubuntu/SOFA/v26.06.00')
MASS, STIFFNESS, STRETCH = .001, 100., .01


def exact(time):
    omega = np.sqrt(STIFFNESS/MASS)
    release = np.pi/(2*omega)
    if time <= release:
        return np.array([STRETCH*(1-np.cos(omega*time)), STRETCH*omega*np.sin(omega*time)])
    return np.array([STRETCH+STRETCH*omega*(time-release), STRETCH*omega])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tag', required=True)
    p.add_argument('--ode', choices=('newmark','bdf1'), default='newmark')
    a = p.parse_args()
    out = BASE/'results'/a.tag
    out.mkdir(exist_ok=False)
    probe = BASE/'cad/build_b3_native_plane_force682/libReGripPenaltyProbe.so'
    if sha(probe) != '11d942a190d96ef3b80b47a31f279308b4a17a09ae8ca5d9b15e90d23028d1d9':
        raise ValueError('observer mismatch')
    records = []
    for mode in ('taut_release', 'initial_slack'):
        for h in (.00025, .000125, .0000625):
            d = out/(mode+'_'+format(h,'.7f'))
            d.mkdir()
            root = ET.Element('Node', name='root', dt=str(h), gravity='0 0 0')
            for plugin in ('AnimationLoop', 'ODESolver.Backward', 'LinearSolver.Direct', 'Mass', 'StateContainer', 'Constraint.Projective', 'SolidMechanics.Spring'):
                ET.SubElement(root, 'RequiredPlugin', pluginName='Sofa.Component.'+plugin)
            ET.SubElement(root, 'RequiredPlugin', pluginName=str(probe))
            ET.SubElement(root, 'DefaultAnimationLoop')
            if a.ode=='newmark':
                ET.SubElement(root, 'NewmarkImplicitSolver', gamma='.5', beta='.25', vdamping='0', rayleighMass='0', rayleighStiffness='0')
            else:
                ET.SubElement(root,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton='50',relativeSuccessiveStoppingThreshold='1e-12',relativeInitialStoppingThreshold='1e-12',absoluteResidualStoppingThreshold='1e-14',maxNbIterationsLineSearch='20',updateStateWhenDiverged='0')
                ET.SubElement(root,'BDFOdeSolver',order='1',newtonSolver='@newton',rayleighMass='0',rayleighStiffness='0')
            ET.SubElement(root, 'EigenSparseLU', name='linear', template='CompressedRowSparseMatrixMat3x3d')
            ET.SubElement(root, 'MechanicalObject', name='point', template='Vec3d', position='0 0 .1 0 0 0')
            ET.SubElement(root, 'UniformMass', totalMass='.002')
            ET.SubElement(root, 'FixedProjectiveConstraint', indices='0')
            ET.SubElement(root, 'SpringForceField', object1='@point', object2='@point', indices1='0', indices2='1', stiffness='100', damping='0', lengths='.09' if mode=='taut_release' else '.11', elongationOnly='1')
            ET.SubElement(root, 'NativePenaltyJournal', point='@point', filename=str(d/'probe.csv'))
            ET.ElementTree(root).write(d/'scene.scn')
            count = round(.008/h)
            proc = guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(count),'--hideProgressBar',d/'scene.scn'], d/'process',480)
            logs = ''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'))
            r = dict(mode=mode, dt_s=h, process=proc, sofa_errors=logs.count('[ERROR]'), status='FAIL_NATIVE_EXECUTION', frames=None, scene_sha256=sha(d/'scene.scn'))
            if proc['exit_code']==0 and not r['sofa_errors']:
                rows = list(csv.DictReader((d/'probe.csv.point.csv').open()))
                if len(rows)!=count:
                    raise ValueError('partial Native states')
                frames=[]
                for row in rows:
                    q=np.fromstring(row['q'],sep=' ').reshape(-1,3)
                    v=np.fromstring(row['v'],sep=' ').reshape(-1,3)
                    time=float(row['time_s'])
                    length=float(np.linalg.norm(q[1]-q[0]))
                    extension=max(0.,length-(.09 if mode=='taut_release' else .11))
                    energy=.5*MASS*float(v[1]@v[1])+.5*STIFFNESS*extension**2
                    ref=exact(time) if mode=='taut_release' else np.zeros(2)
                    frames.append(dict(time_s=time,q=q.tolist(),v=v.tolist(),reference_z_m=float(ref[0]),reference_vz_m_s=float(ref[1]),
                                       geometric_length_m=length,inferred_elastic_tension_N=STIFFNESS*extension,
                                       reconstructed_energy_J=energy,position_error_m=abs(float(q[1,2])-ref[0]),velocity_error_m_s=abs(float(v[1,2])-ref[1])))
                r.update(status='NATIVE_COMPLETED_REFERENCE_DIAGNOSTIC',frames=frames,
                         maximum_position_error_m=max(f['position_error_m'] for f in frames),maximum_velocity_error_m_s=max(f['velocity_error_m_s'] for f in frames),
                         maximum_energy_defect_J=max(abs(f['reconstructed_energy_J']-(.005 if mode=='taut_release' else 0.)) for f in frames),
                         maximum_anchor_displacement_m=max(float(np.linalg.norm(np.asarray(f['q'])[0]-[0,0,.1])) for f in frames))
            records.append(r)
            if r['frames'] is None:
                break
        if records[-1]['frames'] is None:
            break
    # Full common times, all pairs, no denominator floor or omitted zero crossing.
    pairs=[]
    active=[r for r in records if r['mode']=='taut_release' and r['frames']]
    for i,x in enumerate(active):
        for y in active[i+1:]:
            ratio=round(x['dt_s']/y['dt_s'])
            measurements=[]
            for j,fx in enumerate(x['frames']):
                fy=y['frames'][(j+1)*ratio-1]
                if abs(fx['time_s']-fy['time_s'])>1e-12:
                    raise ValueError('inconsistent common physical time')
                for field in ('q','v','inferred_elastic_tension_N','reconstructed_energy_J'):
                    u,w=np.asarray(fx[field]),np.asarray(fy[field])
                    absolute=float(np.max(abs(u-w)))
                    denominator=max(float(np.max(abs(u))),float(np.max(abs(w))))
                    relative=absolute/denominator if denominator else (0. if not absolute else None)
                    measurements.append(dict(time_s=fx['time_s'],observable=field,absolute=absolute,relative=relative))
            pairs.append(dict(dt_s=[x['dt_s'],y['dt_s']],pass_time_gate=all(m['relative'] is not None and m['relative']<=.001 for m in measurements),measurements=measurements))
    dependencies=[SDK/'lib/libSofa.Component.SolidMechanics.Spring.so',SDK/'lib/libSofa.Component.ODESolver.Backward.so',SDK/'include/Sofa.Component.SolidMechanics.Spring/sofa/component/solidmechanics/spring/SpringForceField.inl']
    result=dict(status='ELASTIC_TENDON_REFERENCE_DIAGNOSTIC_NOT_B3' if len(records)==6 and all(r['frames'] for r in records) else 'FAIL_NATIVE_ELASTIC_TENDON',ode=a.ode,scope='Native unilateral elastic string,not CableConstraint or force-control equivalent. No guide/routing/contact/real wire material/Holding qualification.',
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),observer_binary_sha256=sha(probe),
                SDK_dependency_hashes={str(k):sha(k) for k in dependencies},mass_kg=MASS,assumed_stiffness_N_m=STIFFNESS,initial_stretch_m=STRETCH,
                analytic_release_s=float(np.pi/2/np.sqrt(STIFFNESS/MASS)),time_gate=.001,RSS_bytes=None,records=records,pairs=pairs)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    (out/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({**{k:v for k,v in result.items() if k not in ('records','pairs')},'runs':[{k:v for k,v in r.items() if k!='frames'} for r in records],'time_pair_passes':[p['pass_time_gate'] for p in pairs]},indent=2))


if __name__=='__main__':
    main()
