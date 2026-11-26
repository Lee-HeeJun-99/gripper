"""Synthetic software controls ONLY. Does not execute hardware or release CAD."""
import copy,json,tempfile,unittest
from pathlib import Path
from stage2_release_gate import REQUIRED,validate,sha
from hardware_records import evaluate
class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        (self.root/'synthetic.txt').write_text('SYNTHETIC SOFTWARE FIXTURE, NOT PRODUCT EVIDENCE')
        self.expected={'case':'synthetic'}
        self.doc=dict(test_only=True,baseline=self.expected,collision_models_removed=False,qv_forced=False,records={})
        for k,d in REQUIRED.items():
            metrics=[dict(name='ratio',value=.25,maximum=.5,unit='dimensionless')]
            if k=='numerical_convergence':metrics=[dict(name='time_relative',value=.0001,maximum=.001,unit='dimensionless'),dict(name='mesh_relative',value=.001,maximum=.01,unit='dimensionless')]
            refs={'synthetic.txt':sha(self.root/'synthetic.txt')}
            self.doc['records'][k]=dict(status='PASS',domain=d,scope='SYSTEM_LOAD_TRANSFER',material_basis='not_material_dependent',evidence=refs,source=refs,model=refs,metrics=metrics)
    def tearDown(self):self.temp.cleanup()
    def check_bad(self,d):self.assertEqual(validate(d,self.root,self.expected,allow_test=True)['status'],'STAGE2_NOT_QUALIFIED')
    def test_positive_software_fixture(self):self.assertEqual(validate(self.doc,self.root,self.expected,allow_test=True)['status'],'STAGE2_DIGITAL_RELEASE_PASS')
    def test_synthetic_cannot_release(self):self.assertEqual(validate(self.doc,self.root,self.expected)['status'],'STAGE2_NOT_QUALIFIED')
    def test_missing_criterion(self):
        d=copy.deepcopy(self.doc);del d['records']['coupling_capacity'];self.check_bad(d)
    def test_nan(self):
        d=copy.deepcopy(self.doc);d['records']['shaft_strength']['metrics'][0]['value']=float('nan');self.check_bad(d)
    def test_coupon_promotion(self):
        d=copy.deepcopy(self.doc);d['records']['finger_structure']['scope']='SMALL_COUPON';self.check_bad(d)
    def test_missing_evidence(self):
        d=copy.deepcopy(self.doc);d['records']['terminal_retention']['evidence']={};self.check_bad(d)
    def test_stale_hash(self):
        (self.root/'synthetic.txt').write_text('changed');self.check_bad(self.doc)
    def test_wrong_CAD(self):
        d=copy.deepcopy(self.doc);d['baseline']={};self.check_bad(d)
    def test_relaxed_time(self):
        d=copy.deepcopy(self.doc);d['records']['numerical_convergence']['metrics'][0]['maximum']=.01;self.check_bad(d)
    def test_typical_allowable(self):
        d=copy.deepcopy(self.doc);d['records']['shaft_strength']['material_basis']='typical';self.check_bad(d)
    def test_forced_state(self):
        d=copy.deepcopy(self.doc);d['qv_forced']=True;self.check_bad(d)
        self.assertFalse(validate(d,self.root,self.expected,allow_test=True)['analytical_pass'])
        self.assertFalse(validate(d,self.root,self.expected,allow_test=True)['numerical_pass'])
    def test_missing_source(self):
        d=copy.deepcopy(self.doc);d['records']['shaft_strength']['source']={};self.check_bad(d)
    def test_missing_model(self):
        d=copy.deepcopy(self.doc);d['records']['finger_structure']['model']={};self.check_bad(d)
    def test_blank_hardware(self):self.assertEqual(evaluate([])['status'],'NOT MEASURED')
    def test_synthetic_log_fit_only(self):
        rows=[dict(specimen_ID='SYNTHETIC',calibration_ID='SYNTHETIC',timestamp='SYNTHETIC',time_s=i,force_N=i*.1,extension_m=i*.0001,temperature_C=20) for i in range(6)]
        result=evaluate(rows);self.assertAlmostEqual(result['linear_stiffness_N_m'],1000);self.assertFalse(result['hardware_pass'])
    def test_hardware_nan(self):
        self.assertEqual(evaluate([dict(specimen_ID='x',calibration_ID='x',timestamp='x',time_s=0,force_N='nan',extension_m=0,temperature_C=20)])['status'],'INVALID')
if __name__=='__main__':unittest.main()
