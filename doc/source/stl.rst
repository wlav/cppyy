.. _stl:


STL
===

The Standard Template Library (STL), and in particular its container types,
are the de facto equivalents of Python's builtin containers, even as they are
not themselves C++ builtins, but regular classes written in the C++ language.
Python proxies of these classes would be fully functional as-is, but they
are made more useful by giving them pythonistic features, so that they can
be dropped into places where Python builtin containers are expected (for
example, in for-loops).

There are two extremes to achieve this drop-in behavior: always copy
containers, so that you actual deal with true Python objects; or adjust their
interfaces to be the same as their Python equivalents.
Neither is very satisfactory: the former is not because of the existence of
global/static variables and return-by-reference.
If only a copy is available, then expected modifications do not propagate.
Copying is also either slow (when copying every time) or memory intensive (if
the results are cached).
Filling out the interfaces is more appealing, but all operations then involve
C++ function calls which may be slower than the Python equivalents.

Given that neither method will satisfy all cases, ``cppyy`` aims to maximize
functionality and minimum surprises based on common use.
Thus, for example, ``std::vector`` grows a pythonistic ``__len__`` method,
but does not lose its C++ ``size`` method.
Passing a Python container through a const reference to a ``std::vector``
will trigger automatic conversion, but an attempt through a non-const
reference will fail.
``std::string`` is almost always converted to Python's ``str`` on function
returns (the exception is return-by-reference when assigning), but not when
its direct use is more likely such as in the case of variables or when
iterating over a ``std::vector<std::string>``.

The rest of this section shows examples of how STL containers can be used in
a natural, pythonistic, way.


`vector`
--------

A ``std::vector`` is the most common C++ container type because it is more
efficient and performant than specialized types such as ``list`` and
``map``, unless the number of elements gets very large.
Python has several similar types, from the builtin ``tuple`` and ``list``,
the ``array`` from builtin module ``array``, to ``numpy.ndarray``.
A vector is more like the latter in that it can contain only one type, but
more like the former in that it can contain objects.
In practice, it can interplay well with all these containers, but e.g.
efficiency and performance can differ significantly.

A vector can be instantiated from any sequence, including generators, and
vectors of objects can be recursively constructed:

  .. code-block:: python

    >>> from cppyy.gbl.std import vector, pair
    >>> v = vector[int](range(10))
    >>> len(v)
    10
    >>> vp = vector[pair[int, int]](((1, 2), (3, 4)))
    >>> len(vp)
    2
    >>> vp[1][0]
    3
    >>>

To extend a vector with another sequence object, use ``+=``:

  .. code-block:: python

    >>> v += range(10, 20)
    >>> len(v)
    20
    >>>
    
The easiest way to print the full contents of a vector, is by using a list
and printing that instead.
Indexing and slicing of a vector follows the normal Python rules:

  .. code-block:: python

    >>> v[1]
    1
    >>> v[-1]
    19
    >>> v[-4:]
    <cppyy.gbl.std.vector<int> object at 0x7f9051057650>
    >>> list(v[-4:])
    [16, 17, 18, 19]
    >>>

The usual iteration operations work on vector, but the C++ rules still apply,
so a vector that is being iterated over can not be modified in the loop body.
(On the plus side, this makes it much faster to iterate over a vector than,
say, a numpy ndarray.)

  .. code-block:: python

    >>> for i in v[2:5]:
    ...     print(i)
    ...
    2
    3
    4
    >>> 2 in v
    True
    >>> sum(v)
    190
    >>>

