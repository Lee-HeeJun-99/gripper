import ast
import json
import pathlib
import unittest


class PatchLogGuards(unittest.TestCase):
    def test_requested_grid_is_not_enough(self):
        path=pathlib.Path(__file__).resolve().parents[1]/'tools/curve_patch_trial.py'
        tree=ast.parse(path.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='grid_log_check')
        scope={'json':json};exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
        check=scope['grid_log_check'];good='PATCH_GRID {"states":528000,"elements":120}\n'
        self.assertTrue(check(good,528000,120)[0])
        self.assertFalse(check('',528000,120)[0])
        self.assertFalse(check(good,624000,120)[0])
        self.assertFalse(check(good,528000,119)[0])
        self.assertFalse(check(good+'[WARNING] Unused Attribute: edgeSpacing',528000,120)[0])
        self.assertFalse(check(good+'PATCH_GRID {"states":480000,"elements":120}\n',528000,120)[0])


if __name__=='__main__':unittest.main()
