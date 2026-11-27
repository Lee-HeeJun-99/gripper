"""Same actual spool/string with endpoint attached to original FE Root coordinate.
Auxiliary dy is zero in shooting; FE RootY requires augmented original equality.
World Y cable force is transmitted through Root port, never discarded.
"""
import numpy as np
from primary_seated_string import SeatedString
class AttachedString(SeatedString):
 def evaluate(self,z,details=False):
  r=super().evaluate(z,details)
  if not details:
   r[-1]=z[-1];return r
  original=list(r['residual']);r['unconstrained_world_Y_cable_force_N']=float(original[-1]);r['residual'][-1]=float(z[-1]);r['attachment_mode']='Auxiliary string slip=0; physical FE RootY requires augmented-coordinate coupling';return r
