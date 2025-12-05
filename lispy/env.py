"""
Environment module.

This module defines the `Env` class, which represents the execution environment
(scope) for variables.
"""
from typing import List, Optional, Union

from .errors import ArgumentError, SymbolNotFoundError
from .parser import to_string
from .types import Exp, Symbol


class Env(dict):
    """
    An environment: a dict of {'var':val} pairs, with an outer Env.

    This class represents a scope in the Scheme interpreter. It inherits from `dict`
    to store variable bindings and maintains a reference to the outer (enclosing)
    environment for lexical scoping.
    """
    def __init__(
        self,
        parms: Union[List[Symbol], Symbol] = (),
        args: List[Exp] = (),
        outer: Optional['Env'] = None
    ) -> None:
        """
        Initialize the Environment.

        Args:
            parms (Union[List[Symbol], Symbol]): Parameter names. Can be a list of symbols
                or a single symbol (for variadic functions).
            args (List[Exp]): Argument values corresponding to `parms`.
            outer (Optional[Env]): The outer environment. Defaults to None.

        Raises:
            ArgumentError: If the number of arguments does not match the number of parameters.
        """
        self.outer = outer
        if isinstance(parms, Symbol):
            self.update({parms: list(args)})
        else:
            if len(args) != len(parms):
                raise ArgumentError('expected %s, given %s, ' % (to_string(parms), to_string(args)))
            self.update(zip(parms, args))

    def find(self, var: Symbol) -> 'Env':
        """
        Find the innermost Env where var appears.

        Args:
            var (Symbol): The variable name to look up.

        Returns:
            Env: The environment containing the variable.

        Raises:
            SymbolNotFoundError: If the variable is not found in this or any outer environment.
        """
        if var in self:
            return self
        elif self.outer is None:
            raise SymbolNotFoundError(var)
        else:
            return self.outer.find(var)


global_env = Env()
