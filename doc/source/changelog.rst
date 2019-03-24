.. _changelog:

Changelog
=========

For convenience, this changelog keeps tracks of changes with version numbers
of the main cppyy package, but many of the actual changes are in the lower
level packages, which have their own releases.
See :doc:`packages <packages>`, for details on the package structure.
PyPy support lags CPython support.


MASTER : 1.4.5
--------------

* allow templated free functions to be attached as methods to classes
* allow cross-derivation from templated classes
* more support for 'using' declarations (methods and inner namespaces)
* fix overload resolution for std::set::rbegin()/rend() operator ==
* fixes for bugs #61, #67


2019-03-20 : 1.4.4
------------------

* Support for 'using' of namespaces
* Improved support for alias templates
* Faster template lookup
* Have rootcling/genreflex respect compile-time flags (except for --std if
  overridden by CLING_EXTRA_FLAGS)
* Utility to build dictionarys on Windows (32/64)
* Name mangling fixes in Cling for JITed global/static variables on Windows
* Several pointer truncation fixes for 64b Windows


2019-03-10 : 1.4.3
------------------

* Cross-inheritance from abstract C++ base classes
* Preserve 'const' when overriding virtual functions
* Support for by-ref (using ctypes) for function callbacks
* Identity of nested typedef'd classes matches actual
* Expose function pointer variables as std::function's
* More descriptive printout of global functions
* Ensure that standard pch is up-to-date and that it is removed on
  uninstall
* Remove standard pch from wheels on all platforms
* Add -cxxflags option to rootcling
* Install clang resource directory on Windows
