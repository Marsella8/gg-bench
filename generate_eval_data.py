from pathlib import Path
import json
import inspect
from typing import Any
from dsl.samples import TEST_GRAPHS
from dsl.utils import from_graph, get_naive_cost
from dsl.dsl import parse_program, get_program_cost

out = Path(__file__).resolve().parent / "data"
out.mkdir(parents=True, exist_ok=True)


def build_datapoint(name: str, fn) -> dict[str, Any]:
    graph = fn()
    matrix = from_graph(graph)
    prog = parse_program(fn)
    dsl_cost = get_program_cost(prog)
    naive_cost = get_naive_cost(graph)
    ratio = (naive_cost / dsl_cost) if dsl_cost else 0.0
    src = inspect.getsource(fn)
    return {
        "name": name,
        "adjacency_matrix": matrix,
        "dsl_cost": dsl_cost,
        "naive_cost": naive_cost,
        "compression_ratio": ratio,
        "code": src,
    }


def save_dataset():
    dataset = []
    for fn in TEST_GRAPHS:
        name = fn.__name__
        dp = build_datapoint(name, fn)
        dataset.append(dp)
        (out / f"{name}.json").write_text(json.dumps(dp, indent=2))


if __name__ == "__main__":
    save_dataset()
