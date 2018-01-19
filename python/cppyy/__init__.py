""" Dynamic C++ bindings generator.
"""

import os, sys

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
sys.modules['cppyy.gbl'] = gbl
sys.modules['cppyy.gbl.std'] = gbl.std


#- enable auto-loading -------------------------------------------------------
try:    gbl.gInterpreter.EnableAutoLoading()
except: pass


#--- pythonization factories -------------------------------------------------
from . import _pythonization as py
py._set_backend(_backend)


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

def add_include_path(path):
    """Add a path to the include paths available to Cling."""
    if not os.path.isdir(path):
        raise OSError("no such directory: %s" % path)
    gbl.gInterpreter.AddIncludePath(path)

def add_autoload_map(fname):
    """Add the entries from a autoload (.rootmap) file to Cling."""
    if not os.path.isfile(fname):
        raise OSError("no such file: %s" % fname)
    gbl.gInterpreter.LoadLibraryMap(fname)

def _get_name(tt):
    if type(tt) == str:
        return tt
    try:
        ttname = tt.__cppname__
    except AttributeError:
        ttname = tt.__name__
    return ttname

_sizes = {}
def sizeof(tt):
    """Returns the storage size (in chars) of C++ type <tt>."""
    if not isinstance(tt, type) and not type(tt) == str:
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
