""" Dynamic C++ bindings generator.
"""

try:
    import __pypy__
    del __pypy__
    ispypy = True
except ImportError:
    ispypy = False

if ispypy:
    from ._pypy_cppyy import *
else:
    from ._cpython_cppyy import *


#- allow importing from gbl --------------------------------------------------
import sys
sys.modules['cppyy.gbl'] = gbl
sys.modules['cppyy.gbl.std'] = gbl.std
del sys


#- enable auto-loading -------------------------------------------------------
try:    gbl.gInterpreter.EnableAutoLoading()
except: pass


#--- pythonization factories -------------------------------------------------
from . import _pythonization
_pythonization._set_backend(_backend)
from ._pythonization import *
del _pythonization


#--- CFFI style interface ----------------------------------------------------
def cppdef(src):
    """Declare C++ source <src> to Cling.

Example:

cppyy.cppdef(
\"\"\"class MyClass {
   public:
      MyClass(int i) : m_data(i) {
      int m_data;
   };\"\"\"
)"""
    gbl.gInterpreter.Declare(src)

def include(header):
    """Load (and JIT) header file <header> into Cling."""
    gbl.gInterpreter.ProcessLine('#include "%s"' % header)

def _get_name(tt):
    try:
        ttname = tt.__cppname__
    except AttributeError:
        ttname = tt.__name__
    return ttname

_sizes = {}
def sizeof(tt):
    """Returns the storage size (in chars) of C++ type <tt>."""
    if not isinstance(tt, type):
        tt = type(tt)
    try:
        return _sizes[tt]
    except KeyError:
        sz = gbl.gInterpreter.ProcessLine("sizeof(%s);" % (_get_name(tt),))
        _sizes[tt] = sz
        return sz

_typeids = {}
def typeid(tt):
    """Returns the C++ runtime type information for type <tt>."""
    if not isinstance(tt, type):
        tt = type(tt)
    try:
        return _typeids[tt]
    except KeyError:
        tidname = 'typeid_'+str(len(_typeids))
        gbl.gInterpreter.ProcessLine(
            "namespace _cppyy_internal { auto* %s = &typeid(%s); }" %\
            (tidname, _get_name(tt),))
        tid = getattr(gbl._cppyy_internal, tidname)
        _typeids[tt] = tid
        return tid
