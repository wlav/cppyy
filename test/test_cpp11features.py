import py, os, sys
from pytest import raises
from .support import setup_make

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("cpp11featuresDict.so"))

def setup_module(mod):
    setup_make("cpp11featuresDict.so")


class TestCPP11FEATURES:
    def setup_class(cls):
        cls.test_dct = test_dct
        import cppyy
        cls.datatypes = cppyy.load_reflection_info(cls.test_dct)
        cls.N = cppyy.gbl.N

    def test01_shared_ptr(self):
        """Usage and access of std::shared_ptr<>"""

        from cppyy.gbl import TestSharedPtr, create_shared_ptr_instance

      # proper memory accounting
        assert TestSharedPtr.s_counter == 0

        ptr1 = create_shared_ptr_instance()
        assert ptr1
        assert not not ptr1
        assert TestSharedPtr.s_counter == 1

        ptr2 = create_shared_ptr_instance()
        assert ptr2
        assert not not ptr2
        assert TestSharedPtr.s_counter == 2

        del ptr2
        import gc; gc.collect()
        assert TestSharedPtr.s_counter == 1

        del ptr1
        gc.collect()
        assert TestSharedPtr.s_counter == 0

    def test02_nullptr(self):
        """Allow the programmer to pass NULL in certain cases"""
      
        import cppyy

      # test existence
        nullptr = cppyy.nullptr

      # TODO: test usage ...
 
    def test03_move(self):
        """Move construction, assignment, and methods"""

        import cppyy

        def moveit(T):
            from cppyy.gbl import std

          # move constructor
            i1 = T()
            assert T.s_move_counter == 0

            i2 = T(i1)  # cctor
            assert T.s_move_counter == 0

            i3 = T(T()) # should call move, not memoized cctor
            assert T.s_move_counter == 1

            i4 = T(std.move(i1))
            assert T.s_move_counter == 2

          # move assignment
            i4.__assign__(i2)
            assert T.s_move_counter == 2

            i4.__assign__(T())
            assert T.s_move_counter == 3

            i4.__assign__(std.move(i2))
            assert T.s_move_counter == 4

      # order of moving and normal functions are reversed in 1, 2, for
      # overload resolution testing
        moveit(cppyy.gbl.TestMoving1)
        moveit(cppyy.gbl.TestMoving2)
