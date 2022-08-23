import ast
from typing import Optional, Dict, Mapping
from pathlib import Path


class AccImmutables(ast.NodeVisitor):
    mut_funcs = set(dir(Dict)) - set(dir(Mapping))  # let the smart people figure out what counts as "mutating"
    # this one figures out which values are not modified
    # we then need a transformer that uses this, visits function defintions, and modifies whichever args it can

    def __init__(self, func: ast.FunctionDef) -> None:
        self.func = func
        self.are_muted: set[ast.arg] = set()

    @property
    def are_not_muted(self) -> set[ast.arg]:
        # this obviously fails to take into account, among other things, kwargs.
        return set(self.func.args.args) - set(self.are_muted)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if not isinstance(node.value, ast.Name):
            # don't even know what this case is? so gonna ignore it
            return
        if (arg := next(n for n in self.func.args.args if n.arg == node.value.id)) is None:
            return
        if node.attr in self.mut_funcs:
            self.are_muted.add(arg)


class FuncReducer(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Optional[ast.FunctionDef]:
        mut_checker = AccImmutables(node)
        mut_checker.visit(node)
        for arg in node.args.args:
            # for now we assume everything that isn't mutated is a dictionary,
            # because that's definitely a reasonable thing to assume
            if arg not in mut_checker.are_not_muted:
                continue
            if arg.annotation is None:
                continue
            if not isinstance(getattr(arg.annotation, 'value', None), ast.Name):
                # again, ignoring the things we don't understand and are too on vacation to research
                continue
            assert arg.annotation is not None
            arg.annotation.value = ast.Name(id='Mapping')  # type: ignore[attr-defined]
        return node


def test() -> None:
    print(ast.unparse(ast.fix_missing_locations(
        FuncReducer().visit(ast.parse(Path('test.py').read_text())))))


if __name__ == "__main__":
    test()
