"""Read-only installed binary evidence for free-position integration path.
No patching,hooking,library replacement or claimed source-code reconstruction.
"""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);sdk=Path('/home/ubuntu/SOFA/v26.06.00');lib=sdk/'lib/libSofa.Component.AnimationLoop.so.26.06.00';records=[]
 for name,begin,end in (('free_motion','0x41f56','0x42204'),('constraint_loop','0x4ba46','0x4c1dd')):
  proc=guarded(['objdump','-d','-C','--start-address='+begin,'--stop-address='+end,lib],out/name,480);text=(out/name/'stdout.log').read_text();records.append(dict(function=name,process=proc,contains_solve_visitor='SolveVisitor::SolveVisitor' in text,contains_position_vector_operation='MechanicalVOpVisitor::MechanicalVOpVisitor' in text,disassembly_sha256=sha(out/name/'stdout.log')))
 deps=[lib,sdk/'include/Sofa.Component.AnimationLoop/sofa/component/animationloop/FreeMotionAnimationLoop.h',sdk/'include/Sofa.Component.AnimationLoop/sofa/component/animationloop/ConstraintAnimationLoop.h',sdk/'include/Sofa.Simulation.Core/sofa/simulation/SolveVisitor.h',sdk/'include/Sofa.Simulation.Core/sofa/simulation/mechanicalvisitor/MechanicalVOpVisitor.h',sdk/'include/Sofa.Component.ODESolver.Backward/sofa/component/odesolver/backward/NewmarkImplicitSolver.h']
 result=dict(status='READ_ONLY_NATIVE_LOOP_BINARY_AUDIT',scope='Installed26.06 binary functions and public signatures only. SolveVisitor bool means free states,NOT velocity-only. The subsequent VOp receives freePos,pos,freeVel,dt. No inference that a public ODE-factor override alone fixes this loop;actual687 external-force states remain unchanged and failed.',producer_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),SDK_dependency_hashes={str(f):sha(f) for f in deps},records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
