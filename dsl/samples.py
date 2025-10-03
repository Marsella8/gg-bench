"""
Note: to make the examples parsable with my DSL machinations, I have to fully instantiate the graph generation functions (i.e. can't do stuff like wheel(8)).
"""

from dsl.graph_dsl import (
    Graph,
    path_graph,
    shift_graph,
    union_graphs,
    union_map,
    numerical_range,
    connect_one_to_all,
    complete_graph,
    add_edges,
    remove_edges,
    merge_vertices,
    cycle_graph,
    fully_connect,
)


def trifoil() -> Graph:
    # Trifoil graph (idk if it's a term), each leaf has 4 vertices (excluding the center)
    g1 = path_graph(1, 15)
    g2 = connect_one_to_all(0, 1, 5, 6, 10, 11, 15)
    return union_graphs(g1, g2)


def quadrifoil() -> Graph:
    g1 = path_graph(1, 21)
    g2 = connect_one_to_all(0, 1, 5, 6, 10, 11, 15, 16, 20)
    return union_graphs(g1, g2)


def all_to_all_trifoil() -> Graph:
    # Like the one before but instead of the center we have do a K_6
    g1 = path_graph(0, 15)
    g2 = fully_connect(0, 4, 5, 9, 10, 14)
    return union_graphs(g1, g2)


def all_to_all_quadrifoil() -> Graph:
    g1 = path_graph(0, 20)
    g2 = fully_connect(0, 4, 5, 9, 10, 14, 15, 19)
    return union_graphs(g1, g2)


def cross() -> Graph:
    # Basically 2 paths that intersect in the middles
    g1 = path_graph(0, 7)
    g2 = path_graph(7, 14)
    g3 = union_graphs(g1, g2)
    g4 = merge_vertices(g3, 3, 10)
    return g4


def tesseract() -> Graph:
    """Tesseract (4D hypercube) on vertices 0..15."""
    cube0 = path_graph(0, 8)
    cube0 = remove_edges(cube0, (1, 2), (3, 4), (5, 6))
    cube0 = add_edges(
        cube0,
        (0, 2),
        (1, 3),
        (4, 6),
        (5, 7),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    )

    cube1 = shift_graph(cube0, 8)

    bridge = add_edges(
        cube0, (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 15)
    )
    return union_graphs(cube1, bridge)


def parallel() -> Graph:
    """Three parallel paths with shared endpoints."""
    g1 = path_graph(0, 12)
    g2 = path_graph(12, 24)
    g3 = path_graph(24, 36)
    g3 = union_graphs(g1, g2, g3)
    g4 = merge_vertices(g3, 0, 12)
    g4 = merge_vertices(g4, 0, 24)
    g5 = merge_vertices(g4, 11, 23)
    g6 = merge_vertices(g5, 11, 35)
    return g6


def binary_tree() -> Graph:
    """Merge and duplicate a bunch of times the same graph together at the root."""
    t1 = path_graph(0, 3)
    t2 = path_graph(3, 6)

    level1 = union_graphs(t1, t2)
    root = connect_one_to_all(6, 1, 4)
    tree1 = union_graphs(level1, root)

    tree2 = shift_graph(tree1, 7)
    both_trees = union_graphs(tree1, tree2)
    final_root = connect_one_to_all(14, 6, 6 + 7)
    return union_graphs(both_trees, final_root)


def dumbbell() -> Graph:
    """Two complete graphs K_8 connected by a double edge."""
    g1 = complete_graph(0, 8)
    g2 = complete_graph(8, 16)
    g = union_graphs(g1, g2)
    g = add_edges(g, (3, 11), (4, 12))
    return g


def crown_6() -> Graph:
    """Crown graph: cycle where each vertex also connects to vertices at distance 2."""
    g1 = complete_graph(0, 6)
    g2 = remove_edges(g1, (0, 3), (1, 4), (2, 5))
    return g2


def crown_8() -> Graph:
    # I think that crown 8 is more compressible thatn crown 6, cool!
    g1 = cycle_graph(8)
    g2 = cycle_graph(0, 8, 2)
    g3 = cycle_graph(1, 8, 2)
    return union_graphs(g1, g2, g3)


