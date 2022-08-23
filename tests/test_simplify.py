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


def test_list_to_sequence_assign() -> None:
    code = """\
def test(muted: list[str], unmuted: list[int]) -> None:
    muted[2] = 'hello'
    len(unmuted)"""

    result = FuncReducer().visit(ast.parse(code))

    assert ast.unparse(result) == """\
def test(muted: list[str], unmuted: Sequence[int]) -> None:
    muted[2] = 'hello'
    len(unmuted)"""


def test_list_to_sequence_delete() -> None:
    code = """\
def test(muted: list[str], unmuted: list[int]) -> None:
    del muted[2]
    len(unmuted)"""

    result = FuncReducer().visit(ast.parse(code))

    assert ast.unparse(result) == """\
def test(muted: list[str], unmuted: Sequence[int]) -> None:
    del muted[2]
    len(unmuted)"""


def test_list_to_sequence_delete_nested() -> None:
    code = """\
def test(muted: list[str], unmuted: list[int]) -> None:
    del muted[2]
    len(unmuted)

    def test2(muted2: list[str], unmuted2: list[int]) -> None:
        del muted2[3]
        len(unmuted2)"""

    result = FuncReducer().visit(ast.parse(code))

    assert ast.unparse(result) == """\
def test(muted: list[str], unmuted: Sequence[int]) -> None:
    del muted[2]
    len(unmuted)

    def test2(muted2: list[str], unmuted2: Sequence[int]) -> None:
        del muted2[3]
        len(unmuted2)"""
