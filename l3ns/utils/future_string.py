import inspect
class ProxyMethodWrapper:
    def __init__(self, obj, name):
        self.obj, self.name = obj, name
        assert obj is not None
        assert name is not None

    def __call__( self, *args, **kwargs):
        return self.obj._method_call(self.name, *args, **kwargs)


class FutureString77(str):

    _forbidden_methods = ['__add__']
    _pass_methods = ['__repr__', '__str__']

    _released = False
    _released_value = None


    def __init__(self):
        self._call_list = []


    def __getattribute__(self, name: str):

        # print(name)

        attr = object.__getattribute__(self, name)

        if name == "__class__":
            # print('class')
            return FutureString

        # self_methods
        if name in FutureString.__dict__:
            # print('self-methods ' + name)
            return attr

        if self._released:
            # print('released string ' + name)
            return object.__getattribute__(self._released_value, name)

        if name in self._forbidden_methods:
            # print('not implemented ' + name)
            raise NotImplementedError

        # target
        if callable(attr):
            # print('target ' + name)
            return ProxyMethodWrapper(self, attr, name)

        # default
        # print('default ' + name)
        return attr

    def _method_call(self, name, func, *args, **kwargs):

        self._call_list.append((name, func, args, kwargs))
        return self

    def release(self):
        self._released = True

        self._released_value = 'test'


def _proxy_builtin(name):
    def proxy_method(self, *args, **kwargs):
        if self._released:
            return getattr(self._string_value, name)(*args, **kwargs)
        else:
            return ProxyMethodWrapper(self, name)(*args, **kwargs)

    return proxy_method


class FutureString:

    __doc__ = "TODO"

    _forbidden_methods = []
    _pass_methods = ['__repr__', '__str__']

    _released = False
    _string_value = ''

    def __init__(self, call_list=[]):
        self._call_list = call_list

    def __getattribute__(self, name: str):

        # print(name)

        try:
            attr = object.__getattribute__(self, name)
            # print('self-methods ' + name)
            return attr

        except AttributeError:
            pass

        if self._released:
            # print('released string ' + name)
            return object.__getattribute__(self._string_value, name)

        if name in self._forbidden_methods:
            # print('not implemented ' + name)
            raise NotImplementedError

        attr = getattr(self._string_value, name)

        # target
        if callable(attr):
            # print('target ' + name)
            return ProxyMethodWrapper(self, name)

        # default
        # print('default ' + name)
        return attr

    __add__ = _proxy_builtin('__add__')

    def __radd__(self, other):
        if self._released:
            return other + self._string_value
        else:
            return ProxyMethodWrapper(self, '__radd__')(other)

    __getitem__ = _proxy_builtin('__getitem__')

    __mod__ = _proxy_builtin('__mod__')

    def __rmod__(self, other):
        if self._released:
            return other % self._string_value
        else:
            return ProxyMethodWrapper(self, '__rmod__')(other)

    __mul__ = _proxy_builtin('__mul__')

    __rmul__ = _proxy_builtin('__rmul__')

    def __nonzero__(self):
        if self._released:
            return bool(self._string_value)
        else:
            return bool(self._pass_methods)

    def __str__(self):
        if self._released:
            return self._string_value
        else:
            return '< undefined future string >'

    def __dir__(self):
        if self._released:
            return dir(self._string_value)
        else:
            return dir(self._string_value) + list(object.__dir__(self))

    def __hash__(self):
        if self._released:
            return hash(self._string_value)
        else:
            return hash(self._call_list)

    def _method_call(self, name, *args, **kwargs):
        return FutureString(call_list=self._call_list + [(name, args, kwargs), ])

    def release(self, initial_value):

        string_value = initial_value
        for name, args, kwargs in self._call_list:
            if name == "__radd__":
                string_value = args[0] + string_value
            elif name == "__rmod__":
                string_value = args[0] % string_value
            else:
                string_value = getattr(string_value, name)(*args, **kwargs)

        self._string_value = string_value
        self._released = True


fs = FutureString()

print(fs)

fs = 't1 %s meight' % fs

fs.release('test')
print(fs)
