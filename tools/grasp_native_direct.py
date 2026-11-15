"""Inside CPython3.12: fail before animation on construction/initialization errors."""
import importlib.util,os
from pathlib import Path
import Sofa.Core
import Sofa.Simulation
import SofaRuntime
project=Path(__file__).resolve().parents[1]
SofaRuntime.importPlugin(os.environ.get('REGRIP_NATIVE_PLUGIN',str(project/'build/grasp_20261115/stick_v4/libReGripStickSlip.so')))
spec=importlib.util.spec_from_file_location('native_surface',os.environ.get('REGRIP_NATIVE_SCENE',str(project/'scenes/grasp_native_surface.py')));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
root=Sofa.Core.Node('root');module.createScene(root);Sofa.Simulation.init(root)
for i in range(3600):Sofa.Simulation.animate(root,float(root.dt.value))
print('3600 iterations done; NATIVE_SURFACE_DIRECT_COMPLETE',flush=True)
Sofa.Simulation.unload(root)
