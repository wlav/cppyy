.. _philosophy:

Philosophy
==========

.. toctree::
   :hidden:

As a Python-C++ language binder, cppyy has several unique features: it fills
gaps and covers use cases not available through other binders.
This document explains some of the design choices made and the thinking
behind the implementations of those features.
Its purpose is to help you decide whether cppyy covers your use cases and
binding requirements.


Run-time v.s. compile-time
--------------------------

What performs better, run-time or compile-time?
The obvious answer is compile-time: see the performance differences between
C++ and Python, for example.
Obvious, but completely wrong however.
In fact, when it comes to Python, it is even the `wrong question.`

Everything in Python is run-time: modules, classes, functions, etc. are all
run-time constructs.
A Python module that defines a class is a set of instructions to the Python
interpreter that lead to the construction of the desired class object.
A C/C++ extension module that defines a class does the same thing by calling
a succession of Python interpreter Application Programming Interfaces (APIs;
the exact same that Python uses itself internally).
If you use a compile-time binder such as `SWIG`_ or `pybind11`_ to bind a C++
class, then what gets compiled is the series of API calls necessary to
construct a Python-side equivalent at `run-time` (when the module gets
loaded), not the Python class object.
In short, whether a binding is created at "compile-time" or at run-time has
no measurable bearing on performance.

What does affect performance is the overhead to cross the language barrier.
This consists of unboxing Python objects to extract or convert the underlying
objects or data to something that matches what C++ expects; overload
resolution based on the unboxed arguments; offset calculations; and finally
the actual dispatch.
As a practical matter, overload resolution is the most costly part, followed
by the unboxing and conversion.
Best performance is achieved by specialization of the paths through the
run-time: recognize early the case at hand and select an optimized path.
For that reason, `PyPy`_ is so fast: JIT-ed traces operate on unboxed objects
and resolved overloads are baked into the trace, incurring no further cost.
Similarly, this is why pybind11 is so slow: its code generation is the C++
compiler's template engine, so complex path selection and specialization is
very hard to do in a performance-portable way.

In cppyy, a great deal of attention has gone into built-in specialization
paths, which drives its performance.
For example, basic inheritance sequentially lines up classes, whereas
multiple (virtual) inheritance usually requires thunks.
Thus, when calling base class methods on a derived instance, the latter
requires offset calculations that depend on that instance, whereas the former
has fixed offsets fully determined by the class definitions themselves.
By labeling classes appropriately, single inheritance classes (by far the
most common case) do not incur the overhead in PyPy's JIT-ed traces that is
otherwise  unavoidable for multiple virtual inheritance.
As another example, consider that the C++ standard does not allow modifying
a ``std::vector`` while looping over it, whereas Python has no such
restriction, complicating loops.
Thus, cppyy has specialized ``std::vector`` iteration for both PyPy and
CPython, easily outperforming looping over an equivalent numpy array.

In CPython, the performance of `non-overloaded` function calls depends
greatly on the Python interpreter's internal specializations; and Python3
has many specializations specific to basic extension modules (C function
pointer calls), gaining a performance boost of more than 30% over Python2.
Only since Python3.8 is there also better support for closure objects (vector
calls) as cppyy uses, to short-cut through the interpreter's own overhead.

As a practical consideration, whether a binder performs well on code that you
care about, depends `entirely` on whether it has the relevant specializations
for your most performance-sensitive use cases.
The only way to know for sure is to write a test application and measure, but
a binder that provides more specializations, or makes it easy to add your
own, is more likely to deliver.


`LLVM dependency`
-----------------

cppyy depends on `LLVM`_, through Cling.
LLVM is properly internalized, so that it doesn't conflict with other uses;
and in particular it is fine to mix `Numba`_ and cppyy code.
It does mean a download cost of about 20MB for the binary wheel (exact size
differs per platform) on installation, and additional `primarily initial`
memory overheads at run-time.
Whether this is onerous depends strongly not only on the application, but
also on the rest of the software stack.

The initial cost of loading cppyy, and thus starting the Cling interpreter,
is about 45MB (platform dependent).
Initial uses of standard (e.g. STL) C++ results in deserialization of the
precompiled header at another eventual total cost of about 25MB (again,
platform dependent).
The actual bindings of course also carry overheads.
As a rule of thumb, you should budget for ~100MB all-in for the overhead
caused by the bindings.

Other binders do not have this initial memory overhead, but do of course
occur an overhead per module, class, function, etc.
At scale, however, cppyy has some advantages: all binding is lazy (including
the option of automatic loading), standard classes are never duplicated, and
there is no additional "per-module" overhead.
Thus, eventually (depending on the number of classes bound, across how many
modules, what use fraction, etc.), this initial cost is recouped when
compared to other binders.
As a rule of thumb, if about 10% of classes are used, it takes several
hundreds of bound classes before the cppyy-approach is beneficial.
In High Energy Physics, from which it originated, cppyy is regularly used in
software stacks of many thousands of classes, where this advantage is very
important.


`Large deployment`
------------------

The single biggest headache in maintaining an installation of Python
extension modules is that Python patch releases can break them.
The two typical solutions are to either restrict the choice of Python
interpreter and version that are supported (common in HPC) or to provide
binaries (wheels) for a large range of different interpreters and versions
(as e.g. done for conda).

In the case of cppyy, only CPython/CPyCppyy and PyPy/_cppyy (an internal
module) depend on the Python interpreter (see:
:ref:`Package Structure <package-structure>`).
The user-facing ``cppyy`` module is pure Python and the backend (Cling) is
Python-independent.
Most importantly, since all bindings are generated at run-time, there are no
extension modules to regenerate and/or recompile.

Thus, the end-user only needs to rebuild/reinstall CPyCppyy for each relevant
version of Python (and nothing extra is needed for PyPy) to switch Python
versions and/or interpreter.
The rest of the software stack remains completely unchanged.
Only if Cling in cppyy's backend is updated, which happens infrequently, and
non-standard precompiled headers or modules are used, do these need to be
rebuild in full.


.. _`SWIG`: http://swig.org/
.. _`pybind11`: https://pybind11.readthedocs.io/en/stable/
.. _`PyPy`: https://www.pypy.org/
.. _`LLVM`: https://llvm.org/
.. _`Numba`: http://numba.pydata.org/
