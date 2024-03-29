.. _numba:


Numba support
=============

.. caution::

    This is an **experimental** feature, available starting with release
    2.4.0.
    It is still incomplete (see listing below) and has only been tested on
    Linux on x86_64.

Numba `is a JIT compiler`_ for Python functions that can be statically typed
based on their input arguments.
Since C++ objects are always statically typed and already implemented at the
machine level, they can be dynamically integrated into the Numba type tracing
and lowering by exposing type details through C++ reflection at runtime.

JIT-compiling traces of mixed Python/bound C++ code reduces, and in some
cases removes, the overhead of boxing/unboxing native data into their Python
proxies and vice versa.
It can also reduce or remove temporaries, especially for template
expressions.
Thus, there can be significant speedups for mixed code, beyond the Numba
compilation of Python code itself.
The current implementation integrates compiled C++ through function pointers,
object pointers, and pointer offsets, into the intermediate representation
(IR) as generated by Numba.
A future version may integrate Cling-generated IR directly into Numba IR (or
vice versa), e.g. if the C++ code is exposed from (precompiled) headers.
This would allow inlining of C++ code into Numba traces, for further
expected speedups.


Why Numba?
----------

The advertised premise of Numba is that it "makes Python code fast."
However, there is a much more compelling reason: Numba allows developers to
stay in their chosen ecosystem, be it Python or C++, in mixed environments,
without paying for their choice in lost performance.
For example, a Python developer using Numba does not need to rewrite a kernel
into C++ just to run performantly in a C++ framework.
Similarly, a C++ developer can use Numba to compile and create function
pointers to Python code for easy, performant, access.
This becomes even more compelling if the deployment target is a GPU, which
would otherwise certainly require a rewrite of the Python code.
Add that Numba, as a JIT-compiler, is fully run-time just like ``cppyy``,
and the use case for integration is clear.
(Numba does not currently provide support for C++.)


Usage
-------

``cppyy`` does not use Numba extension hooks to minimize accidental
dependencies.
Instead, it requires that the extensions are loaded explicitly by any code
that uses it::

  import cppyy.numba_ext

After that, Numba is able to trace ``cppyy`` bound code when applying the
usual ``numba.njit`` decorator.

Numba type declarations are done lazily, with the ``numba_ext`` module only
initially registering hooks on proxy base classes, to keep overheads in
Numba's type-resolution to a minimum.
On use in a JITed trace, each C++ type or function call is refined to the
actual, concrete types and type-specific overloads, with templates
instantiated as-needed.
Where possible, lowering is kept generic to reduce the number of callbacks
in Numba's compilation chain.


Examples
--------

The following, non-exhaustive, set of examples gives an idea of the
current level of support.
More examples can be found in the `test suite`_.

C++ free (global) functions can be called and overloads will be selected, or
a template will be instantiated, based on the provided types.
Exact type matches are fully supported, there is some support for typedefs
add implicit conversions for builtin types, there is no support for
conversions of custom types or default arguments.

-  **Basic usage**: To use ``cppyy`` in Numba JITed code, simply import
   ``cppyy.numba_ext``, after which further use is transparent and the same
   as when otherwise using ``cppyy`` in Python.
   Example:

.. code-block:: python

   >>> import numba
   >>> import cppyy
   >>> import cppyy.numba_ext          # enables numba to work with cppyy
   >>> import math
   >>> @numba.jit(nopython=True)
   ... def cpp_sqrt(x):
   ...   return cppyy.gbl.sqrt(x)      # direct use, no extra setup required
   >>> print("Sqrt of 4: ", cpp_sqrt(4.0))
   Sqrt of 4: 2.0
   >>> print("Sqrt of Pi: ", cpp_sqrt(math.pi))
   Sqrt of Pi: 1.7724538509055159


-  **Overload selection**: C++ overloads provide different implementations
   for different argument  types (not to be confused with Numba overloads,
   which provide different implementations for the same argument types).
   Unfortunately, mapping of Python types to C++ types is often not exact,
   so a "best match" is chosen, similarly to what ``cppyy`` normally does.
   However, the latter, being dynamic, is more flexible.
   For example, best-match C++ integer type can be value dependent, whereas
   in the Numba trace, it is by definition fixed at JIT time.
   Example:

