dicts = functioncallsDict.so
CHECK_PYBIND11 := $(shell python -m pybind11 1>&2 1> /dev/null; echo $$?)
ifeq ($(CHECK_PYBIND11),0)
  dicts += py11_functioncalls.so
endif
CHECK_SWIG := $(shell swig -help 1>&2 1> /dev/null; echo $$?)
ifeq ($(CHECK_SWIG),0)
  dicts += _swig_functioncalls.so
endif
all : $(dicts)

ifeq ($(ROOTSYS),)
  clingconfig := cling-config
else
  clingconfig := root-config
endif

cppflags=$(shell $(clingconfig) --cflags) -O3 -fPIC

PLATFORM := $(shell uname -s)
ifeq ($(PLATFORM),Darwin)
  cppflags+=-dynamiclib -single_module -arch x86_64 -undefined dynamic_lookup
endif

py11_%.so: py11_%.cxx %.cxx
	$(CXX) -O3 -shared -std=c++11 -fPIC `python -m pybind11 --includes` -o $@ $^

%_wrap.cxx: %.h %.i
	swig -python -c++ $*.i

_swig_%.so: %_wrap.cxx %.cxx
	$(CXX) -O3 -shared `python-config --includes` -std=c++11 -fPIC  -o $@ $^

%Dict.so: %_rflx.cpp %.cxx
	$(CXX) $(cppflags) -shared -o $@ $^

%_rflx.cpp: %.h %.xml
	genreflex $< --selection=$*.xml --rootmap=$*Dict.rootmap --rootmap-lib=$*Dict.so

.PHONY: bench clean

bench: all
	pytest -s bench_*.py --benchmark-sort=mean

clean:
	-rm -f $(dicts) $(subst .so,.rootmap,$(dicts)) $(subst Dict.so,_rflx_rdict.pcm,$(dicts)) $(subst Dict.so,_rflx.cpp,$(dicts)) $(wildcard *_wrap.cxx) $(wildcard *.pyc)
