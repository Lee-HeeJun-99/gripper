from sofa_v108 import create_scene
def createScene(root):
    return create_scene(root,case='01_COMBINED_FREE_LDL',mode='combined',solver='ldl',k=0.0,dt=0.0005,axial_force=0.0)
