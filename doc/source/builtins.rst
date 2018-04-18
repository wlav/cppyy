.. _builtins:

Builtins
========

C++ has a far richer set of builtin types than Python.
Most Python code can remain relatively agnostic to that, and ``cppyy``
provides automatic conversions as appropriate.
On the other hand, Python builtin types such as lists and maps are far
richer than any builtin types in C++.
These are mapped to their Standard Template Library equivalents instead.

The C++ code used for the examples below can be found
:doc:`here <cppyy_features_header>`, and it is assumed that that code is
loaded at the start of any session.
Download it, save it under the name ``features.h``, and load it:

  .. code-block:: python

    >>> import cppyy
    >>> cppyy.include('features.h')
    >>>


Most builtin data types map onto the expected equivalent Python types, with
the caveats that there may be size differences, different precision or
rounding.
For example, a C++ ``float`` is returned as a Python ``float``, which is in
fact a C++ ``double``.
If sizes allow, conversions are automatic.
For example, a C++ ``unsigned int`` becomes a Python ``long``, but
unsigned-ness is still honored:

  .. code-block:: python

    >>> type(cppyy.gbl.gUint)
    <type 'long'>
    >>> cppyy.gbl.gUint = -1
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: cannot convert negative integer to unsigned
    >>>

Builtin arrays are supported by through arrays from module ``array`` (or any
other builtin-type array that implements the Python buffer interface).
Out-of-bounds checking is limited to those cases where the size is known at
compile time.
Example:

  .. code-block:: python

    >>> from cppyy.gbl import Concrete
    >>> from array import array
    >>> c = Concrete()
    >>> c.array_method(array('d', [1., 2., 3., 4.]), 4)
    1 2 3 4
    >>> c.m_data[4] # static size is 4, so out of bounds
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    IndexError: buffer index out of range
    >>>

When the C++ code takes a pointer or reference type to a specific builtin
type (such as an ``unsigned int`` for example), then types need to match
exactly.
``cppyy`` supports the types provided by the standard modules ``ctypes`` and
``array`` for those cases.

