"""dmsh_build.py quad_prim_id on synthetic MSL: quads emulated as triangles
in Metal receive primitive_id per triangle; gl_PrimitiveID is per quad (gl_PrimitiveID >> 1)."""
import ast
from pathlib import Path
import re
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import dmsh_side   # noqa: E402


def load():
    tree = ast.parse((TOOLS / 'dmsh_build.py').read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'quad_prim_id']
    ns = {'re': re, 'dmsh_side': dmsh_side}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(TOOLS / 'dmsh_build.py'), 'exec'), ns)
    return ns['quad_prim_id']


quad_prim_id = load()

SHADER_WITH_PRIM_ID = '''#include <metal_stdlib>
using namespace metal;

struct main0_out { float4 c [[color(0)]]; };
struct main0_in { float4 p [[user(locn0)]]; };

fragment main0_out main0(main0_in in [[stage_in]], uint gl_PrimitiveID [[primitive_id]])
{
    main0_out out = {};
    out.c = float4(float(gl_PrimitiveID), 0, 0, 1);
    return out;
}
'''

SHADER_WITHOUT_PRIM_ID = '''#include <metal_stdlib>
using namespace metal;

struct main0_out { float4 c [[color(0)]]; };
struct main0_in { float4 p [[user(locn0)]]; };

fragment main0_out main0(main0_in in [[stage_in]])
{
    main0_out out = {};
    out.c = in.p;
    return out;
}
'''


class TestQuadPrimId(unittest.TestCase):
    def test_inserts_shift(self):
        res = quad_prim_id(SHADER_WITH_PRIM_ID)
        self.assertIn('gl_PrimitiveID = gl_PrimitiveID >> 1;', res)
        # Check that it's inserted inside main0's body
        self.assertRegex(res, r'main0\([^)]*\)\s*\{\s*gl_PrimitiveID = gl_PrimitiveID >> 1;')

    def test_inserts_shift_custom_variable(self):
        shader = SHADER_WITH_PRIM_ID.replace('gl_PrimitiveID', 'custom_prim')
        res = quad_prim_id(shader)
        self.assertIn('custom_prim = custom_prim >> 1;', res)
        self.assertRegex(res, r'main0\([^)]*\)\s*\{\s*custom_prim = custom_prim >> 1;')

    def test_leaves_non_prim_id_unchanged(self):
        res = quad_prim_id(SHADER_WITHOUT_PRIM_ID)
        self.assertEqual(res, SHADER_WITHOUT_PRIM_ID)


if __name__ == '__main__':
    unittest.main()
