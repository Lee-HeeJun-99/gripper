from sofa_v105 import create_scene

def createScene(root):
    return create_scene(root,case='01_ALL_ZERO_K01_DT05',k=0.01,dt=0.0005,connections='all',initial_offset_y=0.0)
