from sofa_v109 import create_scene

def createScene(root):
    return create_scene(root,case='06_TAN_K01_LDL_AXIAL',mode="combined",solver="ldl",k=0.1,dt=0.0005,axial_force=1e-05)
