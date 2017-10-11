Installation
============

The ``cppyy`` module and its dependencies are available through `PyPI`_ for
both CPython (2 and 3) and PyPy (5.9.0 and later).
Build-time only dependencies are ``cmake`` (for general build), ``python2.7``
(for LLVM), and a modern C++ compiler (one that supports at least C++11).

Compilation of the backend, which contains a customized version of
Clang/LLVM, can take a long time, so it is recommended to set the MAKE_NPROCS
environment variable to the number of cores available on your machine or more.
To see progress, use ``--verbose``::

 $ MAKE_NPROCS=32 pip install --verbose cppyy

The bdist_wheel of the backend is reused by pip for all versions of CPython
and PyPy, thus the long compilation is needed only once.
Prepared wheels of cppyy-cling (which contains LLVM) for Mac 10.12 and
Linux/Gentoo `are available`_.
To use them, tell ``pip``::

 $  pip install --extra-index https://cern.ch/wlav/wheels cppyy

PyPy 5.7 and 5.8 have a built-in module ``cppyy``.
You can still install the ``cppyy`` package, but the built-in module takes
precedence.
To use ``cppyy``, first import a compatibility module::

 $ pypy
 [PyPy 5.8.0 with GCC 5.4.0] on linux2
 >>>> import cppyy_compat, cppyy
 >>>>

You will have to set ``LD_LIBRARY_PATH`` appropriately if you get an
``EnvironmentError`` (it will indicate the needed directory).

Note that your python interpreter (whether CPython or ``pypy-c``) may not have
been linked by the C++ compiler.
This can lead to problems during loading of C++ libraries and program shutdown.
In that case, re-linking is highly recommended.

Older versions of PyPy (5.6.0 and earlier) have a built-in ``cppyy`` based on
`Reflex`_, which is less feature-rich and no longer supported.
However, both the :doc:`distribution tools <distribution>` and user-facing
Python codes are very backwards compatible.

.. _`PyPI`: https://pypi.python.org/pypi/cppyy/
.. _`are available`: https://cern.ch/wlav/wheels/
.. _`Reflex`: https://root.cern.ch/how/how-use-reflex


Package structure
-----------------
.. _package-structure:

There are four PyPA packages involved in a full installation, with the
following structure::

               (A) _cppyy (PyPy)
           /                        \
 (1) cppyy                            (3) cling-backend -- (4) cppyy-cling
           \                        /
             (2) CPyCppyy (CPython)

The user-facing package is always ``cppyy`` (1).
It is used to select the other (versioned) required packages, based on the
python interpreter for which it is being installed.

Below (1) follows a bifurcation based on interpreter.
This is needed for functionality and performance: for CPython, there is the
CPyCppyy package (2).
It is written in C++, makes use of the Python C-API, and installs as a Python
extension module.
For PyPy, there is the builtin module ``_cppyy`` (A).
This is not a PyPA package.
It is written in RPython as it needs access to low-level pointers, JIT hints,
and the ``_cffi_backend`` backend module (itself builtin).

Shared again across interpreters is the backend, which is split in a small
wrapper (3) and a large package that contains Cling/LLVM (4).
The former is still under development and expected to be updated frequently.
It is small enough to download and build very quickly.
The latter, however, takes a long time to build, but since it is very stable,
splitting it if off allows the creation of binary wheels that need updating
only infrequently (expected about twice a year).

All code is publicly available; see the
:doc:`section on repositories <repositories>`.
