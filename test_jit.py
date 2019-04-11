import pytest
import jit
from assembler import FunctionAssembler as FA
from test_assembler import TestFunctionAssembler as AssemblerTest

class TestCompiledFuntion(AssemblerTest):

    def test_basic(self):
        code = b'\xf2\x0f\x58\xc1\xc3' # addsd  xmm0,xmm1 ; ret
        p = jit.CompiledFunction(2, code)
        assert p.fptr(12.34, 56.78) == 12.34 + 56.78
        assert p(12.34, 56.78) == 12.34 + 56.78

    def load(self, asm):
        code = asm.assemble_and_relocate()
        return jit.CompiledFunction(asm.nargs, code)

class TestRegAllocator:

    def test_allocate(self):
        regs = jit.RegAllocator()
        assert regs.get('a') == FA.xmm0
        assert regs.get('b') == FA.xmm1
        assert regs.get('a') == FA.xmm0
        assert regs.get('c') == FA.xmm2

    def test_too_many_vars(self):
        regs = jit.RegAllocator()
        # force allocation of xmm0..xmm14
        for i in range(13):
            regs.get('var%d' % i)
        assert regs.get('var13') == FA.xmm13
        pytest.raises(NotImplementedError, "regs.get('var14')")


class TestAstCompiler:

    def test_empty(self):
        comp = jit.AstCompiler("""
        def foo():
            pass
        """)
        fn = comp.compile()
        assert fn() == 0

    def test_simple(self):
        comp = jit.AstCompiler("""
        def foo():
            return 100
        """)
        fn = comp.compile()
        assert fn() == 100

    def test_arguments(self):
        comp = jit.AstCompiler("""
        def foo(a, b):
            return b
        """)
        fn = comp.compile()
        assert fn(3, 4) == 4

    def test_add(self):
        comp = jit.AstCompiler("""
        def foo(a, b):
            return a+b
        """)
        fn = comp.compile()
        assert fn(3, 4) == 7

    def test_binops(self):
        comp = jit.AstCompiler("""
        def foo(a, b):
            return (a-b) + (a*b) - (a/b)
        """)
        fn = comp.compile()
        res = (3-4) + (3*4) - (3.0/4)
        assert fn(3, 4) == res
