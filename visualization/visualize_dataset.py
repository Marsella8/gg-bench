from __future__ import annotations  # my beloved

from pathlib import Path
import json
import itertools
from flask import Flask


def matrix_to_elements(matrix: list[list[int]]):
    n = len(matrix)
    nodes = [{"data": {"id": str(i)}} for i in range(n)]
    edges = [
        {"data": {"source": str(i), "target": str(j)}}
        for (i, j) in itertools.combinations(range(n), 2)
        if matrix[i][j] == 1
    ]
    return {"nodes": nodes, "edges": edges}


app = Flask(__name__)


@app.route("/")
def index():
    root = Path(__file__).resolve().parent
    data_dir = root.parent / "data"
    graphs = []

    json_files = sorted(
        p
        for p in data_dir.iterdir()
        if p.suffix == ".json" and p.name != "_dataset.json"
    )
    for p in json_files:
        obj = json.loads(p.read_text())
        graphs.append(
            {
                "name": obj["name"],
                "dsl_cost": obj["dsl_cost"],
                "naive_cost": obj["naive_cost"],
                "ratio": obj["compression_ratio"],
                "elements": matrix_to_elements(obj["adjacency_matrix"]),
            }
        )

    template_path = root / "template.html"
    template = template_path.read_text()
    return template.format(graph_count=len(graphs), graphs_json=json.dumps(graphs))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
