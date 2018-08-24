import math


#- group: empty-free ---------------------------------------------------------
def empty_call():
    pass

#- group: empty-inst ---------------------------------------------------------
class EmptyCall(object):
    def empty_call(self):
        pass


#- group: builtin-args-free --------------------------------------------------
class Value(object):
    def __init__(self):
        self.m_int = 42

def take_an_int(val):
    pass

def take_a_double(val):
    pass

def take_a_struct(val):
    pass

#- group: builtin-args-inst --------------------------------------------------
class TakeAValue(object):
    def take_an_int(self, val):
        pass

    def take_a_double(self, val):
        pass

    def take_a_struct(self, val):
        pass


#- group: do_work-free -------------------------------------------------------
def do_work(val):
    return math.atan(val)

#- group: do_work-inst -------------------------------------------------------
class DoWork(object):
    def do_work(self, val):
        return math.atan(val)
