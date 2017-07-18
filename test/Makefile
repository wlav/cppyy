dicts = advancedcppDict.so \
        advancedcpp2Dict.so \
        datatypesDict.so \
        example01Dict.so \
        fragileDict.so \
        operatorsDict.so \
        overloadsDict.so \
        std_streamsDict.so \
        stltypesDict.so
all : $(dicts)

ifndef CPPYYHOME
  CPPYYHOME=$(dir $(shell python -c 'import cppyy, os; os.write(1, cppyy.__file__)'))
endif

ifndef BACKENDHOME
  BACKENDHOME=$(CPPYYHOME)/../cppyy_backend
endif

genreflex := $(shell command -v genreflex 2> /dev/null)
ifndef genreflex
  genreflex := $(BACKENDHOME)/bin/genreflex
endif

cppflags=-std=c++11 -I$(BACKENDHOME)/include -O3 -m64 -fPIC

PLATFORM := $(shell uname -s)
ifeq ($(PLATFORM),Darwin)
  cppflags+=-dynamiclib -single_module -arch x86_64 -undefined dynamic_lookup
endif

%Dict.so: %_rflx.cpp %.cxx
	g++ $(cppflags) -shared -o $@ $^

%_rflx.cpp: %.h %.xml
	$(genreflex) $< --selection=$*.xml --rootmap=$*Dict.rootmap --rootmap-lib=$*Dict.so

.PHONY: test clean

test:
	pytest test_*.py

clean:
	-rm -f $(dicts) $(subst .so,.rootmap,$(dicts)) $(subst Dict.so,_rflx_rdict.pcm,$(dicts)) $(subst Dict.so,_rflx.cpp,$(dicts)) $(wildcard *.pyc)
