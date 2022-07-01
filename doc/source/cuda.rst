.. _cuda:


CUDA support
============

.. warning::

    This is an **experimental** feature, available starting with release
    2.3.0.
    It is still incomplete and has only been tested on Linux on x86_64.

CUDA is supported by passing all JITed code through two pipelines: one for the
CPU and one for the GPU.
Use of the ``__CUDA__`` pre-processor macro enables more fine-grained control
over which pipeline sees what, which is used e.g. in the pre-compiled header:
the GPU pipeline has the CUDA headers included, the CPU pipeline does not.
Building the pre-compiled header will also pick up common CUDA libraries such
as cuBLAS, if installed.

Each version of CUDA requires specific versions of Clang and the system
compiler (e.g. gcc) for proper functioning.
Since Cling as used by ``cppyy`` is still running Clang9 (work on the port to
Clang13 is on-going) and since CUDA has changed the APIs for launching kernels
in v11, the latest supported version of CUDA is v10.2.
This is also the default for the binary distribution; use of a different
version of CUDA (older than v10.2) will work but does require rebuilding
``cppyy-cling`` from source.

There are three environment variables to control Cling's handling of CUDA:

* ``CLING_ENABLE_CUDA`` (required): set to ``1`` to enable the CUDA
  backend.

* ``CLING_CUDA_PATH`` (optional): set to the local CUDA installation if not
  in a standard location.

* ``CLING_CUDA_ARCH`` (optional): set the architecture to target; default is
  ``sm_35`` and Clang9 is limited to ``sm_75``.

After enabling CUDA with ``CLING_ENABLE_CUDA=1`` CUDA code can be used and
kernels can be launched from JITed code by in ``cppyy.cppdef()``.
There is currently no syntax or helpers yet to launch kernels from Python.
