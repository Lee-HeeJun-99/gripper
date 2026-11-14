from sofa_v108 import create_scene
def createScene(root):
    return create_scene(root,case='02_COMBINED_FREE_CG',mode='combined',solver='cg',k=0.0,dt=0.0005,axial_force=0.0)
