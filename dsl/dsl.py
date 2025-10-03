from dataclasses import dataclass
from typing import Callable, Any
import ast
import inspect


def get_only(items: list[Any]) -> Any:
    items = list(items)
    if len(items) != 1:
        raise ValueError(f"Expected 1 item, got {len(items)}")
    return items[0]


@dataclass
class DSL:
    functions: list[Callable]
    types: list[type]


Constant = int
Variable = str
LeafTerm = Constant | Variable
FunctionApplication = tuple[str, list[LeafTerm]]
FunctionAbstraction = tuple[str, FunctionApplication]
Functional = tuple[str, FunctionApplication, FunctionAbstraction]
Term = (
    FunctionApplication | Functional
)  # not great naming, basically you always call a function (the only function is union_map), so at the top level you never have e.g. a funciton abstraction


@dataclass
class Program:
    instructions: list[Term]
    original_function: Callable


def parse_program(program: Callable) -> Program:
    def _get_source_tree(fn: Callable) -> ast.FunctionDef:
        src = inspect.getsource(fn)
        module = ast.parse(src)
        fndefs = [n for n in module.body if isinstance(n, ast.FunctionDef)]
        return get_only(fndefs)

    def _leaf(node: ast.AST) -> LeafTerm:
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return int(node.value)
        if isinstance(node, ast.Name):
            return node.id
        return ast.unparse(node)

    def _fun_app(call: ast.Call) -> FunctionApplication:
        fname = _fun_name(call.func)
        args: list[LeafTerm] = list(map(_leaf, call.args))
        return (fname, args)

    def _lambda(lam: ast.Lambda) -> FunctionAbstraction:
        params = [a.arg for a in lam.args.args]
        if len(params) != 1:
            raise ValueError(
                "Only single-parameter lambdas are supported in this grammar"
            )
        if not isinstance(lam.body, ast.Call):
            raise ValueError("Lambda body must be a single DSL call in this grammar")
        body = _fun_app(lam.body)
        return (get_only(params), body)

    def _fun_name(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        raise ValueError(f"Unsupported function reference: {ast.unparse(node)}")

    def _parse_union_map_call(value: ast.Call) -> Term:
        if (
            len(value.args) < 2
            or not isinstance(value.args[0], ast.Call)
            or not isinstance(value.args[1], ast.Lambda)
        ):
            raise ValueError("union_map(items: Call, fn: Lambda) expected")
        items = _fun_app(value.args[0])
        fn_abs = _lambda(value.args[1])
        return ("union_map", items, fn_abs)

    fn = _get_source_tree(program)
    instructions: list[Term] = []

    for stmt in fn.body:
        if isinstance(stmt, ast.Assign):
            value = stmt.value
            if isinstance(value, ast.Call):
                fname = _fun_name(value.func)
                if fname == "union_map":
                    instructions.append(_parse_union_map_call(value))
                else:
                    instructions.append(_fun_app(value))
            continue

        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            value = stmt.value
            fname = _fun_name(value.func)
            if fname == "union_map":
                instructions.append(_parse_union_map_call(value))
            else:
                instructions.append(_fun_app(value))
            continue

        if isinstance(stmt, ast.Return):
            value = stmt.value
            if isinstance(value, ast.Call):
                fname = _fun_name(value.func)
                if fname == "union_map":
                    instructions.append(_parse_union_map_call(value))
                else:
                    instructions.append(_fun_app(value))
            continue

        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        ):
            continue

        raise ValueError(
            f"Unsupported statement in DSL program: {ast.dump(stmt, include_attributes=False)}"
        )

    return Program(instructions=instructions, original_function=program)


def get_program_cost(program: Program) -> int:
    def cost_function_application(app: FunctionApplication) -> int:
        _, args = app
        return len(args)

    def cost_function_abstraction(abs_fn: FunctionAbstraction) -> int:
        _, body = abs_fn
        return 1 + cost_function_application(body)

    def cost_term(term: Term) -> int:
        if isinstance(term, tuple) and len(term) == 3 and term[0] == "union_map":
            _, items_app, fn_abs = term
            items_cost = cost_function_application(items_app)
            fn_cost = cost_function_abstraction(fn_abs)
            return items_cost + fn_cost
        if isinstance(term, tuple) and len(term) == 2 and isinstance(term[0], str):
            return cost_function_application(term)
        raise ValueError(f"Unsupported term: {term}")

    return sum(cost_term(t) for t in program.instructions)
