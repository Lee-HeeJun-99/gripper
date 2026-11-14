from sofa_v108 import create_scene
def createScene(root):
    return create_scene(root,case='06_COMBINED_TAN_K1_CG_AXIAL',mode='combined',solver='cg',k=1.0,dt=0.0005,axial_force=1e-05)
