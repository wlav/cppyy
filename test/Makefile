dicts = advancedcppDict.so \
        advancedcpp2Dict.so \
        conversionsDict.so \
        cpp11featuresDict.so \
        crossinheritanceDict.so \
        datatypesDict.so \
        doc_helperDict.so \
        example01Dict.so \
        fragileDict.so \
        operatorsDict.so \
        overloadsDict.so \
        pythonizablesDict.so \
        std_streamsDict.so \
        stltypesDict.so \
        templatesDict.so

all : $(dicts)

cppflags=$(shell cling-config --cppflags) -std=c++11 -O3 -fPIC -I$(shell python -c 'import sysconfig as sc; print(sc.get_config_var("INCLUDEPY"))') -Wno-register

PLATFORM := $(shell uname -s)
ifeq ($(PLATFORM),Darwin)
  cppflags+=-dynamiclib -single_module -undefined dynamic_lookup -Wno-delete-non-virtual-dtor
endif

%Dict.so: %.cxx
	$(CXX) $(cppflags) -shared -o $@ $^

.PHONY: test clean

test:
	pytest test_*.py

clean:
	-rm -f $(dicts) $(wildcard *.pyc)
