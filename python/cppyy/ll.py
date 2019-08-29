""" Low-level utilities, to be used for "emergencies only".
"""

import cppyy


__all__ = [
    'cast',
    'static_cast',
    'reinterpret_cast',
    'dynamic_cast',
    ]


# create low-level casting helpers
cppyy.cppdef("""namespace __cppyy_internal {
    template<typename T, typename U>
    T cppyy_cast(U val) { return (T)val; }

    template<typename T, typename U>
    T cppyy_static_cast(U val) { return static_cast<T>(val); }

    template<typename T, typename U>
    T cppyy_reinterpret_cast(U val) { return reinterpret_cast<T>(val); }

    template<typename T, typename S>
    T* cppyy_dynamic_cast(S* obj) { return dynamic_cast<T*>(obj); }
}""")


# import casting helpers
cast             = cppyy.gbl.__cppyy_internal.cppyy_cast
static_cast      = cppyy.gbl.__cppyy_internal.cppyy_static_cast
reinterpret_cast = cppyy.gbl.__cppyy_internal.cppyy_reinterpret_cast
dynamic_cast     = cppyy.gbl.__cppyy_internal.cppyy_dynamic_cast
