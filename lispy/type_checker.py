"""
Type checking functionality.
"""
from typing import Any

from .constants import TYPE_BOOL, TYPE_FLOAT, TYPE_INT, TYPE_LIST, TYPE_STR
from .errors import UserError
from .messages import ERR_UNKNOWN_TYPE

TYPE_MAPPING = {
    TYPE_INT: int,
    TYPE_FLOAT: float,
    TYPE_STR: str,
    TYPE_BOOL: bool,
    TYPE_LIST: list,
}


def check_type(val: Any, type_sym: str) -> bool:
    """
    Check if value matches the Scheme type symbol.

    Args:
        val (Any): The value to check.
        type_sym (str): The type symbol (e.g. 'int').

    Returns:
        bool: True if the value matches the type, False otherwise.

    Raises:
        UserError: If the type symbol is unknown.
    """
    if type_sym not in TYPE_MAPPING:
        raise UserError(ERR_UNKNOWN_TYPE)

    expected_type = TYPE_MAPPING[type_sym]
    # Special case for numbers? In Python bool is int.
    if expected_type is int and isinstance(val, bool):
        return False
    return isinstance(val, expected_type)
