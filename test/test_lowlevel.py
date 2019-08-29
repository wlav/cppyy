import py, os, sys
from pytest import raises


class TestLOWLEVEL:
    def setup_class(cls):
        import cppyy

    def test01_builtin_casts(self):
        """Test casting of builtin types"""

        import cppyy
        from cppyy import ll

        for cast in (ll.cast, ll.static_cast):
            assert type(cast[float](1)) == float
            assert cast[float](1) == 1.

            assert type(cast[int](1.1)) == int
            assert cast[int](1.1) == 1

        assert len(ll.reinterpret_cast['int*'](0)) == 0
        raises(ReferenceError, ll.reinterpret_cast['int*'](0).__getitem__, 0)
