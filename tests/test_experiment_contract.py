import json
from pathlib import Path
import tempfile
import unittest
from experiments.run import load_config,execute

class Contract(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.c=dict(model='multilayer-static-0.1',units='model_F_mm_s',assumptions='unit-test research assumption',parameters={})
    def config(self,text=None):
        p=self.root/'config.json';p.write_text(json.dumps(self.c) if text is None else text);return p
    def test_valid_and_duplicate_output(self):
        p=self.config();self.assertTrue(execute(p,self.root/'out')['numerical_gate'])
        with self.assertRaises(FileExistsError):execute(p,self.root/'out')
    def test_bad_json(self):
        for text in ('{','[]','{"parameters": NaN}'):
            with self.assertRaises(ValueError):load_config(self.config(text))
    def test_missing_or_unknown_keys(self):
        for key in list(self.c):
            c=self.c.copy();del c[key];p=self.root/'bad.json';p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):load_config(p)
        self.c['extra']=1
        with self.assertRaises(ValueError):load_config(self.config())
    def test_invalid_model_units_assumptions(self):
        for key,value in [('model','fake'),('units','N_m_s'),('assumptions','')]:
            c=self.c.copy();c[key]=value;p=self.root/'bad.json';p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):load_config(p)
    def test_invalid_parameters(self):
        for params in ({'layers':0},{'unknown':1},{'connectors':[1,1]},{'young':float('inf')}):
            self.c['parameters']=params
            with self.assertRaises(ValueError):load_config(self.config())

if __name__=='__main__':unittest.main()
