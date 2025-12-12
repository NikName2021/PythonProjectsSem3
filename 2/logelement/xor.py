from .master import *


class TXor(TLog2In):
    def __init__(self):
        TLog2In.__init__(self)
        self._or = TOr()
        self._and = TAnd()
        self._notAnd = TNot()
        self._finalAnd = TAnd()

        self._and.link(self._notAnd, 1)
        self._or.link(self._finalAnd, 1)
        self._notAnd.link(self._finalAnd, 2)

    def calc(self):
        self._or.In1 = self.In1
        self._or.In2 = self.In2
        self._and.In1 = self.In1
        self._and.In2 = self.In2

        self._res = self._finalAnd.Res


class TXorV2(TLog2In):
    def __init__(self):
        TLog2In.__init__(self)

    def calc(self):
        self._res = self.In1 ^ self.In2
