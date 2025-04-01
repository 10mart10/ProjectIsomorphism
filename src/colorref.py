from graph_io import *
from collections import defaultdict, deque
import time
import sys
from line_profiler_pycharm import profile


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

    print(printResult)

    return result


#@profile
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


def refine(G, freq_map):
    queue = deque(freq_map.keys())
    iteration_count = 0

    while queue:
        color = queue.popleft()
        colorsThatChange = defaultdict()

        affected = defaultdict(list)
        for v in freq_map[color]:
            for n in v.neighbours:
                if n not in affected[n.label]:
                    affected[n.label].append(n)
                n.connections += 1

        for c, vertices in affected.items():
            connections = defaultdict(list)
            for v in freq_map[c]:
                connections[v.connections].append(v)
                v.connections = 0
            if len(connections) > 1:
                freq_map.pop(c)
                colorsThatChange[c] = defaultdict(list)
                for conn, vertices in connections.items():
                    colorsThatChange[c][conn] += vertices

        new_colors = {}
        if colorsThatChange:
            for c, connDict in colorsThatChange.items():
                notInQueue = c not in queue
                biggest = max(connDict, key=lambda x: len(connDict[x]))
                for conn, vertices in connDict.items():
                    if c in freq_map:
                        new_color = max(freq_map.keys()) + 1
                    else:
                        new_color = c
                    freq_map[new_color] = set(vertices)
                    new_colors[new_color] = vertices
                    for vertex in vertices:
                        vertex.label = new_color
                    if conn == biggest and notInQueue:
                        continue
                    queue.append(new_color)

        iteration_count += 1 if new_colors else 0

    return freq_map, iteration_count


def fast_colorref(path):
    with open(path, 'r') as f:
        data = load_graph(f, read_list=True)
    graphs = data[0]
    n_graphs = len(graphs)

    eq_classes = {}

    for g_idx, G in enumerate(graphs):
        freq_map = defaultdict(int)
        G.identifier = g_idx
        for i, v in enumerate(G.vertices):
            v.identifier = i
            v.label = 0
            v.connections = 0
            freq_map[v.label] += 1

    for j, G in enumerate(graphs):
        freq_map = {0: set(G.vertices)}
        stable_partition, iterations = refine(G, freq_map)
        sizes = sorted(len(v) for v in stable_partition.values())
        discrete = len(sizes) == len(G.vertices)

        key = tuple(sizes)
        if key not in eq_classes:
            eq_classes[key] = ([], sizes, iterations, discrete)

        eq_classes[key][0].append(j)

    result = [(idx_list, sorted(list(key)), iters, discrete) for idx_list, key, iters, discrete in
              eq_classes.values()]
    print(result)


if __name__ == "__main__":
    startTime = time.time()
    fast_colorref("Graphs/SampleGraphsBasicColorRefinement/colorref_smallexample_6_15.grl")
    endTime = time.time()
    totalTime = endTime - startTime
    print(f"Time was {totalTime} seconds")
