import ast
import pathlib
import unittest


class SealedRoles(unittest.TestCase):
    def test_no_source_or_git_output(self):
        path=pathlib.Path(__file__).resolve().parents[1]/'tools/curve_replay.py';tree=ast.parse(path.read_text());function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='inside_results');scope={};exec(compile(ast.Module(body=[function],type_ignores=[]),str(path),'exec'),scope)
        root=pathlib.Path('/tmp/regrip_readonly_path_test');valid=scope['inside_results'];case=root/'results/old'
        self.assertTrue(valid(case,root/'results/new',root))
        self.assertFalse(valid(case,root/'.git/new',root))
        self.assertFalse(valid(root/'models/case',root/'results/new',root))
        self.assertFalse(valid(case,root/'results',root))
        self.assertFalse(valid(case,root/'results/../models/new',root))

    def test_no_unrelated_role_digest_fallback(self):
        path=pathlib.Path(__file__).resolve().parents[1]/'tools/curve_replay.py'
        tree=ast.parse(path.read_text());function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='role_hashes');scope={}
        exec(compile(ast.Module(body=[function],type_ignores=[]),str(path),'exec'),scope);collect=scope['role_hashes']
        value={'parent':[{'frame_sha256':'actual','unrelated':'wrong'},{'nested':{'frame_sha256':'actual'}}]}
        self.assertEqual(collect(value,'frame_sha256'),{'actual'})
        self.assertEqual(collect({'unrelated':'actual'},'frame_sha256'),set())
        self.assertEqual(collect({'parent':[value,{'frame_sha256':'different'}]},'frame_sha256'),{'actual','different'})
        self.assertEqual(value['parent'][0]['unrelated'],'wrong')


if __name__=='__main__':unittest.main()
