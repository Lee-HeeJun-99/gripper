import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import numpy as np
from film_surface_modal_response import rational_step
class RationalTests(unittest.TestCase):
 def test_local_orders(self):
  lam=4.;c=.3;q=.2;v=1.3;omega=np.sqrt(lam-c*c/4)
  for method,lower,upper in (('Gauss2',25,40),('Radau2',12,20)):
   errors=[]
   for h in (.1,.05):
    exact=np.exp(-c*h/2)*np.array([q*np.cos(omega*h)+(v+c*q/2)*np.sin(omega*h)/omega,v*np.cos(omega*h)-(lam*q+c*v/2)*np.sin(omega*h)/omega])
    got=np.array(rational_step(q,v,lam,c,h,method));errors.append(np.linalg.norm(got-exact))
   self.assertTrue(lower<errors[0]/errors[1]<upper)
 def test_energy_inventory(self):
  lam=np.array([1.,100.,1e6]);q=np.array([.2,.3,.4]);v=np.array([1.,2.,3.]);initial=.5*(lam*q*q+v*v)
  for method in ('Gauss2','Radau2'):
   x,y=q.copy(),v.copy()
   for i in range(32):x,y=rational_step(x,y,lam,0,.01,method)
   energy=.5*(lam*x*x+y*y)
   if method=='Gauss2':self.assertLess(np.max(abs(energy-initial)/initial),1e-13)
   else:self.assertTrue(np.all(energy<initial)) # Recorded numerical damping,not heat.
 def test_ballistic(self):
  for method in ('Gauss2','Radau2'):
   q,v=rational_step(2.,3.,0.,0.,.125,method);self.assertEqual(q,2.375);self.assertEqual(v,3.)
if __name__=='__main__':unittest.main()
