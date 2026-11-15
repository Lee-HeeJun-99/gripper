"""Only isolatedCPython3.12; installed-engine-only plugins, no matched SDK mixing."""
import os,importlib.util
import Sofa.Core,Sofa.Simulation,SofaRuntime
SofaRuntime.importPlugin(os.environ['REGRIP_NATIVE_FRAME']);SofaRuntime.importPlugin(os.environ['REGRIP_NATIVE_BEAM'])
spec=importlib.util.spec_from_file_location('native',os.environ['REGRIP_NATIVE_SCENE']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);root=Sofa.Core.Node('root');module.createScene(root);Sofa.Simulation.init(root);steps=int(os.environ['REGRIP_NATIVE_STEPS'])
for i in range(steps):Sofa.Simulation.animate(root,float(root.dt.value))
print(str(steps)+' iterations done; actual native conservative beam',flush=True);Sofa.Simulation.unload(root)
