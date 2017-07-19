""" PyPy-specific touch-ups
"""

from cppyy_backend import loader

__all__ = [
    'gbl',
    'addressof',
    'bind_object',
    'load_reflection_info',
    ]


# first load the dependency libraries of the backend, then
# pull in the built-in low-level cppyy
c = loader.load_cpp_backend()
import _cppyy as _backend     # built-in module
_backend._cpp_backend = c


#- exports -------------------------------------------------------------------
import sys
_thismodule = sys.modules[__name__]
for name in __all__:
    setattr(_thismodule, name, getattr(_backend, name))
del name, sys

# add _backend itself to exports
__all__.append('_backend')
