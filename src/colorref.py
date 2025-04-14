from graph_io import *
import os
from collections import defaultdict, deque
import time
import sys
from line_profiler import profile


#@profile
def basic_colorref(path: str) -> list:
    with open(path, 'r') as f:
        data = load_graph(f, read_list=True)
    graphs = data[0]
    n_graphs = len(graphs)

    for j, G in enumerate(graphs):
        for i, v in enumerate(G.vertices):
            v.label = len(v.neighbours)
            v.identifier = i
        G.identifier = j

    initially_stable = {}

    for g_idx, G in enumerate(graphs):
        freq_map = defaultdict(int)
        for v in G.vertices:
            freq_map[v.label] += 1

        neighbor_signatures = set(
            tuple(sorted(n.label for n in v.neighbours)) for v in G.vertices
        )

        initially_stable[g_idx] = (len(neighbor_signatures) == 1)

    stable_iteration = {g_idx: None for g_idx in range(n_graphs)}
    previous_freq_maps = [{} for _ in range(n_graphs)]

    iteration = 0
    while True:
        iteration += 1

        signature_map = {}
        for G in graphs:
            for v in G.vertices:
                neighbor_colors = sorted(n.label for n in v.neighbours)
                signature_map[v] = (v.label, tuple(neighbor_colors))

        new_labels = {}
        next_color = 0
        for v in signature_map:
            sig = signature_map[v]
            if sig not in new_labels:
                new_labels[sig] = next_color
                next_color += 1
            v.label = new_labels[sig]

        for g_idx, G in enumerate(graphs):

            freq_map = defaultdict(int)
            for v in G.vertices:
                freq_map[v.label] += 1

            sorted_freq = tuple(sorted(freq_map.values()))

            if sorted_freq == previous_freq_maps[g_idx] and stable_iteration[g_idx] is None:
                stable_iteration[g_idx] = iteration

            previous_freq_maps[g_idx] = sorted_freq

        if all(stable_iteration[g] is not None for g in range(n_graphs)):
            break

    eq_class_signatures = {}

    for g_idx, G in enumerate(graphs):
        freq_map = defaultdict(int)
        color_signature = []

        for v in G.vertices:
            freq_map[v.label] += 1
            color_signature.append(v.label)

        sizes = sorted(freq_map.values())
        discrete = len(sizes) == len(G.vertices) and all(s == 1 for s in sizes)

        class_signature = (
            tuple(sizes),
            tuple(sorted(color_signature)),
            0 if initially_stable[g_idx] else stable_iteration[g_idx],
            discrete
        )

        eq_class_signatures[g_idx] = class_signature

    eq_classes = defaultdict(list)

    for g_idx, signature in eq_class_signatures.items():
        eq_classes[signature].append(graphs[g_idx])

    result = [(idx_list, len(list(key[0])), key[2], key[3]) for key, idx_list in eq_classes.items()]
    printResult = []
    for key, idx_list in eq_classes.items():
        printResult.append(
            (sorted([g.identifier for g in idx_list]), sorted(list(key[0])), key[2], key[3]))

    # print(printResult)

    return result


#@profile
def colorrefPreColored(graphs):
    n_graphs = len(graphs)
    initially_stable = {}

    for g_idx, G in enumerate(graphs):
        freq_map = defaultdict(int)
        for v in G.vertices:
            freq_map[v.label] += 1

        neighbor_signatures = set(
            tuple(sorted(n.label for n in v.neighbours)) for v in G.vertices
        )

        initially_stable[g_idx] = (len(neighbor_signatures) == 1)

    stable_iteration = {g_idx: None for g_idx in range(n_graphs)}
    previous_freq_maps = [{} for _ in range(n_graphs)]

    iteration = 0
    while True:
        iteration += 1

        signature_map = {}
        for G in graphs:
            for v in G.vertices:
                neighbor_colors = sorted(n.label for n in v.neighbours)
                signature_map[v] = (v.label, tuple(neighbor_colors))

        new_labels = {}
        next_color = 0
        for v in signature_map:
            sig = signature_map[v]
            if sig not in new_labels:
                new_labels[sig] = next_color
                next_color += 1
            v.label = new_labels[sig]

        for g_idx, G in enumerate(graphs):

            freq_map = defaultdict(int)
            for v in G.vertices:
                freq_map[v.label] += 1

            sorted_freq = tuple(sorted(freq_map.values()))

            if sorted_freq == previous_freq_maps[g_idx] and stable_iteration[g_idx] is None:
                stable_iteration[g_idx] = iteration

            previous_freq_maps[g_idx] = sorted_freq

        if all(stable_iteration[g] is not None for g in range(n_graphs)):
            break
    return graphs

