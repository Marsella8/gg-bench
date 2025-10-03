from dsl.dsl import parse_program, get_program_cost
from dsl.graph_dsl import (
    cycle_graph,
    union_graphs,
    path_graph,
    shift_graph,
    complete_graph,
    remove_edges,
    add_edges,
    connect_one_to_all,
    union_map,
    numerical_range,
)


def p1():
    g1 = cycle_graph(0, 10)
    g2 = cycle_graph(10, 20)
    g3 = cycle_graph(20, 30)
    g4 = union_graphs(g1, g2, g3)
    return g4


def test_p1():
    program = parse_program(p1)
    correct = 9  # 2 + 2 + 2 + 3
    output = get_program_cost(program)
    assert output == correct


def p2():
    g1 = path_graph(0, 6)
    g2 = shift_graph(g1, 6)
    g3 = union_graphs(g1, g2)
    return g3


def test_p2():
    program = parse_program(p2)
    correct = 6  # 2 + 2 + 2
    output = get_program_cost(program)
    assert output == correct


def p3():
    g1 = complete_graph(0, 5)
    g2 = complete_graph(5, 10)
    g = union_graphs(g1, g2)
    g = add_edges(g, (4, 9))
    return g


def test_p3():
    program = parse_program(p3)
    correct = 8  # 2 + 2 + 2 + 2
    output = get_program_cost(program)
    assert output == correct


def p4():
    g1 = complete_graph(0, 6)
    g2 = remove_edges(g1, (0, 3), (1, 4), (2, 5))
    return g2


def test_p4():
    program = parse_program(p4)
    correct = 6  # 2 + 4
    output = get_program_cost(program)
    assert output == correct


def p5():
    g = union_map(
        numerical_range(5), lambda i: connect_one_to_all(0, 2 * i + 1, 2 * i + 2)
    )
    return g


def test_p5():
    program = parse_program(p5)
    correct = 5  # 1 + (1 + 3)
    output = get_program_cost(program)
    assert output == correct


def p6():
    outer = cycle_graph(5)
    inner = cycle_graph(5, 10)
    g = union_graphs(outer, inner)
    g = add_edges(g, (4, 5), (1, 6), (3, 7), (0, 8), (2, 9))
    return g


def test_p6():
    program = parse_program(p6)
    correct = 11  # 1 + 2 + 2 + 6
    output = get_program_cost(program)
    assert output == correct


def p7():
    left = path_graph(0, 6)
    right = path_graph(6, 12)
    single_rung = path_graph(0, 12, 6)
    rungs = union_map(numerical_range(1, 5), lambda k: shift_graph(single_rung, k))
    g = union_graphs(left, right, rungs)
    return g


def test_p7():
    program = parse_program(p7)
    correct = 15  # 2 + 2 + 3 + (2 + (1+2)) + 3
    output = get_program_cost(program)
    assert output == correct


def p8():
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


def test_p8():
    program = parse_program(p8)
    correct = 18  # 1 + 2 + 2 + 4 + 4 + 5
    output = get_program_cost(program)
    assert output == correct


def p9():
    outer = cycle_graph(8)
    inner = union_map(
        numerical_range(8), lambda i: connect_one_to_all(i + 8, ((i + 3) % 8) + 8)
    )
    spokes = union_map(numerical_range(8), lambda i: connect_one_to_all(i, i + 8))
    return union_graphs(outer, inner, spokes)


def test_p9():
    program = parse_program(p9)
    correct = 12  # 1 + 4 + 4 + 3
    output = get_program_cost(program)
    assert output == correct


def p10():
    ring = cycle_graph(12)
    spokes = union_map(numerical_range(0, 12, 2), lambda k: connect_one_to_all(12, k))
    return union_graphs(ring, spokes)


def test_p10():
    program = parse_program(p10)
    correct = 9  # 1 + (3 + (1+2)) + 2
    output = get_program_cost(program)
    assert output == correct


def p11():
    c1 = cycle_graph(8)
    c2 = shift_graph(c1, 8)
    rungs = union_map(numerical_range(8), lambda i: connect_one_to_all(i, i + 8))
    return union_graphs(c1, c2, rungs)


def test_p11():
    program = parse_program(p11)
    correct = 10  # 1 + 2 + 4 + 3
    output = get_program_cost(program)
    assert output == correct


