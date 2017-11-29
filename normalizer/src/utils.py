# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import sys


class StringView:
    def __init__(self, s, start=0, size=sys.maxint):
        self.s, self.start, self.stop = s, start, min(start + size, len(s))
        self.size = self.stop - self.start
        self._buf = buffer(s, start, self.size)

    def find(self, sub, start=0, stop=None):
        assert start >= 0, start
        assert (stop is None) or (stop <= self.size), stop
        ofs = self.s.find(sub, self.start + start,
                          self.stop if (stop is None) else (self.start + stop))
        if ofs != -1:
            ofs -= self.start
        return ofs

    def split(self, sep=None, maxsplit=sys.maxint):
        assert maxsplit > 0, maxsplit
        ret = []
        if sep is None:  # whitespace logic
            pos = [self.start, self.start]  # start and stop

            def eat(whitespace=False):
                while (pos[1] < self.stop) and (whitespace == (ord(self.s[pos[1]]) <= 32)):
                    pos[1] += 1

            def eat_whitespace():
                eat(True)
                pos[0] = pos[1]
            eat_whitespace()
            while pos[1] < self.stop:
                eat()
                ret.append(self.__class__(self.s, pos[0], pos[1] - pos[0]))
                eat_whitespace()
                if len(ret) == maxsplit:
                    ret.append(self.__class__(self.s, pos[1]))
                    break
        else:
            start = stop = 0
            while len(ret) < maxsplit:
                stop = self.find(sep, start)
                if -1 == stop:
                    break
                ret.append(self.__class__(
                    self.s, self.start + start, stop - start))
                start = stop + len(sep)
            ret.append(self.__class__(
                self.s, self.start + start, self.size - start))
        return ret

    def split_str(self, sep=None, maxsplit=sys.maxint):
        "if you really want strings and not views"
        return [str(sub) for sub in self.split(sep, maxsplit)]

    def __cmp__(self, s):
        if isinstance(s, self.__class__):
            return cmp(self._buf, s._buf)
        assert isinstance(s, str), type(s)
        return cmp(self._buf, s)

    def __len__(self):
        return self.size

    def __str__(self):
        return str(self._buf)

    def __repr__(self):
        return "'%s'" % self._buf
