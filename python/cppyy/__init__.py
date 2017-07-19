""" Dynamic C++ bindings generator.
"""

try:
    import __pypy__
    from ._pypy_cppyy import *
    del __pypy__
except ImportError:
    from ._python_cppyy import *


#- allow importing from gbl --------------------------------------------------
import sys
sys.modules['cppyy.gbl'] = gbl
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
    gbl.gInterpreter.Declare(src)
