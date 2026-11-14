"""Analytical/independent reference checks; not SOFA or real-gripper validation."""
import math
import json
from dataclasses import replace
import unittest
from models.multilayer.beam import Design, solve, spring_slider, friction_path
from reference_fem.planar import solve as old_solve

class Research(unittest.TestCase):
    def test_old_30mm_reference(self):
        for k in (0.,1.,100.):
            d=Design(length=30,nodes=11,connectors=tuple(range(1,11)),load=1e-4,coupling=k)
            self.assertAlmostEqual(solve(d)['deflection_mm'],old_solve(k)['deflection_mm'],places=10)
    def test_cantilever_and_length_scaling(self):
        for layers in (1,2,4):
            d=Design(layers=layers,coupling=0);r=solve(d)
            exact=d.load*d.length**3/(3*layers*d.young*d.inertia)
            self.assertLess(abs(r['deflection_mm']/exact-1),1e-9)
            self.assertLess(abs(r['energy']-.5*r['external_work']),1e-14)
        d=Design(coupling=0);self.assertLess(abs(solve(d)['deflection_mm']/solve(replace(d,length=30))['deflection_mm']-(100/30)**3),1e-7)
    def test_timoshenko(self):
        d=Design(timoshenko=True,coupling=0);r=solve(d)
        G=d.young/(2*(1+d.poisson));exact=d.load/d.layers*(d.length**3/(3*d.young*d.inertia)+d.length/(d.shear_correction*G*d.area))
        self.assertLess(abs(r['deflection_mm']/exact-1),1e-8)
    def test_mesh_same_connectors(self):
        d=Design(nodes=11,connectors=(2,5,10));a=solve(d);b=solve(replace(d,nodes=21,connectors=(4,10,20)))
        self.assertLess(abs(a['deflection_mm']/b['deflection_mm']-1),1e-8)
    def test_wire_tip_moment(self):
        d=Design(coupling=0,load=0,wire_tension=1e-5,wire_eccentricity=.1);r=solve(d)
        exact=d.wire_tension*d.wire_eccentricity*d.length**2/(2*d.layers*d.young*d.inertia)
        self.assertLess(abs(r['deflection_mm']/exact-1),1e-8)
    def test_contact_complementarity_penalty(self):
        d=Design(coupling=0,contact_gap=.005,contact_stiffness=.1);r=solve(d)
        compliance=d.length**3/(3*d.layers*d.young*d.inertia)
        exact=(compliance*d.load+compliance*d.layers*d.contact_stiffness*d.contact_gap)/(1+compliance*d.layers*d.contact_stiffness)
        self.assertAlmostEqual(r['deflection_mm'],exact,places=10)
        self.assertGreater(r['contact_reaction'],0);self.assertLess(r['normalized_residual'],1e-6)
    def test_slider_dissipation_yield_and_reverse(self):
        a=spring_slider(.2,0,10,1);self.assertAlmostEqual(a['traction'],1);self.assertAlmostEqual(a['plastic'],.1)
        b=spring_slider(.1,a['plastic'],10,1);self.assertAlmostEqual(b['traction'],0)
        c=spring_slider(-.2,b['plastic'],10,1);self.assertAlmostEqual(c['traction'],-1);self.assertGreater(c['dissipation'],0)
    def test_friction_limits(self):
        d=Design();loads=[0,1e-6,2e-6,0,-1e-6,0]
        off=friction_path(d,loads,0,.3,8);on=friction_path(d,loads,1.,.3,8)
        self.assertAlmostEqual(off[1]['deflection_mm'],solve(replace(d,coupling=0))['deflection_mm'],places=9)
        self.assertAlmostEqual(on[1]['deflection_mm'],solve(d)['deflection_mm'],places=9)
        loop=friction_path(d,loads,1e-9,.3,8)
        self.assertTrue(all(r['dissipation']>=0 and r['residual']<1e-12 for r in loop));self.assertGreater(loop[-1]['cumulative_dissipation'],0)
    def test_invalid_parameters(self):
        for d in (Design(young=-1),Design(nodes=1),Design(connectors=(1,1)),Design(load=float('nan'))):
            with self.assertRaises(ValueError):solve(d)
        with self.assertRaises(ValueError):spring_slider(0,0,0,1)
    def test_slider_closed_cycle_work_balance(self):
        path=[i*.01 for i in range(21)]+[i*.01 for i in range(19,-21,-1)]+[i*.01 for i in range(-19,1)]
        plastic=0.;previous_s=0.;previous_t=0.;work=0.;diss=0.;energy=0.
        for slip in path:
            r=spring_slider(slip,plastic,10.,1.);work+=.5*(previous_t+r['traction'])*(slip-previous_s)
            diss+=r['dissipation'];energy=r['elastic_energy'];plastic=r['plastic'];previous_s=slip;previous_t=r['traction']
        self.assertAlmostEqual(work,energy+diss,places=12)
    def test_friction_checkpoint_json_restart(self):
        d=Design();loads=[0.,1e-6,2e-6,0.,-1e-6,0.]
        whole=friction_path(d,loads,1e-9,.3,8)
        first=friction_path(d,loads[:3],1e-9,.3,8,return_checkpoint=True)
        state=json.loads(json.dumps(first['checkpoint']))
        rest=friction_path(d,loads[3:],1e-9,.3,8,checkpoint=state)
        self.assertEqual(whole,first['records']+rest)
        with self.assertRaises(ValueError):friction_path(d,loads,2e-9,.3,8,checkpoint=state)
        state['q'][1]+=.1
        with self.assertRaisesRegex(ValueError,'hash mismatch'):friction_path(d,loads,1e-9,.3,8,checkpoint=state)

if __name__=='__main__':unittest.main()
