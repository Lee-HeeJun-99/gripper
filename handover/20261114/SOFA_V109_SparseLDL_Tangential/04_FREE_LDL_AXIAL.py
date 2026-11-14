from sofa_v109 import create_scene

def createScene(root):
    return create_scene(root,case='04_FREE_LDL_AXIAL',mode="combined",solver="ldl",k=0,dt=0.0005,axial_force=1e-05)