@profile
def colorrefPreColoredFast(graphs, color=None):
    freq_map = defaultdict(set)

    for G in graphs:
        for v in G.vertices:
            v.connections = 0
            freq_map[v.label].add(v)

    _,iterations = refine(None, freq_map, color)

    eq_classes = {}
    for G in graphs:

        freq_map_local = defaultdict(int)
        for v in G.vertices:
            freq_map_local[v.label] += 1
        sizes = sorted(freq_map_local.values())
        discrete = len(sizes) == len(G.vertices) and all(s == 1 for s in sizes)

        vertex_profiles = sorted(
            (v.label, tuple(sorted(n.label for n in v.neighbours)))
            for v in G.vertices
        )

        key = (
            tuple(sizes),
            tuple(vertex_profiles),
            iterations,
            discrete
        )

        if key not in eq_classes:
            eq_classes[key] = ([], sizes, iterations, discrete)
        eq_classes[key][0].append(G.identifier)
    if len(eq_classes) > 1:
        return 0, graphs
    if discrete:
        return 1, graphs

    return 2, graphs


@profile
def refine(G, freq_map, color=None):
    if color is None:
        queue = deque(freq_map.keys())
    else:
        queue = deque([color])
    iteration_count = 0
    color_id = max(freq_map.keys()) + 1

    while queue:
        color = queue.popleft()
        affected = defaultdict(set)

        for v in freq_map[color]:
            for n in v.neighbours:
                affected[n.label].add(n)
                n.connections += 1

        to_split = []
        for c, vertices in affected.items():
            buckets = defaultdict(set)
            for v in freq_map[c]:
                buckets[v.connections].add(v)
                v.connections = 0
            if len(buckets) > 1:
                to_split.append((c, buckets))

        for c, buckets in to_split:
            del freq_map[c]
            bucket_keys = sorted(buckets.keys(), key=lambda k: (-len(buckets[k]), k))


            used_color = False

            for conn in bucket_keys:
                if not used_color:
                    new_color = c
                    used_color = True
                else:
                    new_color = color_id
                    color_id += 1

                freq_map[new_color] = set(buckets[conn])
                for v in buckets[conn]:
                    v.label = new_color

                if new_color != c:
                    queue.append(new_color)

            iteration_count += 1

    return freq_map, iteration_count


@profile
def fast_colorref(path):
    with open(path, 'r') as f:
        data = load_graph(f, read_list=True)
    graphs = data[0]

    all_vertices = []
    for G in graphs:
        G.identifier = graphs.index(G)
        for i, v in enumerate(G.vertices):
            v.label = len(v.neighbours)
            v.connections = 0
            v.identifier = i
            all_vertices.append(v)

    freq_map = defaultdict(set)
    for v in all_vertices:
        freq_map[v.label].add(v)

    _, iterations = refine(None, freq_map)

    eq_classes = {}
    for G in graphs:

        freq_map_local = defaultdict(int)
        for v in G.vertices:
            freq_map_local[v.label] += 1
        sizes = sorted(freq_map_local.values())
        discrete = len(sizes) == len(G.vertices) and all(s == 1 for s in sizes)

        vertex_profiles = sorted(
            (v.label, tuple(sorted(n.label for n in v.neighbours)))
            for v in G.vertices
        )

        key = (
            tuple(sizes),
            tuple(vertex_profiles),
            iterations,
            discrete
        )

        if key not in eq_classes:
            eq_classes[key] = ([], sizes, iterations, discrete)
        eq_classes[key][0].append(G.identifier)

    printResult = [(sorted(idx_list), len(sizes), iters, discrete) for idx_list, sizes, iters, discrete in
                   eq_classes.values()]
    # print(printResult)

    result = [(list(graphs[i] for i in sorted(idx_list)), sizes, iters, discrete) for
              idx_list, sizes, iters, discrete in eq_classes.values()]

    return result


if __name__ == "__main__":
    path = "Graphs/SampleGraphsBasicColorRefinement/colorref_largeexample_6_960.grl"
    startTime = time.time()
    print(fast_colorref(path))
    endTime = time.time()
    totalTime = endTime - startTime
    print(f"Time was {totalTime} seconds")
    # startTime = time.time()
    # print(basic_colorref(path))
    # endTime = time.time()
    # totalTime = endTime - startTime
    # print(f"Time was {totalTime} seconds")