def ladder_with_rungs_6() -> Graph:
    left = path_graph(0, 6)
    right = path_graph(6, 12)
    single_rung = path_graph(0, 12, 6)
    rungs = union_map(numerical_range(1, 5), lambda k: shift_graph(single_rung, k))
    return union_graphs(left, right, rungs)


def ladder_with_rungs_12() -> Graph:
    left = path_graph(0, 12)
    right = path_graph(12, 24)
    single_rung = path_graph(0, 24, 12)
    rungs = union_map(numerical_range(1, 11), lambda k: shift_graph(single_rung, k))
    return union_graphs(left, right, rungs)


def triplex_clique_chain() -> Graph:
    k5a = complete_graph(0, 5)
    k5b = shift_graph(k5a, 5)
    k5c = shift_graph(k5b, 5)
    g = union_graphs(k5a, k5b, k5c)
    g2 = add_edges(g, (2, 5), (7, 10), (2, 11))
    return g2


def butterfly() -> Graph:
    """A very ugly butterfly"""
    c8 = cycle_graph(12)
    center = connect_one_to_all(0, 3, 6, 9)
    return union_graphs(c8, center)


def crown_dumbbell() -> Graph:
    """Two crowns with a bridge between them"""
    c1 = remove_edges(complete_graph(0, 6), (0, 3), (1, 4), (2, 5))
    c2 = shift_graph(c1, 6)
    g = union_graphs(c1, c2)
    g2 = add_edges(g, (0, 9), (3, 6))
    return g2


def glasses_with_no_bridge() -> Graph:
    """Cool trick: shift by 4 so they are not disjoint, and then the union basically merges the 2 nodes"""
    c1 = remove_edges(complete_graph(0, 6), (0, 3), (1, 4), (2, 5))
    c2 = shift_graph(c1, 4)
    g = union_graphs(c1, c2)
    return g


def interlocked_cycles() -> Graph:
    """Two cycles with a vertex in common"""
    c1 = cycle_graph(6)
    c2 = cycle_graph(6, 12)
    g = union_graphs(c1, c2)
    g2 = merge_vertices(g, 0, 6)
    g3 = merge_vertices(g2, 3, 9)
    return g3


def petersen() -> Graph:
    """Petersen graph !!!"""
    outer = cycle_graph(5)
    inner = cycle_graph(5, 10)
    g = union_graphs(outer, inner)
    return add_edges(g, (4, 5), (1, 6), (3, 7), (0, 8), (2, 9))


def petersen_complete() -> Graph:
    """Like a petersen but with a K_5 instead of the star"""
    outer = cycle_graph(5)
    inner = complete_graph(5, 10)
    g1 = union_graphs(outer, inner)
    g2 = add_edges(g1, (0, 5), (1, 6), (2, 7), (3, 8), (4, 9))
    return g2


def dodecahedron() -> Graph:
    """Dodecahedral graph (20 vertices, 3-regular)."""
    top = cycle_graph(5)
    bottom = shift_graph(top, 5)
    ring = shift_graph(cycle_graph(10), 10)
    top_spokes = union_map(
        numerical_range(5), lambda k: connect_one_to_all(k, 10 + 2 * k)
    )
    bottom_spokes = union_map(
        numerical_range(5), lambda k: connect_one_to_all(5 + k, 11 + 2 * k)
    )
    return union_graphs(top, bottom, ring, top_spokes, bottom_spokes)


def moebius_kantor() -> Graph:
    """Cool shape, dont really know how to compress it nicely"""
    outer = cycle_graph(8)
    inner = union_map(
        numerical_range(8), lambda i: connect_one_to_all(i + 8, (i + 3) % 8 + 8)
    )
    spokes = union_map(numerical_range(8), lambda i: connect_one_to_all(i, i + 8))
    return union_graphs(outer, inner, spokes)


def friendship_graph_5() -> Graph:
    return union_map(
        numerical_range(5), lambda k: fully_connect(0, 2 * k + 1, 2 * k + 2)
    )


def friendship_graph_8() -> Graph:
    return union_map(
        numerical_range(8), lambda k: fully_connect(0, 2 * k + 1, 2 * k + 2)
    )


def friendship_graph_12() -> Graph:
    return union_map(
        numerical_range(12), lambda k: fully_connect(0, 2 * k + 1, 2 * k + 2)
    )


