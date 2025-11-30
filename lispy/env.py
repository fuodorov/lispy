from typing import List, Optional, Union

from .parser import to_string
from .types import Exp, Symbol


class Env(dict):
    """An environment: a dict of {'var':val} pairs, with an outer Env."""
    def __init__(
        self,
        parms: Union[List[Symbol], Symbol] = (),
        args: List[Exp] = (),
        outer: Optional['Env'] = None
    ) -> None:
        self.outer = outer
        if isinstance(parms, Symbol):
            self.update({parms: list(args)})
        else:
            if len(args) != len(parms):
                raise TypeError('expected %s, given %s, ' % (to_string(parms), to_string(args)))
            self.update(zip(parms, args))

    def find(self, var: Symbol) -> 'Env':
        """Find the innermost Env where var appears."""
        if var in self:
            return self
        elif self.outer is None:
            raise LookupError(var)
        else:
            return self.outer.find(var)


global_env = Env()
