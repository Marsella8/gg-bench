from dsl.dsl import DSL

# Types
Number = int
Vertex = int
Edge = tuple[Vertex, Vertex]
EdgeList = list[Edge]
VertexList = list[Vertex]
Graph = tuple[VertexList, EdgeList]


# DSL Functions

## Create a graph from nothing


def path_graph(start: int, end: int | None = None, step: int = 1) -> Graph:
    if end is None:
        end = start
        start = 0

    vertices = list(range(start, end, step))
    if len(vertices) < 2:
        return (vertices, [])
    edges = [(vertices[i], vertices[i + 1]) for i in range(len(vertices) - 1)]
    return (vertices, edges)


def complete_graph(start: int, end: int | None = None, step: int = 1) -> Graph:
    if end is None:
        end = start
        start = 0
    vertices = list(range(start, end, step))
    edges = [(a, b) for i, a in enumerate(vertices) for b in vertices[i + 1 :]]
    return (vertices, edges)


def cycle_graph(start: int, end: int | None = None, step: int = 1) -> Graph:
    if end is None:
        end = start
        start = 0
    vertices = list(range(start, end, step))
    if len(vertices) < 3:
        return (vertices, [])
    edges = [
        (vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))
    ]
    edges = [(min(a, b), max(a, b)) for a, b in edges]
    return (vertices, edges)


## Modify existing graphs


def shift_graph(graph: Graph, offset: int) -> Graph:
    """Shift all vertex indices in the graph by offset."""
    vertices, edges = graph
    new_vertices = [v + offset for v in vertices]
    new_edges = [(a + offset, b + offset) for a, b in edges]
    return (new_vertices, new_edges)


def union_graphs(*gg: Graph) -> Graph:
    """Union of a bunch of graphs."""
    vertices = []
    edges = []
    for g in gg:
        v, e = g
        vertices.extend(v)
        edges.extend(e)
    vertices = sorted(list(set(vertices)))
    edges = sorted(list(set(edges)))
    return (vertices, edges)


# Create graph from vertices


def connect_one_to_all(center: Vertex, *targets: Vertex) -> Graph:
    """Create a star graph with center connected to all targets."""
    vertices = [center] + list(targets)
    edges = [(center, t) for t in targets]
    return (vertices, edges)


def fully_connect(*vertices: Vertex) -> Graph:
    """Create a fully connected graph with the given vertices."""
    edges = [(i, j) for i in vertices for j in vertices if i < j]
    return (vertices, edges)


def merge_vertices(graph: Graph, v1: Vertex, v2: Vertex) -> Graph:
    """Merge vertices v1 and v2 into a single vertex in graph. v1 is kept. All the old edges of v2 belong to v1."""
    vertices, edges = graph
    if v1 not in vertices or v2 not in vertices or v1 == v2:
        return graph

    new_vertices = [v for v in vertices if v != v2]

    new_edges = []
    for a, b in edges:
        if a == v2:
            a = v1
        if b == v2:
            b = v1
        new_edges.append((min(a, b), max(a, b)))

    new_edges = list(set(new_edges))

    return (new_vertices, new_edges)


def remove_vertex(graph: Graph, v: Vertex) -> Graph:
    """Remove vertex v from graph."""
    vertices, edges = graph
    new_edges = [(a, b) for a, b in edges if a != v and b != v]
    new_vertices = [a for a in vertices if a != v]
    return (new_vertices, new_edges)


def add_edges(graph: Graph, *edges: Edge) -> Graph:
    """If any vercies are missing, we add them as well"""
    vertices, existing_edges = graph
    new_edges = list(set(existing_edges) | set(edges))
    new_vertices = list(set(vertices) | set(v for e in new_edges for v in e))
    return (new_vertices, new_edges)


def remove_edges(graph: Graph, *edges: Edge) -> Graph:
    """Remove edges from a graph."""
    vertices, existing_edges = graph
    edges_to_remove = set(edges) | set((b, a) for a, b in edges)
    new_edges = [edge for edge in existing_edges if edge not in edges_to_remove]
    return (vertices, new_edges)


def vertices(*args, **kwargs) -> list[Vertex]:
    return list(range(*args, **kwargs))


def numerical_range(start: int, end: int | None = None, step: int = 1) -> list[Number]:
    if end is None:
        end = start
        start = 0
    return list(range(start, end, step))


def union_map(items, fn) -> Graph:
    acc: Graph = ([], [])
    for x in items:
        acc = union_graphs(acc, fn(x))
    return acc


GRAPH_DSL = DSL(
    functions=[
        path_graph,
        shift_graph,
        connect_one_to_all,
        union_graphs,
        union_map,
        fully_connect,
        merge_vertices,
        remove_vertex,
        complete_graph,
        cycle_graph,
        add_edges,
        remove_edges,
        vertices,
        numerical_range,
    ],
    types=[
        Number,
        Vertex,
        Edge,
        EdgeList,
        VertexList,
        Graph,
    ],
)
