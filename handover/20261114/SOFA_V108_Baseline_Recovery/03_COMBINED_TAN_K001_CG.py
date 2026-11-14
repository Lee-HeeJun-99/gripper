from sofa_v108 import create_scene
def createScene(root):
    return create_scene(root,case='03_COMBINED_TAN_K001_CG',mode='combined',solver='cg',k=0.01,dt=0.0005,axial_force=0.0)
