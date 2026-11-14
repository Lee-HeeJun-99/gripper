from sofa_v109 import create_scene

def createScene(root):
    return create_scene(root,case='01_TAN_K001_LDL',mode="combined",solver="ldl",k=0.01,dt=0.0005,axial_force=0)
