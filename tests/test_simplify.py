import ast
from astplay.simplify import FuncReducer


def test_dict_to_mapping_update() -> None:
    code = """\
def test(muted: dict[str, int], unmuted: dict[int, int]) -> None:
    muted.update({'hello': 5})
    unmuted.items()"""

    result = FuncReducer().visit(ast.parse(code))

    assert ast.unparse(result) == """\
def test(muted: dict[str, int], unmuted: Mapping[int, int]) -> None:
    muted.update({'hello': 5})
    unmuted.items()"""


def test_dict_to_mapping_assign() -> None:
    code = """\
def test(muted: dict[str, int], unmuted: dict[int, int]) -> None:
    muted['hello'] = 5
    unmuted.items()"""

    result = FuncReducer().visit(ast.parse(code))

    assert ast.unparse(result) == """\
def test(muted: dict[str, int], unmuted: Mapping[int, int]) -> None:
    muted['hello'] = 5
    unmuted.items()"""


def test_dict_to_mapping_delete() -> None:
    code = """\
def test(muted: dict[str, int], unmuted: dict[int, int]) -> None:
    del muted['hello']
    unmuted.items()"""

    result = FuncReducer().visit(ast.parse(code))

    assert ast.unparse(result) == """\
def test(muted: dict[str, int], unmuted: Mapping[int, int]) -> None:
    del muted['hello']
    unmuted.items()"""