.. code-block:: python

   >>> cppyy.cppdef("""
   ... int mul(int x) { return x * 2; }
   ... float mul(float x) { return x * 3; }
   ... """)
   >>> @numba.jit(nopython=True)
   ... def oversel(a):
   ...   total = type(a[0])(0)
   ...   for i in range(len(a)):
   ...      total += cppyy.gbl.mul(a[i])
   ...   return total

   >>> a = np.array(range(10), dtype=np.float32)
   >>> print("Array: ", a)
   Array: [0. 1. 2. 3. 4. 5. 6. 7. 8. 9.]
   >>> print("Overload selection output: ", oversel(a))
   Overload selection output: 135.0
   >>> a = np.array(range(10), dtype=np.int32)
   >>> print("Array: ", a)
   Array: [0 1 2 3 4 5 6 7 8 9]
   >>> print("Overload selection output: ", oversel(a))
   Overload selection output: 90

-  **Template instantiation**: templates are instantiated as needed as part
   of the overload selection.
   The best match is done for the arguments provided at the point of first
   use.
   If those arguments vary based on program input, it may make sense to
   provide Numba with type hints and pre-compile such functions.
   Example:

.. code-block:: python

   >>> import cppyy
   >>> import cppyy.numba_ext
   >>> import numba
   >>> import numpy as np
   >>> cppyy.cppdef("""
   ... template<typename T>
   ... T square(T t) { return t*t; }
   ... """)
   >>> @numba.jit(nopython=True)
   ... def tsa(a):
   ...   total = type(a[0])(0)
   ...   for i in range(len(a)):
   ...      total += cppyy.gbl.square(a[i])
   ...   return total
   >>> a = np.array(range(10), dtype=np.float32)
   >>> print("Float array: ", a)
   Float array: [0. 1. 2. 3. 4. 5. 6. 7. 8. 9.]
   >>> print("Sum of squares: ", tsa(a))
   Sum of squares: 285.0
   >>> print()
   >>> a = np.array(range(10), dtype=np.int32)
   >>> print("Integer array: ", a)
   Integer array: [0 1 2 3 4 5 6 7 8 9]
   >>> print("Sum of squares: ", tsa(a))
   Sum of squares: 285


Instances of C++ classes can be passed into Numba traces.
They can be returned from functions called *within* the trace, but cannot yet
be returned *from* the trace.
Their public data is accessible (read-only) if of built-in type and their
public methods can be called, for which overload selection works.
Example:

.. code-block:: python

   >>> import cppyy
   >>> import numba
   >>> import numpy as np
   >>> 
   >>> cppyy.cppdef("""\
   ... class MyData {
   ... public:
   ...     MyData(int i, int j) : fField1(i), fField2(j) {}
   ...
   ... public:
   ...     int get_field1() { return fField1; }
   ...     int get_field2() { return fField2; }
   ...
   ...     MyData copy() { return *this; }
   ...
   ... public:
   ...     int fField1;
   ...     int fField2;
   ... };""")
   True
   >>> @numba.jit(nopython=True)
   >>> def tsdf(a, d):
   ...     total = type(a[0])(0)
   ...     for i in range(len(a)):
   ...         total += a[i] + d.fField1 + d.fField2
   ...     return total
   ...
   >>> d = cppyy.gbl.MyData(5, 6)
   >>> a = np.array(range(10), dtype=np.int32)
   >>> print(tsdf(a, d))
   155
   >>> # example of method calls
   >>> @numba.jit(nopython=True)
   >>> def tsdm(a, d):
   ...     total = type(a[0])(0)
   ...     for i in range(len(a)):
   ...         total += a[i] +  d.get_field1() + d.get_field2()
   ...     return total
   ...
   >>> print(tsdm(a, d))
   155
   >>> # example of object return by-value
   >>> @numba.jit(nopython=True)
   >>> def tsdcm(a, d):
   ...     total = type(a[0])(0)
   ...     for i in range(len(a)):
   ...         total += a[i] + d.copy().fField1 + d.get_field2()
   ...     return total
   ...
   >>> print(tsdcm(a, d))
   155
   >>>


Demo: Numba physics example
---------------------------

Motivating example taken from:
`numba_scalar_impl.py <https://github.com/numba/numba-examples/blob/master/examples/physics/lennard_jones/numba_scalar_impl.py>`_

