import networkx as nx
from dsl.graph_dsl import Graph


def from_adjacency_matrix(matrix: list[list[int]]) -> Graph:
    n = len(matrix)
    vertices = list(range(n))
    edges = []

    for i in range(n):
        for j in range(n):
            if matrix[i][j] != matrix[j][i]:
                raise ValueError(
                    f"Matrix is not symmetric at position ({i},{j}): {matrix[i][j]} != {matrix[j][i]}"
                )

    for i in range(n):
        for j in range(i, n):
            if matrix[i][j] == 1:
                edges.append((i, j))

    return (vertices, edges)


def from_graph(graph: Graph) -> list[list[int]]:
    """The order of vertices determines the ordering in the adjacency matrix."""
    vertices, edges = graph
    n = len(vertices)
    index_of: dict[int, int] = {v: i for i, v in enumerate(vertices)}
    matrix = [[0 for _ in range(n)] for _ in range(n)]

    for a, b in edges:
        if a not in index_of or b not in index_of:
            continue
        i = index_of[a]
        j = index_of[b]
        matrix[i][j] = 1
        matrix[j][i] = 1

    return matrix


def are_graphs_equal(g1: Graph, g2: Graph) -> bool:
    v1, e1 = g1
    v2, e2 = g2

    e1_normalized = set(frozenset([a, b]) for a, b in e1)
    e2_normalized = set(frozenset([a, b]) for a, b in e2)

    if set(v1) == set(v2) and e1_normalized == e2_normalized:
        return True

    nx_g1 = nx.Graph()
    nx_g1.add_nodes_from(v1)
    nx_g1.add_edges_from(e1)

    nx_g2 = nx.Graph()
    nx_g2.add_nodes_from(v2)
    nx_g2.add_edges_from(e2)

    return nx.is_isomorphic(nx_g1, nx_g2)


def get_naive_cost(graph: Graph) -> int:
    vertices, edges = graph
    V, E = len(vertices), len(edges)

    def _by_adding_edges() -> int:
        return E + 1

    def _by_removing_edges() -> int:
        return V * (V - 1) // 2 - E + 1

    return min(_by_removing_edges(), _by_adding_edges())
