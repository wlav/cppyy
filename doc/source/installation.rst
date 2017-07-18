Installation
============

The installation instructions depend on whether you install for PyPy or
CPython.
The former has a builtin cppyy module, and thus only requires the backend.
The latter needs both cppyy and the backend.
Compiling the backend takes a long time (it contains a customized version
of Clang/LLVM), so it is recommended to set the MAKE_NPROCS environment
variable to the number of cores available on your machine.


PyPy
----

This assumes PyPy2.7 v5.7 or later; earlier versions use a Reflex-based cppyy
module, which is no longer supported.
Both the tooling and user-facing Python codes are however very backwards
compatible.
Further build dependencies are cmake (for general build), Python2.7 (for LLVM),
and a modern C++ compiler (one that supports at least C++11).

Install for PyPy, using pip::

 $ MAKE_NPROCS=8 pypy-c -m pip install --verbose PyPy-cppyy-backend

Set the number of parallel builds ('8' in this example) to a number appropriate
for your machine.
The use of --verbose is recommended so that you can see the build progress.


CPython
-------

Both Python2 and Python3 are supported.
Further build dependencies are cmake (for general build), Python2.7 (for LLVM),
and a modern C++ compiler (supporting at least C++11).

Install using pip::

 $ MAKE_NPROCS=8 pip install --verbose CPyCppyy

Set the number of parallel builds ('8' in this example) to a number appropriate
for your machine.
Installing CPyCppyy will pull in PyPy-cppyy-backend, which does not depend Python
and can thus be shared between PyPy and CPython by installing it in a common
location.


Running environment
-------------------

The default installation of the backend will be under
$PYTHONHOME/site-packages/cppyy_backend/lib,
which needs to be added to your dynamic loader path (LD_LIBRARY_PATH).
If you need the dictionary and class map generation
:doc:`tools <distribution>`, you need to add
$PYTHONHOME/site-packages/cppyy_backend/bin to your executable path (PATH).