def clique_chain_3() -> Graph:
    base = complete_graph(3)
    return union_map(numerical_range(3), lambda i: shift_graph(base, i * 2))


def clique_chain_4() -> Graph:
    base = complete_graph(0, 4)
    return union_map(numerical_range(4), lambda i: shift_graph(base, i * 3))


def clique_chain_5() -> Graph:
    base = complete_graph(0, 5)
    return union_map(numerical_range(5), lambda i: shift_graph(base, i * 4))


def cycle_chain_3() -> Graph:
    base = cycle_graph(3)
    return union_map(numerical_range(3), lambda i: shift_graph(base, i * 2))


def cycle_chain_4() -> Graph:
    base = cycle_graph(4)
    return union_map(numerical_range(4), lambda i: shift_graph(base, i * 3))


def cycle_chain_5() -> Graph:
    base = cycle_graph(5)
    return union_map(numerical_range(5), lambda i: shift_graph(base, i * 4))


def wheel_8() -> Graph:
    c = cycle_graph(7)
    s = connect_one_to_all(7, *numerical_range(7))
    return union_graphs(c, s)


def wheel_12() -> Graph:
    c = cycle_graph(11)
    s = connect_one_to_all(11, *numerical_range(11))
    return union_graphs(c, s)


# New interesting shapes (< 20 vertices)
def heawood_graph() -> Graph:
    """Heawood graph (14 vertices): C14 plus chords (i, i+5)."""
    base = cycle_graph(14)
    chords = union_map(
        numerical_range(14), lambda i: connect_one_to_all(i, (i + 5) % 14)
    )
    return union_graphs(base, chords)


def prism_8() -> Graph:
    """Prism graph over C8 (16 vertices)."""
    c1 = cycle_graph(8)
    c2 = shift_graph(c1, 8)
    rungs = union_map(numerical_range(8), lambda i: connect_one_to_all(i, i + 8))
    return union_graphs(c1, c2, rungs)


def gear_6() -> Graph:
    """Gear graph G6 (13 vertices): C12 ring + center connected to alternate ring vertices."""
    ring = cycle_graph(12)
    spokes = union_map(numerical_range(0, 12, 2), lambda k: connect_one_to_all(12, k))
    return union_graphs(ring, spokes)


def prism_7() -> Graph:
    c1 = cycle_graph(7)
    c2 = shift_graph(c1, 7)
    rungs = union_map(numerical_range(7), lambda i: connect_one_to_all(i, i + 7))
    return union_graphs(c1, c2, rungs)


def prism_9() -> Graph:
    c1 = cycle_graph(9)
    c2 = shift_graph(c1, 9)
    rungs = union_map(numerical_range(9), lambda i: connect_one_to_all(i, i + 9))
    return union_graphs(c1, c2, rungs)


def helm_9() -> Graph:
    rim = cycle_graph(8)
    hub = connect_one_to_all(8, *numerical_range(8))
    wheel = union_graphs(rim, hub)
    pendants = union_map(numerical_range(8), lambda i: connect_one_to_all(i, 9 + i))
    return union_graphs(wheel, pendants)


def helm_6() -> Graph:
    rim = cycle_graph(5)
    hub = connect_one_to_all(5, *numerical_range(5))
    wheel = union_graphs(rim, hub)
    pendants = union_map(numerical_range(5), lambda i: connect_one_to_all(i, 6 + i))
    return union_graphs(wheel, pendants)


def generalized_petersen_6_2() -> Graph:
    outer = cycle_graph(6)
    inner = union_map(
        numerical_range(6), lambda i: connect_one_to_all(6 + i, (i + 2) % 6 + 6)
    )
    spokes = union_map(numerical_range(6), lambda i: connect_one_to_all(i, i + 6))
    return union_graphs(outer, inner, spokes)


def generalized_petersen_9_2() -> Graph:
    outer = cycle_graph(9)
    inner = union_map(
        numerical_range(9), lambda i: connect_one_to_all(9 + i, (i + 2) % 9 + 9)
    )
    spokes = union_map(numerical_range(9), lambda i: connect_one_to_all(i, i + 9))
    return union_graphs(outer, inner, spokes)


