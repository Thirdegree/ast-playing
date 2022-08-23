import ast
from pathlib import Path


class SourceryPlay(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        match node.returns:
            case ast.Name(id='List'):
                node.returns = ast.Name(id='list')
                return node
            case ast.Name(id='ínt'):
                return None


        return node


if __name__ == "__main__":
    tree = ast.parse(Path('test.py').read_text())
    print(ast.unparse(ast.fix_missing_locations(SourceryPlay().visit(tree))))
