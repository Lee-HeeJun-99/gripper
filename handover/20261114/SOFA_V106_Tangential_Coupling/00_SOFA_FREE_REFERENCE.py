from sofa_v105 import create_scene

def createScene(root):
    return create_scene(root,case='00_BASELINE',k=0.0,dt=0.0005,connections='none',initial_offset_y=0.0)