def complete_bipartite_3_5() -> Graph:
    return union_map(numerical_range(3), lambda i: connect_one_to_all(i, 3, 4, 5, 6, 7))


def complete_bipartite_4_4() -> Graph:
    return union_map(
        numerical_range(4), lambda i: connect_one_to_all(i, *numerical_range(4, 8))
    )


def web_5_3() -> Graph:
    r1 = cycle_graph(5)
    r2 = shift_graph(r1, 5)
    r3 = shift_graph(r2, 5)
    s12 = union_map(numerical_range(5), lambda i: connect_one_to_all(i, i + 5))
    s23 = union_map(numerical_range(5), lambda i: connect_one_to_all(i + 5, i + 10))
    return union_graphs(r1, r2, r3, s12, s23)


def web_6_3() -> Graph:
    r1 = cycle_graph(6)
    r2 = shift_graph(r1, 6)
    r3 = shift_graph(r2, 6)
    s12 = union_map(numerical_range(6), lambda i: connect_one_to_all(i, i + 6))
    s23 = union_map(numerical_range(6), lambda i: connect_one_to_all(i + 6, i + 12))
    return union_graphs(r1, r2, r3, s12, s23)


def wagner_graph() -> Graph:
    c8 = cycle_graph(8)
    chords = add_edges(c8, (0, 4), (1, 5), (2, 6), (3, 7))
    return chords


def moebius_ladder_10() -> Graph:
    ring = cycle_graph(10)
    rungs = union_map(numerical_range(5), lambda i: connect_one_to_all(i, i + 5))
    return union_graphs(ring, rungs)


def desargues_graph() -> Graph:
    outer = cycle_graph(10)
    inner = union_map(
        numerical_range(10), lambda i: connect_one_to_all(10 + i, (i + 3) % 10 + 10)
    )
    spokes = union_map(numerical_range(10), lambda i: connect_one_to_all(i, i + 10))
    return union_graphs(outer, inner, spokes)


def nauru_graph() -> Graph:
    outer = cycle_graph(12)
    inner = union_map(
        numerical_range(12), lambda i: connect_one_to_all(12 + i, (i + 5) % 12 + 12)
    )
    spokes = union_map(numerical_range(12), lambda i: connect_one_to_all(i, i + 12))
    return union_graphs(outer, inner, spokes)


def durer_graph() -> Graph:
    c1 = cycle_graph(6)
    c2 = shift_graph(c1, 6)
    rungs = union_map(numerical_range(6), lambda i: connect_one_to_all(i, i + 6))
    return union_graphs(c1, c2, rungs)


def cube_graph_q3() -> Graph:
    c1 = cycle_graph(4)
    c2 = shift_graph(c1, 4)
    rungs = union_map(numerical_range(4), lambda i: connect_one_to_all(i, i + 4))
    return union_graphs(c1, c2, rungs)


def prism_10() -> Graph:
    c1 = cycle_graph(10)
    c2 = shift_graph(c1, 10)
    rungs = union_map(numerical_range(10), lambda i: connect_one_to_all(i, i + 10))
    return union_graphs(c1, c2, rungs)


def generalized_petersen_7_2() -> Graph:
    outer = cycle_graph(7)
    inner = union_map(
        numerical_range(7), lambda i: connect_one_to_all(7 + i, (i + 2) % 7 + 7)
    )
    spokes = union_map(numerical_range(7), lambda i: connect_one_to_all(i, i + 7))
    return union_graphs(outer, inner, spokes)


def gear_8() -> Graph:
    ring = cycle_graph(16)
    spokes = union_map(numerical_range(0, 16, 2), lambda k: connect_one_to_all(16, k))
    return union_graphs(ring, spokes)


def paley_13() -> Graph:
    return union_map(
        numerical_range(13),
        lambda i: connect_one_to_all(
            i,
            (i + 1) % 13,
            (i + 3) % 13,
            (i + 4) % 13,
        ),
    )


def overlapping_cliques() -> Graph:
    base = complete_graph(0, 6)
    shifted = shift_graph(base, 4)
    return union_graphs(base, shifted)


def double_ring_with_chords() -> Graph:
    ring = cycle_graph(12)
    ring2 = shift_graph(ring, 6)
    chords = union_map(
        numerical_range(0, 12, 3), lambda i: connect_one_to_all(i, (i + 3) % 12)
    )
    return union_graphs(ring, ring2, chords)


