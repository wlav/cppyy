import py, os, sys
from pytest import raises
from .support import setup_make, pylong

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("crossinheritanceDict.so"))

def setup_module(mod):
    setup_make("crossinheritanceDict.so")


class TestCROSSINHERITANCE:
    def setup_class(cls):
        cls.test_dct = test_dct
        import cppyy
        cls.example01 = cppyy.load_reflection_info(cls.test_dct)

    def test01_override_function(self):
        """Test ability to override a simple function"""

        import cppyy
        Base1 = cppyy.gbl.CrossInheritance.Base1

        assert Base1().get_value() == 42

        class Derived(Base1):
            def get_value(self):
                return 13

        assert Derived().get_value() == 13

        assert Base1.call_get_value(Base1())   == 42
        assert Base1.call_get_value(Derived()) == 13

    def test02_constructor(self):
        """Test constructor usage"""

        import cppyy
        Base1 = cppyy.gbl.CrossInheritance.Base1

        assert Base1(27).get_value() == 27

        class Derived1(Base1):
            def __init__(self, pyval):
                Base1.__init__(self)
                self.m_pyint = pyval

            def get_value(self):
                return self.m_pyint+self.m_int

        d = Derived1(2)
        assert d.m_int   == 42
        assert d.m_pyint ==  2
        assert d.get_value()           == 44
        assert Base1.call_get_value(d) == 44

        class Derived2(Base1):
            def __init__(self, pyval, cppval):
                Base1.__init__(self, cppval)
                self.m_pyint = pyval

            def get_value(self):
                return self.m_pyint+self.m_int

        d = Derived2(2, 27)
        assert d.m_int   == 27
        assert d.m_pyint ==  2
        assert d.get_value()           == 29
        assert Base1.call_get_value(d) == 29
