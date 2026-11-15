import ast
import pathlib
import unittest


class LocalHistoryGuards(unittest.TestCase):
    def test_only_provenance_is_excluded(self):
        path = pathlib.Path(__file__).resolve().parents[1] / 'tools/curve_local_history.py'
        tree = ast.parse(path.read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'immutable')
        scope = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), scope)
        normalize = scope['immutable']
        first = dict(provenance='old', binary='abc', nested=[dict(source='123', provenance='old')])
        second = dict(provenance='new', binary='abc', nested=[dict(source='123', provenance='new')])
        self.assertEqual(normalize(first), normalize(second))
        second['binary'] = 'changed'
        self.assertNotEqual(normalize(first), normalize(second))
        second['binary'] = 'abc'
        second['nested'][0]['source'] = 'changed'
        self.assertNotEqual(normalize(first), normalize(second))


if __name__ == '__main__':
    unittest.main()
