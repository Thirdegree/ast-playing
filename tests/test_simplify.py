import ast
from astplay.simplify import FuncReducer


def test_dict_to_mapping() -> None:
    code = """\
def test(muted: dict[str, int], unmuted: dict[int, int]) -> None:
    muted.update({'hello': 5})
    unmuted.items()"""

    result = FuncReducer().visit(ast.parse(code))

    assert ast.unparse(result) == """\
def test(muted: dict[str, int], unmuted: Mapping[int, int]) -> None:
    muted.update({'hello': 5})
    unmuted.items()"""