def overlapped_ladders_with_diagonals() -> Graph:
    left = path_graph(0, 8)
    right = path_graph(8, 16)
    single_rung = path_graph(0, 16, 8)
    rungs = union_map(numerical_range(1, 8), lambda k: shift_graph(single_rung, k))
    ladder = union_graphs(left, right, rungs)
    diag1 = union_map(numerical_range(7), lambda i: connect_one_to_all(i, i + 9))
    diag2 = union_map(numerical_range(7), lambda i: connect_one_to_all(i + 8, i + 1))
    ladderx = union_graphs(ladder, diag1, diag2)
    shifted = shift_graph(ladderx, 4)
    return union_graphs(ladderx, shifted)


def twin_wheels_overlap() -> Graph:
    rim1 = cycle_graph(9)
    hub1 = connect_one_to_all(9, *numerical_range(9))
    w1 = union_graphs(rim1, hub1)
    w2 = shift_graph(w1, 5)
    return union_graphs(w1, w2)


def clique_ring_bipart() -> Graph:
    c = cycle_graph(10)
    even = fully_connect(0, 2, 4, 6, 8)
    odd = fully_connect(1, 3, 5, 7, 9)
    return union_graphs(c, even, odd)


def overlapping_k4_chain() -> Graph:
    base = complete_graph(0, 4)
    return union_map(numerical_range(6), lambda i: shift_graph(base, 2 * i))


def grid_3x4_braced_overlap() -> Graph:
    row1 = path_graph(0, 4)
    row2 = path_graph(4, 8)
    row3 = path_graph(8, 12)
    cols_top = union_map(numerical_range(4), lambda c: connect_one_to_all(c, 4 + c))
    cols_bottom = union_map(
        numerical_range(4), lambda c: connect_one_to_all(4 + c, 8 + c)
    )
    braces_top = union_map(numerical_range(3), lambda c: connect_one_to_all(c, 5 + c))
    braces_bottom = union_map(
        numerical_range(3), lambda c: connect_one_to_all(4 + c, 9 + c)
    )
    grid = union_graphs(
        row1, row2, row3, cols_top, cols_bottom, braces_top, braces_bottom
    )
    overlapped = shift_graph(grid, 2)
    return union_graphs(grid, overlapped)


def overlapping_bipartites() -> Graph:
    k34_a = union_map(numerical_range(3), lambda i: connect_one_to_all(i, 3, 4, 5, 6))
    k34_b = shift_graph(k34_a, 2)
    return union_graphs(k34_a, k34_b)


TEST_GRAPHS = [
    trifoil,
    quadrifoil,
    all_to_all_trifoil,
    all_to_all_quadrifoil,
    cross,
    tesseract,
    parallel,
    binary_tree,
    dumbbell,
    crown_6,
    crown_8,
    ladder_with_rungs_6,
    ladder_with_rungs_12,
    triplex_clique_chain,
    butterfly,
    crown_dumbbell,
    glasses_with_no_bridge,
    interlocked_cycles,
    petersen,
    petersen_complete,
    dodecahedron,
    moebius_kantor,
    friendship_graph_5,
    friendship_graph_8,
    friendship_graph_12,
    clique_chain_3,
    clique_chain_4,
    clique_chain_5,
    cycle_chain_3,
    cycle_chain_4,
    cycle_chain_5,
    wheel_8,
    wheel_12,
    heawood_graph,
    prism_8,
    gear_6,
    prism_7,
    prism_9,
    helm_9,
    helm_6,
    generalized_petersen_6_2,
    generalized_petersen_9_2,
    complete_bipartite_3_5,
    complete_bipartite_4_4,
    web_5_3,
    web_6_3,
    wagner_graph,
    moebius_ladder_10,
    desargues_graph,
    nauru_graph,
    durer_graph,
    cube_graph_q3,
    prism_10,
    generalized_petersen_7_2,
    gear_8,
    paley_13,
    overlapping_cliques,
    double_ring_with_chords,
    overlapped_ladders_with_diagonals,
    twin_wheels_overlap,
    clique_ring_bipart,
    overlapping_k4_chain,
    grid_3x4_braced_overlap,
    overlapping_bipartites,
]
