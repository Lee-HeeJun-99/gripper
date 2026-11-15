"""Executed only inside isolated CPython3.12/SofaPython3."""
import importlib.util,os
import Sofa.Core,Sofa.Simulation,SofaRuntime
SofaRuntime.importPlugin(os.environ['REGRIP_NATIVE_PLUGIN'])
spec=importlib.util.spec_from_file_location('surface',os.environ['REGRIP_NATIVE_SCENE']);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
root=Sofa.Core.Node('root');module.createScene(root);Sofa.Simulation.init(root)
steps=int(os.environ['REGRIP_NATIVE_STEPS'])
for i in range(steps):Sofa.Simulation.animate(root,float(root.dt.value))
print(str(steps)+' iterations done; native surface integration complete',flush=True);Sofa.Simulation.unload(root)