def p12():
    c = cycle_graph(8)
    g = add_edges(c, (0, 4), (1, 5), (2, 6), (3, 7))
    return g


def test_p12():
    program = parse_program(p12)
    correct = 6  # 1 + (1 + 4)
    output = get_program_cost(program)
    assert output == correct


def p13():
    c1 = cycle_graph(7)
    c2 = shift_graph(c1, 7)
    rungs = union_map(numerical_range(7), lambda i: connect_one_to_all(i, i + 7))
    return union_graphs(c1, c2, rungs)


def test_p13():
    program = parse_program(p13)
    correct = 10  # 1 + 2 + (1 + (1 + 2)) + 3
    output = get_program_cost(program)
    assert output == correct


def p14():
    rim = cycle_graph(5)
    hub = connect_one_to_all(5, 0, 1, 2, 3, 4)
    wheel = union_graphs(rim, hub)
    pendants = union_map(numerical_range(5), lambda i: connect_one_to_all(i, 6 + i))
    return union_graphs(wheel, pendants)


def test_p14():
    program = parse_program(p14)
    correct = 15  # 1 + 6 + 2 + (1 + (1 + 2)) + 2
    output = get_program_cost(program)
    assert output == correct


def p15():
    base = cycle_graph(14)
    chords = union_map(
        numerical_range(14), lambda i: connect_one_to_all(i, (i + 5) % 14)
    )
    return union_graphs(base, chords)


def test_p15():
    program = parse_program(p15)
    correct = 7  # 1 + (1 + (1 + 2)) + 2
    output = get_program_cost(program)
    assert output == correct


def p16():
    outer = cycle_graph(6)
    inner = union_map(
        numerical_range(6), lambda i: connect_one_to_all(6 + i, ((i + 2) % 6) + 6)
    )
    spokes = union_map(numerical_range(6), lambda i: connect_one_to_all(i, i + 6))
    return union_graphs(outer, inner, spokes)


def test_p16():
    program = parse_program(p16)
    correct = 12  # 1 + (1 + (1 + 2)) + (1 + (1 + 2)) + 3
    output = get_program_cost(program)
    assert output == correct


def p17():
    outer = cycle_graph(9)
    inner = union_map(
        numerical_range(9), lambda i: connect_one_to_all(9 + i, ((i + 2) % 9) + 9)
    )
    spokes = union_map(numerical_range(9), lambda i: connect_one_to_all(i, i + 9))
    return union_graphs(outer, inner, spokes)


def test_p17():
    program = parse_program(p17)
    correct = 12  # 1 + 4 + 4 + 3
    output = get_program_cost(program)
    assert output == correct


def p18():
    return union_map(numerical_range(3), lambda i: connect_one_to_all(i, 3, 4, 5, 6, 7))


def test_p18():
    program = parse_program(p18)
    correct = 8  # 1 + (1 + 5)
    output = get_program_cost(program)
    assert output == correct


def p19():
    left = path_graph(0, 6)
    right = path_graph(6, 12)
    rungs = union_map(numerical_range(6), lambda i: connect_one_to_all(i, i + 6))
    return union_graphs(left, right, rungs)


def test_p19():
    program = parse_program(p19)
    correct = 11  # 2 + 2 + (1 + (1 + 2)) + 3
    output = get_program_cost(program)
    assert output == correct


def p20():
    r1 = cycle_graph(6)
    r2 = shift_graph(r1, 6)
    r3 = shift_graph(r2, 6)
    s12 = union_map(numerical_range(6), lambda i: connect_one_to_all(i, i + 6))
    s23 = union_map(numerical_range(6), lambda i: connect_one_to_all(i + 6, i + 12))
    return union_graphs(r1, r2, r3, s12, s23)


def test_p20():
    program = parse_program(p20)
    correct = 18  # 1 + 2 + 2 + 4 + 4 + 5
    output = get_program_cost(program)
    assert output == correct


def p21():
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
        cube0,
        (0, 8),
        (1, 9),
        (2, 10),
        (3, 11),
        (4, 12),
        (5, 13),
        (6, 14),
        (7, 15),
    )
    return union_graphs(cube1, bridge)


def test_p21():
    program = parse_program(p21)
    correct = 28  # 2 + 4 + 9 + 2 + 9 + 2
    output = get_program_cost(program)
    assert output == correct
