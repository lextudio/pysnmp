#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#

import sys


class PySnmpError(Exception):
    def __init__(self, *args):
        msg = args and str(args[0]) or ""

        self.cause = sys.exc_info()

        if self.cause[0]:
            msg += f" caused by {self.cause[0]}: {self.cause[1]}"

        if msg:
            args = (msg,) + args[1:]

        Exception.__init__(self, *args)
