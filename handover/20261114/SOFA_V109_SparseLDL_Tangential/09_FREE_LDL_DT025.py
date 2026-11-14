from sofa_v109 import create_scene

def createScene(root):
    return create_scene(root,case='09_FREE_LDL_DT025',mode="combined",solver="ldl",k=0,dt=0.00025,axial_force=0)
