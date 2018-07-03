#include <pybind11/pybind11.h>
#include "functioncalls.h"

namespace py = pybind11;

PYBIND11_MODULE(py11_functioncalls, m) {
    py::class_<EmptyCall>(m, "EmptyCall")
        .def(py::init<>())
        .def("empty_call", &EmptyCall::empty_call);

    py::class_<Value>(m, "Value")
        .def(py::init<>());

    py::class_<TakeAValue>(m, "TakeAValue")
        .def(py::init<>())
        .def("take_an_int",   &TakeAValue::take_an_int)
        .def("take_a_double", &TakeAValue::take_a_double)
        .def("take_a_value",  &TakeAValue::take_a_value);
}
