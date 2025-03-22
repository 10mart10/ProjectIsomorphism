
from importGraphs import *
from collections import defaultdict
import time
from line_profiler_pycharm import profile


@profile
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

    final_info = []
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
    # print(result)

    return result



@profile
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

