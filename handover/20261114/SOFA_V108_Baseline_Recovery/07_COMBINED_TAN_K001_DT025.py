from sofa_v108 import create_scene
def createScene(root):
    return create_scene(root,case='07_COMBINED_TAN_K001_DT025',mode='combined',solver='cg',k=0.01,dt=0.00025,axial_force=0.0)
