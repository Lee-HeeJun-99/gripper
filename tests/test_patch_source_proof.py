import ast
import pathlib
import unittest


class PatchProof(unittest.TestCase):
    def test_force_edit_does_not_disappear(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        tree=ast.parse((root/'tools/curve_patch_proof.py').read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='reverse')
        scope={'ast':ast};exec(compile(ast.Module(body=[function],type_ignores=[]),'proof','exec'),scope)
        generator='\n'.join('once('+repr('old'+str(i))+','+repr('new'+str(i))+')'for i in range(6))
        parent='CurvedMaterialContact '+' '.join('old'+str(i)for i in range(6))+' force=original'
        compiled='PatchRefinedContact '+' '.join('new'+str(i)for i in range(6))+' force=original'
        self.assertEqual(scope['reverse'](compiled,generator),parent)
        self.assertNotEqual(scope['reverse'](compiled.replace('force=original','force=wrong'),generator),parent)


if __name__=='__main__':unittest.main()
