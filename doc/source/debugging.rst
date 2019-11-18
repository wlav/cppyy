.. _debugging:
   
Debugging
=========

By default, the ``clang`` JIT as used by cppyy does not generate debugging
information.
This is because in a production setting this information, being internal to
the wrapper generation, goes unused.
However, that does mean that a debugger that starts from python, will not be
able to step through JITed code into the C++ function that needs debugging,
even when that function's code itself contains debugging information.
   
To enable debugging information in JITed code, set the ``EXTRA_CLING_ARGS``
envar to ``-g`` (and any further compiler options you need, e.g. add ``-O2``
to debug optimized code).

It is also useful to have a traceback through the Python code that led to the
problem in C++.
Many modern debuggers allow mixed-mode C++/Python debugging (for example
`gdb`_ and `MSVC`_), but cppyy can also turn abortive C++ signals (such as a
segmentation violation) into Python exceptions, yielding a traceback.
This is particularly useful when working with cross-inheritance and other
cross-language callbacks.

To enable the signals to exceptions conversion, import the lowlevel module
``cppyy.ll`` and use:

  .. code-block:: python

    import cppyy.ll
    cppyy.ll.set_signals_as_exception(True)

Call ``set_signals_as_exception(False)`` to disable the conversion again.
It is recommended to only have the conversion enabled around the problematic
code, as it comes with a performance penalty.
For convenient scoping, you can also use:

  .. code-block:: python

    with cppyy.ll.signals_as_exception():
        # crashing code goes here

The translation of signals to exceptions is as follows (all of the exceptions
are subclasses of ``cppyy.ll.FatalError``):

========================================  ========================================
C++ signal                                Python exception
========================================  ========================================
``SIGSEGV``                               ``cppyy.ll.SegmentationViolation``
``SIGBUS``                                ``cppyy.ll.BusError``
``SIGABRT``                               ``cppyy.ll.AbortSignal``
``SIGILL``                                ``cppyy.ll.IllegalInstruction``
========================================  ========================================


.. _`gdb`: https://wiki.python.org/moin/DebuggingWithGdb
.. _`MSVC`: https://docs.microsoft.com/en-us/visualstudio/python/debugging-mixed-mode-c-cpp-python-in-visual-studio
