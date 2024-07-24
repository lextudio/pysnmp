#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from bisect import bisect


class OrderedDict(dict):
    """Ordered dictionary used for indices"""

    def __init__(self, *args, **kwargs):
        self.__keys = []
        self.__dirty = True
        super().__init__()
        if args:
            self.update(*args)
        if kwargs:
            self.update(**kwargs)

    def __setitem__(self, key, value):
        if key not in self:
            self.__keys.append(key)
            self.__dirty = True
        super().__setitem__(key, value)

    def __delitem__(self, key):
        if key in self:
            self.__keys.remove(key)
            self.__dirty = True
        super().__delitem__(key)

    def clear(self):
        super().clear()
        self.__keys = []
        self.__dirty = True

    def keys(self):
        if self.__dirty:
            self.__order()
        return list(self.__keys)

    def values(self):
        if self.__dirty:
            self.__order()
        return [self[k] for k in self.__keys]

    def items(self):
        if self.__dirty:
            self.__order()
        return [(k, self[k]) for k in self.__keys]

    def update(self, *args, **kwargs):
        if args:
            iterable = args[0]
            if hasattr(iterable, "keys"):
                for k in iterable:
                    self[k] = iterable[k]
            else:
                for k, v in iterable:
                    self[k] = v

        if kwargs:
            for k in kwargs:
                self[k] = kwargs[k]

    def sortingFun(self, keys):
        keys.sort()

    def __order(self):
        self.sortingFun(self.__keys)
        self.__keysLens = sorted({len(k) for k in self.__keys}, reverse=True)
        self.__dirty = False

    def nextKey(self, key):
        if self.__dirty:
            self.__order()

        keys = self.__keys

        nextIdx = bisect(keys, key)

        if nextIdx < len(keys):
            return keys[nextIdx]

        else:
            raise KeyError(key)

    def getKeysLens(self):
        if self.__dirty:
            self.__order()
        return self.__keysLens


class OidOrderedDict(OrderedDict):
    """OID-ordered dictionary used for indices"""

    def __init__(self, *args, **kwargs):
        self.__keysCache = {}
        OrderedDict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if key not in self.__keysCache:
            if isinstance(key, tuple):
                self.__keysCache[key] = key
            else:
                self.__keysCache[key] = [int(x) for x in key.split(".") if x]

    def __delitem__(self, key):
        OrderedDict.__delitem__(self, key)
        if key in self.__keysCache:
            del self.__keysCache[key]

    def sortingFun(self, keys):
        keys.sort(key=lambda k, d=self.__keysCache: d[k])
