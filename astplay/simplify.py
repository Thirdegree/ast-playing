"""
Where possible, reduce mutable types to their immutable counterpart (dict -> mapping, list -> sequence, etc)
"""
import ast
from typing import Optional, Dict, Mapping, Union
from pathlib import Path


class AccImmutables(ast.NodeVisitor):
    # let the smart people figure out what counts as "mutating"
    mut_funcs = set(dir(Dict)) - set(dir(Mapping))
    # this one figures out which values are not modified
    # we then need a transformer that uses this, visits function defintions, and modifies whichever args it can

    def __init__(self, func: ast.FunctionDef) -> None:
        self.func = func
        self.are_muted_args: set[ast.arg] = set()

    @property
    def non_muted_args(self) -> set[ast.arg]:
        # this obviously fails to take into account, among other things, kwargs.
        return set(self.func.args.args) - set(self.are_muted_args)

    def _matching_func_arg(self, name: ast.Name) -> Optional[ast.arg]:
        return next((n for n in self.func.args.args if n.arg == name.id), None)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.generic_visit(node)
        if not isinstance(node.value, ast.Name):
            # don't even know what this case is? so gonna ignore it
            return
        if (arg := self._matching_func_arg(node.value)) is None:
            return
        if node.attr in self.mut_funcs:
            self.are_muted_args.add(arg)

    def _check_modify_mutli(self, node: Union[ast.Assign, ast.Delete]) -> None:
        for target in node.targets:
            if not isinstance(target, ast.Subscript):
                continue
            if not isinstance(target.value, ast.Name):
                continue
            if (arg := self._matching_func_arg(target.value)) is None:
                continue
            self.are_muted_args.add(arg)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.generic_visit(node)
        self._check_modify_mutli(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        self.generic_visit(node)
        self._check_modify_mutli(node)


class FuncReducer(ast.NodeTransformer):
    reduce_map = {
        'Dict': 'Mapping',
        'dict': 'Mapping',
        'List': 'Sequence',
        'list': 'Sequence',
    }

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Optional[ast.FunctionDef]:
        _node = self.generic_visit(node)
        assert isinstance(_node, ast.FunctionDef), f"function has been turned into... something else? {node}"
        node = _node
        mut_checker = AccImmutables(node)
        mut_checker.visit(node)
        for arg in node.args.args:
            if arg not in mut_checker.non_muted_args:
                continue
            if arg.annotation is None:
                continue
            value = getattr(arg.annotation, 'value', None)
            if not isinstance(value, ast.Name):
                # again, ignoring the things we don't understand and are too on vacation to research
                continue
            value.id = self.reduce_map.get(value.id, value.id)
        return node


def test() -> None:
    print(ast.unparse(ast.fix_missing_locations(
        FuncReducer().visit(ast.parse(Path('test.py').read_text())))))


if __name__ == "__main__":
    test()