.. code-block:: python

   >>> import numba
   >>> import cppyy
   >>> import cppyy.numba_ext
   ...
   >>> cppyy.cppdef("""
   ... #include <vector>
   ... struct Atom {
   ...    float x;
   ...    float y;
   ...    float z;
   ... };
   ...
   ... std::vector<Atom> atoms = {{1, 2, 3}, {2, 3, 4}, {3, 4, 5}, {4, 5, 6}, {5, 6, 7}};
   ... """)
   ...
   >>> @numba.njit
   >>> def lj_numba_scalar(r):
   ...    sr6 = (1./r)**6
   ...    pot = 4.*(sr6*sr6 - sr6)
   ...    return pot

   >>> @numba.njit
   >>> def distance_numba_scalar(atom1, atom2):
   ...    dx = atom2.x - atom1.x
   ...    dy = atom2.y - atom1.y
   ...    dz = atom2.z - atom1.z
   ...
   ...    r = (dx * dx + dy * dy + dz * dz) ** 0.5
   ...
   ...    return r
   ...
   >>> def potential_numba_scalar(cluster):
   ...    energy = 0.0
   ...    for i in range(cluster.size() - 1):
   ...       for j in range(i + 1, cluster.size()):
   ...           r = distance_numba_scalar(cluster[i], cluster[j])
   ...           e = lj_numba_scalar(r)
   ...       energy += e
   ...
   ...    return energy
   ...
   >>> print("Total lennard jones potential =", potential_numba_scalar(cppyy.gbl.atoms))
   Total lennard jones potential = -0.5780277345740283


Overhead
--------

The main overhead of JITing Numba traces is in the type annotation in Numba
itself, optimization of the IR and assembly by the backend less so.
(There is also a non-negligible cost to Numba initialization, which is why
``cppyy`` does not provide automatic extension hooks.)
The use of ``cppyy`` bound C++, which relies on the same Numba machinery,
does not change that, since the reflection-based lookups are in C++ and
comparatively very fast.
For example, there is no appreciable difference in wall clock time to JIT a
trace using Numba's included math functions (from module ``math`` or
``numpy``) or one that uses C++ bound ones whether from the standard library
or a templated versions from e.g. Eigen.
Use of very complex template expressions may change this balance, but in
principle, wherever it makes sense in the first place to use Numba JITing, it
is also fine, performance-wise, to use ``cppyy`` bound C++ inside the trace.

A second important overhead is in unboxing Python proxies of C++ objects,
in particular when passed as an argument to a Numba-JITed function.
The main costs are in the lookup (types are matched at every invocation) and
to a lesser extent the subsequent copying of the instance data.
Thus, functions that take a C++ object as an argument will require more time
spent in the function body for JITing to be worth it than functions that do
not.

The current implementation invokes C++ callables through function pointers
and accesses data through offsets calculations from the object's base
address.
A future implementation may be able to inline C++ into the Numba trace if
code is available in headers files or was JITed.


Further Information
-------------------

-  Numba documentation:
   `numba.readthedocs.io <https://numba.readthedocs.io/en/stable/user/index.html>`_.

-  "Using C++ From Numba, Fast and Automatic", presented at `PyHEP 2022 <https://compiler-research.org/presentations/#CppyyNumbaPyHEP2022>`_

   - `PyHEP 2022 video <https://www.youtube.com/watch?v=RceFPtB4m1I>`_
   - `PyHEP 2022 slides <https://compiler-research.org/assets/presentations/B_Kundu-PyHEP22_Cppyy_Numba.pdf>`_
   - `PyHEP 2022 notebook <https://github.com/sudo-panda/PyHEP-2022>`_

-  Presentation at CERN's ROOT Parallelism, Performance and Programming Model
   (`PPP <https://indico.cern.ch/event/1196174/>`_) Meeting

   - `PPP slides <https://indico.cern.ch/event/1196174/contributions/5028203/attachments/2501253/4296778/PPP.pdf>`_
   - `PPP notebook <https://indico.cern.ch/event/1196174/contributions/5028203/attachments/2501253/4296735/PPP.ipynb>`_


Acknowledgements
----------------

This work is supported in part by the `Compiler Research Organization`_
(Princeton University), with contributions from
`Vassil Vassilev <https://github.com/vgvassilev>`_,
`Baidyanath Kundu <https://github.com/sudo-panda>`_, and
`Aaron Jomy <https://github.com/maximusron>`_.


.. _is a JIT compiler: https://numba.pydata.org/

.. _test suite: https://github.com/wlav/cppyy/blob/master/test/test_numba.py

.. _Compiler Research Organization: https://compiler-research.org/
