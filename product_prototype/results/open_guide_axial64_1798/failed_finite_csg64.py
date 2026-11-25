"""Installed Manifold Mesh64 adapter, no geometry repair or SDK changes.
Trimesh default adapter casts all input vertices to float32. This adapter
preserves float64 coordinates and indices; no merge/tolerance override.
"""
from functools import reduce
import numpy as np
import trimesh
import manifold3d

def boolean64(meshes,operation,check_volume=True,**kwargs):
    assert not kwargs, 'Undeclared engine options'
    if check_volume and not all(m.is_volume for m in meshes):
        raise ValueError('Input is not a positive closed volume')
    values=[]
    for mesh in meshes:
        value=manifold3d.Manifold(manifold3d.Mesh64(
            vert_properties=np.ascontiguousarray(mesh.vertices,dtype=np.float64),
            tri_verts=np.ascontiguousarray(mesh.faces,dtype=np.uint64)))
        assert value.status()==manifold3d.Error.NoError
        values.append(value)
    if operation=='union': result=reduce(lambda a,b:a+b,values)
    elif operation=='intersection': result=reduce(lambda a,b:a^b,values)
    elif operation=='difference': result=values[0]-reduce(lambda a,b:a+b,values[1:])
    else: raise ValueError(operation)
    assert result.status()==manifold3d.Error.NoError
    raw=result.to_mesh64()
    return trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=False)

def register():
    # Only the caller's in-process registry; no installed code/file patched.
    trimesh.boolean._engines['manifold64']=boolean64
