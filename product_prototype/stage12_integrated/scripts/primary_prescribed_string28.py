"""Conditional seated string with upstream gamma retained as an EXTERNAL DOF.

Reuse proven massive string ODE. Solve endpoint/length/motor torque equations
for five internal unknowns; return FeY as gamma force instead of setting FeY=0.
This does not qualify the gamma attachment to the physical Root/Finger model.
"""
import numpy as np
from scipy.optimize import root
from primary_seated_string import SeatedString

class PrescribedYString(SeatedString):
 def __init__(self,points,Rm,C,E,r,gamma_mm,order=16):
  super().__init__(points,Rm,C,E,r,order);self.gamma_mm=float(gamma_mm)
 def evaluate(self,z,details=False):
  full=super().evaluate(np.r_[z,self.gamma_mm],details)
  if not details:return full[:5]
  full['residual']=full['residual'][:5];full['solver_state']=np.asarray(z).tolist();full['upstream_gamma_generalized_force_N']=full['Fe_N'][1];return full
 def solve(self,seed):
  self.T=seed['T_N'];z=np.array([-seed['wire_start_tension_N'],0.,seed['drum_tangent_phi_rad'],seed['wire_free_length_m']*1000,seed['rotor_angle_rad']]);sol=root(self.evaluate,z,tol=1e-10);r=self.evaluate(sol.x,True);r.update(root_success=bool(sol.success),root_message=str(sol.message),residual_max=float(np.max(abs(sol.fun))));return r
