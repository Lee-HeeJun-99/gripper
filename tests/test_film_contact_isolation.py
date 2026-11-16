import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from film_contact_isolate import clipped
from film_contact_oscillator import bdf,reference

class ContactIsolation(unittest.TestCase):
    def test_independent_area_force(self):
        self.assertEqual(clipped([-1.,0.,-2.],2.,3.),(0.,0.))
        self.assertEqual(clipped([1.,1.,1.],2.,3.),(2.,6.))
        area,force=clipped([1.,-1.,-1.],2.,3.)
        self.assertAlmostEqual(area,.5);self.assertAlmostEqual(force,.5)
        self.assertEqual(clipped([0.,0.,0.],2.,3.),(0.,0.))

    def test_bdf2_smooth_reference(self):
        ref,ramp=reference(0.,1e-11)
        errors=[]
        for n in (100,200,400):
            rows=bdf(np.linspace(0,2,n+1),0.,ramp)
            errors.append(max(abs(rows[:,1]-ref.sol(rows[:,0])[0])))
        self.assertGreater(errors[0]/errors[1],3.8)
        self.assertGreater(errors[1]/errors[2],3.8)
        self.assertAlmostEqual(ref.t_events[0][0],1.408373,places=10)

if __name__=='__main__':unittest.main()
