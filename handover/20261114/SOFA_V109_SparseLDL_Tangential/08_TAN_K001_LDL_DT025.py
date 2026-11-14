from sofa_v109 import create_scene

def createScene(root):
    return create_scene(root,case='08_TAN_K001_LDL_DT025',mode="combined",solver="ldl",k=0.01,dt=0.00025,axial_force=0)
