"""Auditable XML adapter of V109 create_combined_scene, k=0 by default.

Original sources under handover are never edited. Native WriteState replaces
Python Recorder109 only. No change to mechanics, mass, solver, or load.
"""
import argparse
import math
from pathlib import Path
import xml.etree.ElementTree as ET

PLUGINS = ['AnimationLoop', 'Constraint.Projective', 'LinearSolver.Direct',
           'ODESolver.Backward', 'Mass', 'SolidMechanics.FEM.Elastic',
           'StateContainer', 'Topology.Container.Constant', 'MechanicalLoad',
           'Mapping.NonLinear', 'Playback']


def generate(destination, dt=0.0005, load=0.0001, k=None, connectors=None, n=11):
    from trial_validation import validate_config
    validate_config(k,connectors,dt,dt,load,n,60)
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element('Node', name='V109_NATIVE_FREE', dt=str(dt), gravity='0 0 0')
    for i, plugin in enumerate(PLUGINS):
        ET.SubElement(root, 'RequiredPlugin', name='req' + str(i), pluginName='Sofa.Component.' + plugin)
    ET.SubElement(root, 'DefaultAnimationLoop')
    ET.SubElement(root, 'EulerImplicitSolver', rayleighMass='0.2', rayleighStiffness='0.1')
    ET.SubElement(root, 'SparseLDLSolver', name='globalLDL', template='CompressedRowSparseMatrixd')
    body = ET.SubElement(root, 'Node', name='Bilayer')
    poses = [[30.0*i/(n-1), 0, z, 0, 0, 0, 1] for z in [-0.2, 0.2] for i in range(n)]
    ET.SubElement(body, 'MechanicalObject', name='dofs', template='Rigid3d',
                  position=' '.join(str(v) for p in poses for v in p))
    lines = [[i, i+1] for i in range(n-1)] + [[n+i, n+i+1] for i in range(n-1)]
    ET.SubElement(body, 'MeshTopology', name='edges', lines=' '.join(str(v) for p in lines for v in p))
    ET.SubElement(body, 'UniformMass', totalMass='0.00002')
    radius = (4*(8*0.4**3/12)/math.pi)**0.25
    ET.SubElement(body, 'BeamFEMForceField', radius=str(radius), radiusInner='0',
                  youngModulus='250', poissonRatio='0.32')
    ET.SubElement(body, 'FixedProjectiveConstraint', indices=f'0 {n}')
    ET.SubElement(body, 'ConstantForceField', indices=f'{n-1} {2*n-1}',
                  forces=f'0 0 {-load/2} 0 0 0 0 0 {-load/2} 0 0 0')
    ET.SubElement(body, 'PrecisionStateWriter', filename=str(destination.parent/'rigid.txt'))
    if k is not None:
        attributes = dict(name='tangential', stiffness=str(k), layerThickness='0.4',
                          nodesPerLayer=str(n), includeRoot='false')
        if connectors is not None:
            if not connectors or any(i<1 or i>=n for i in connectors):
                raise ValueError('connectors must contain valid non-root node indices')
            attributes['connectorIndices']=' '.join(map(str, sorted(set(connectors))))
        ET.SubElement(body, 'TangentialRigidForceField', **attributes)
    iface = ET.SubElement(body, 'Node', name='Interface')
    ET.SubElement(iface, 'MechanicalObject', name='points', template='Vec3d',
                  position=' '.join(f'{30.0*i/(n-1)} 0 0' for _ in range(2) for i in range(n)))
    ET.SubElement(iface, 'RigidMapping', template='Rigid3d,Vec3d', input='@../dofs',
                  output='@points', rigidIndexPerPoint=' '.join(map(str, range(2*n))),
                  globalToLocalCoords='true')
    ET.SubElement(iface, 'PrecisionStateWriter', filename=str(destination.parent/'interface.txt'))
    ET.indent(root)
    ET.ElementTree(root).write(destination, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination')
    parser.add_argument('--dt', type=float, default=0.0005)
    args = parser.parse_args()
    generate(args.destination, dt=args.dt)
