"""
Source: https://github.com/fireuser909/override/blob/master/__init__.py
"""


class override(object):
    '''Use this decorator to assert this callable, classmethod, staticmethod,
    or property overrides an attribute of the same type as the decorated attrbute 
    of its first superclass that has it. 

    This decorator must be used inside a class which its metaclass is OverridesMeta
    or a subclass of it for the decorated attribute to be checked.

    Upon success, the class that this decorater was calledinside will set the
    decorated attribute's name to the  decorated attribute. If the assertion
    failed, the class will raise a subclass of OverrideError.

    Note: classmethods are treated like methods, staticmethods like functions
    '''
    __slots__ = "__func__",

    def __new__(cls, func):
        self = object.__new__(cls)
        if not callable(func) and not isinstance(func, (classmethod, staticmethod, property)):
            raise ValueError("value of func parameter must be callable")
        self.__func__ = func
        return self

    def __eq__(self, other):
        if not isinstance(other, override):
            return NotImplemented
        else:
            return self.__func__ is other.__func__

    def __hash__(self):
        return hash((self.__func__,))
