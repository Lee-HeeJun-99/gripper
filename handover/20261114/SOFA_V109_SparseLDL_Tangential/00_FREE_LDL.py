from sofa_v109 import create_scene

def createScene(root):
    return create_scene(root,case='00_FREE_LDL',mode="combined",solver="ldl",k=0,dt=0.0005,axial_force=0)
