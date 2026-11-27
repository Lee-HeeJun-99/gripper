"""P1 Root-local relative translation with five internal string equations.
Preserve original world-Y model; return exact local directional endpoint force.
"""
import numpy as np
from primary_prescribed_string28 import PrescribedYString
from primary_seated_string import SeatedString
class LocalGammaString(PrescribedYString):
 def __init__(self,points,Rm,C,E,r,gamma_mm,order=16,axis=None):
  super().__init__(points,Rm,C,E,r,gamma_mm,order)
  self.axis=np.array(axis,dtype=float);assert abs(np.linalg.norm(self.axis)-1)<1e-12
 def evaluate(self,z,details=False):
  original=self.E.copy();self.E=original+self.axis*self.gamma_mm*.001
  try:full=SeatedString.evaluate(self,np.r_[z,0.],details)
  finally:self.E=original
  if not details:return full[:5]
  full['residual']=full['residual'][:5];full['solver_state']=np.asarray(z).tolist()
  full['root_local_Y_shift_mm']=self.gamma_mm;full['root_local_Y_axis']=self.axis.tolist()
  full['upstream_gamma_generalized_force_N']=float(self.axis@full['Fe_N'])
  return full
