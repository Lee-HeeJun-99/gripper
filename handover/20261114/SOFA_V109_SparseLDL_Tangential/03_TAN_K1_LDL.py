from sofa_v109 import create_scene

def createScene(root):
    return create_scene(root,case='03_TAN_K1_LDL',mode="combined",solver="ldl",k=1.0,dt=0.0005,axial_force=0)
