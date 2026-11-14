"""Environment probe only; this is not the ReGrip reference model."""
import sys


def createScene(root):
    print("REGRIP_PYTHON_SMOKE", sys.version, flush=True)
    root.dt = 0.0005
    root.addObject("RequiredPlugin", name="animation", pluginName="Sofa.Component.AnimationLoop")
    root.addObject("DefaultAnimationLoop")
    return root
