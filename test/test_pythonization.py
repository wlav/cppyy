import py, os, sys
from pytest import raises
from .support import setup_make, pylong

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("pythonizablesDict.so"))

def setup_module(mod):
    setup_make("pythonizablesDict.so")


class TestClassPYTHONIZATIONS:
    def setup_class(cls):
        cls.test_dct = test_dct
        import cppyy
        cls.pyzables = cppyy.load_reflection_info(cls.test_dct)

    def test00_api(self):
        """Test basic semantics of the pythonization API"""

        import cppyy

        raises(TypeError, cppyy.py.add_pythonization, 1)

        def pythonizor1(klass, name):
            pass

        def pythonizor2(klass, name):
            pass

        pythonizor3 = pythonizor1

        cppyy.py.add_pythonization(pythonizor1)
        assert cppyy.py.remove_pythonization(pythonizor2) == False
        assert cppyy.py.remove_pythonization(pythonizor3) == True

    def test01_size_mapping(self):
        """Use composites to map GetSize() onto buffer returns"""

        import cppyy

        def set_size(self, buf):
            buf.reshape((self.GetN(),))
            return buf

        cppyy.py.add_pythonization(
            cppyy.py.compose_method("pyzables::NakedBuffers$", "Get[XY]$", set_size))

        bsize, xval, yval = 3, 2, 5
        m = cppyy.gbl.pyzables.NakedBuffers(bsize, xval, yval)

        x = m.GetX()
        assert len(x) == bsize
        assert list(x) == list(map(lambda x: x*xval, range(bsize)))

        y = m.GetY()
        assert len(y) == bsize
        assert list(y) == list(map(lambda x: x*yval, range(bsize)))

    def test02_type_pinning(self):
        """Verify pinnability of returns"""

        import cppyy

        cppyy.gbl.pyzables.GimeDerived._creates = True

        result = cppyy.gbl.pyzables.GimeDerived()
        assert type(result) == cppyy.gbl.pyzables.MyDerived

        cppyy.py.make_interface(cppyy.gbl.pyzables.MyBase)
        assert type(result) == cppyy.gbl.pyzables.MyDerived


    def test03_transparency(self):
        """Transparent use of smart pointers"""

        import cppyy

        Countable = cppyy.gbl.pyzables.Countable
        mine = cppyy.gbl.pyzables.mine

        assert type(mine) == Countable
        assert type(mine.__smartptr__()) == cppyy.gbl.std.shared_ptr(Countable)
        assert mine.say_hi() == "Hi!"

    def test04_converters(self):
        """Smart pointer argument passing"""

        import cppyy

        pz = cppyy.gbl.pyzables
        mine = pz.mine

        pz.pass_mine_rp_ptr(mine)
        pz.pass_mine_rp_ref(mine)
        pz.pass_mine_rp(mine)

        pz.pass_mine_sp_ptr(mine)
        pz.pass_mine_sp_ref(mine)

        pz.pass_mine_sp_ptr(mine.__smartptr__())
        pz.pass_mine_sp_ref(mine.__smartptr__())

        pz.pass_mine_sp(mine)
        pz.pass_mine_sp(mine.__smartptr__())

        # TODO:
        # cppyy.gbl.mine = mine
        pz.renew_mine()

    def test05_executors(self):
        """Smart pointer return types"""

        import cppyy

        pz = cppyy.gbl.pyzables
        Countable = pz.Countable

        mine = pz.gime_mine_ptr()
        assert type(mine) == Countable
        assert type(mine.__smartptr__()) == cppyy.gbl.std.shared_ptr(Countable)
        assert mine.say_hi() == "Hi!"

        mine = pz.gime_mine_ref()
        assert type(mine) == Countable
        assert type(mine.__smartptr__()) == cppyy.gbl.std.shared_ptr(Countable)
        assert mine.say_hi() == "Hi!"

        mine = pz.gime_mine()
        assert type(mine) == Countable
        assert type(mine.__smartptr__()) == cppyy.gbl.std.shared_ptr(Countable)
        assert mine.say_hi() == "Hi!"


## actual test run
if __name__ == '__main__':
    result = run_pytest(__file__)
    sys.exit(result)
