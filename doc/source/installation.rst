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

PyPy 5.7 and 5.8 have a built-in module ``cppyy``.
You can still install the ``cppyy`` package (or, alternatively, just
``cppyy-backend``), but the built-in takes precedence.
To use ``cppyy`` without further setting environment variables, simply load
the backend explicitly, before importing ``cppyy``::

 $ pypy
 [PyPy 5.8.0 with GCC 5.4.0] on linux2
 >>>> from cppyy_backend import loader
 >>>> c = loader.load_cpp_backend()
 >>>> import cppyy
 >>>>

Older versions of PyPy (5.6.0 and earlier) have a built-in ``cppyy`` based on
`Reflex`_, which is less feature-rich and no longer supported.
However, both the :doc:`distribution tools <distribution>` and user-facing
Python codes are very backwards compatible.

.. _`PyPI`: https://pypi.python.org/pypi/cppyy/
.. _`Reflex`: https://root.cern.ch/how/how-use-reflex
