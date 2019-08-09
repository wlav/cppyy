""" Externally provided types: get looked up if all else fails, e.g.
    for typedef-ed C++ builtin types.
"""

import sys

def _create_mapper(cls):
    def mapper(name, scope):
        if scope:
            cppname = scope+'::'+name
            modname = 'cppyy.gbl.'+scope
        else:
            cppname = name
            modname = 'cppyy.gbl'
        return type(name, (cls,), {'__cpp_name__' : cppname, '__module__' : modname})
    return mapper

class _Bool(object):
    def __init__(self, val = bool()):
        if val: self.val = True
        else: self.val = False

    def __nonzero__(self):
        return self.val

    def __bool__(self):
        return self.val

    def __eq__(self, other):
        if self: return other == True
        return other == False

    def __repr__(self):
        if self.val: return repr(True)
        else: return repr(False)


def initialize(backend):
    if not hasattr(backend, 'type_map'):
        return

    tm = backend.type_map

    # boolean type (builtin type bool can nog be subclassed)
    tm['bool'] = _create_mapper(_Bool)

    # char types
    str_tm = _create_mapper(str)
    for tp in ['char', 'unsigned char', 'signed char']:
        tm[tp] = str_tm
    if sys.hexversion < 0x3000000:
        tm['wchar_t'] = _create_mapper(unicode)
    else:
        tm['wchar_t'] = str_tm

    # integer types
    int_tm = _create_mapper(int)
    for tp in ['short', 'unsigned short', 'int']:
        tm[tp] = int_tm

    if sys.hexversion < 0x3000000:
        long_tm = _create_mapper(long)
    else:
        long_tm = tm['int']
    for tp in ['unsigned int', 'long', 'unsigned long', 'long long', 'unsigned long long']:
        tm[tp] = long_tm

    # floating point types
    float_tm = _create_mapper(float)
    for tp in ['float', 'double', 'long double']:
        tm[tp] = float_tm
