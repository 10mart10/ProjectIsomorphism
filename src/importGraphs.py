from graph import *
from basicpermutationgroup import Orbit, Stabilizer, Reduce, FindNonTrivialOrbit
from permv2 import *
from colorref import *

USE_FAST_ALGORITHM = True


def main(path: str, include_generators: bool = False):
    if "grl" not in path:
        with open(path) as f:
            G = load_graph(f)
            G.identifier = 0
            # if USE_FAST_ALGORITHM:
            #     graphs_refined = colorrefPreColoredFast([G])
            # else:
            #     graphs_refined = colorrefPreColored([G])

            aut_count = calculateAut(G)
            #aut_count = "aut broken"
            if include_generators:
                generators = update_generating_set(G, [], [])
                return aut_count, generators
            else:
                return aut_count
    else:
        if USE_FAST_ALGORITHM:
            refinedGraphs = fast_colorref(path)
        else:
            refinedGraphs = basic_colorref(path)

        results = []
        for graphs in refinedGraphs:
            if graphs[3] or len(graphs[0]) <= 1:
                results.append(graphs[0])
            else:
                results += checkIsomorphism(graphs[0])

        # if "Aut" in path:
        #     autResults = []
        #     for result in results:
        #         aut_count = calculateAut(result[0])
        #         if include_generators:
        #             generators = update_generating_set(result[0], [], [])
        #             autResults.append((sorted([graph.identifier for graph in result]),
        #                                aut_count,
        #                                generators))
        #         else:
        #             autResults.append((sorted([graph.identifier for graph in result]),
        #                                aut_count))
        #     return autResults

        adIdentifier = []
        for result in results:
            adIdentifier.append(sorted([graph.identifier for graph in result]))
        return adIdentifier


# calculates the amount of automorphisms for a graph
def calculateAut(graph: Graph):
    setBase(graph)
    if USE_FAST_ALGORITHM:
        _, graphs = colorrefPreColoredFast([graph])
    else:
        graphs = colorrefPreColored([graph])

    global X
    X = set()
    update_generating_set(graphs[0], [], [])
    print("Final generators:", [str(p) for p in X])
    print("Total:", len(X))


    generators = list(X)
    gens = Reduce(generators)

    # Check for trivial automorphism after reduction
    if len(gens) == 0 or (len(gens) == 1 and gens[0].istrivial()):
        print("Warning: Only trivial automorphism")

    print("Final generators 2:", [str(g) for g in gens])

    order = group_order(gens)
    print("Automorphism group order:", order)
    return order



# sets the colour of all vertices to it's base value
def setBase(graph: Graph):
    for i, vertex in enumerate(graph.vertices):
        vertex.label = len(vertex.neighbours)
        vertex.identifier = i


# brancher function, does the branching for the calls count isomorphisms for all vectors of a certain color
#@profile
def brancher(graphs, checkIsomorphism, colorsDict=None):
    if len(graphs) == 1:
        graphs.append(graphCopy(graphs[0]))
    if colorsDict is None:
        colorsDict = calculateColorDict(graphs)

    # Save the old colors
    colors = []
    for index in range(2):
        colors.append([v.label for v in graphs[index].vertices])

    # choosing the color class with C>=4
    colorClass = None
    for color, vectors in colorsDict.items():
        if len(vectors) >= 4:
            colorClass = color
            break
    newColor = max(colorsDict.keys()) + 1
    # set a random vector with color colorClass of graphG to the new color
    for vector in colorsDict[colorClass]:
        if vector in graphs[0].vertices:
            vector.label = newColor
            break
    # Save the basic color of graphG
    colors.append([v.label for v in graphs[0].vertices])
    counter = 0
    # set all vectors with color colorClass of graphH to the new color and count the isomorphisms
    for vector in colorsDict[colorClass]:
        if not vector in graphs[0].vertices:
            graphs[1].vertices[vector.identifier].label = newColor
            # call countIsomorphism for the new colors
            counter += countIsomorphism(graphs[0], graphs[1], checkIsomorphism, newColor)
            for vertice in range(len(graphs[1].vertices)):
                graphs[1].vertices[vertice].label = colors[1][vertice]
            # if you're looking for isomorphisms and you find one, return True
            if checkIsomorphism == 1 and (counter > 0 or counter):
                for vertice in range(len(graphs[0].vertices)):
                    graphs[0].vertices[vertice].label = colors[0][vertice]
                return True
            # reset the colours
            for vertice in range(len(graphs[1].vertices)):
                graphs[0].vertices[vertice].label = colors[2][vertice]
    for vertice in range(len(graphs[0].vertices)):
        graphs[0].vertices[vertice].label = colors[0][vertice]
    return counter


# countIsomorphism function, stops if it's unbalanced or bijection and increase by one if it's an isomorphism.
# If not it calls brancher to look deeper
#@profile
def countIsomorphism(graphG, graphH, checkIsomorphism, colors):
    if USE_FAST_ALGORITHM:
        val, coloredGraphs = colorrefPreColoredFast([graphG, graphH], colors)
        if val == 0:
            return 0
        if val == 1:
            return 1
        if val == 2:
            return brancher([graphG, graphH], checkIsomorphism)
    else:
        coloredGraphs = colorrefPreColored([graphG, graphH])

    colorsDict = calculateColorDict(coloredGraphs)
    graphGcolors = sorted([v.label for v in graphG.vertices])
    # balanced or not

    print(f"G labels: {[v.label for v in graphG.vertices]}")
    print(f"H labels: {[v.label for v in graphH.vertices]}")

    # Adjacency check (lightweight)
    print("G adjacency:")
    for v in graphG.vertices:
        print(f"{v.identifier}: {[n.identifier for n in v.neighbours]}")
    print("H adjacency:")
    for v in graphH.vertices:
        print(f"{v.identifier}: {[n.identifier for n in v.neighbours]}")


    if graphGcolors != sorted([v.label for v in graphH.vertices]):
        return 0
    # bijection or not
    if len(set(graphGcolors)) == len(graphGcolors):
        return 1

    return brancher([graphG, graphH], checkIsomorphism, colorsDict)


# create a dictionary with the colors as keys and the vectors with that color as values
#@profile
def calculateColorDict(coloredGraphs):
    colorsDict = defaultdict(list)
    for graph in coloredGraphs:
        for vertex in graph.vertices:
            colorsDict[vertex.label].append(vertex)
    return colorsDict


# Given equivalence classes, check if they are isomorphic and return isomorphic classes as a list of lists
#@profile
def checkIsomorphism(graphs: [Graph]):
    # if there are only two graphs, check if they are isomorphic
    if len(graphs) == 2:
        if brancher(graphs, 1):
            return [graphs]
        return [[graphs[0]], [graphs[1]]]
    # else check if they are isomorphic in pairs, and ensure that no graphs are checked unnecessarily
    # start by creating two dictionaries, one for false isomorphisms and one for correct isomorphisms
    falseIsomorphism = {graph.identifier: set() for graph in graphs}
    correctIsomorphism = {graph.identifier: {graph} for graph in graphs}

    # go over the graphs
    for graph1 in graphs:
        for graph2 in graphs:
            # if the graphs are already checked, directly or indirectly, skip them
            if graph1 in correctIsomorphism[graph2.identifier] or graph1 in falseIsomorphism[
                graph2.identifier]:
                continue
            if graph1 == graph2:
                continue
            # check if the graphs are isomorphic
            if brancher([graphCopy(graph1), graphCopy(graph2)], 1):
                # if they are, add them to the correct isomorphism dictionary and add all already known isomorphisms as well
                correctIsomorphism[graph1.identifier].add(graph2)
                correctIsomorphism[graph2.identifier].add(graph1)
                for graph3 in correctIsomorphism[graph2.identifier]:
                    correctIsomorphism[graph3.identifier].add(graph1)
                    correctIsomorphism[graph1.identifier].add(graph3)
                for graph3 in correctIsomorphism[graph1.identifier]:
                    correctIsomorphism[graph3.identifier].add(graph2)
                    correctIsomorphism[graph2.identifier].add(graph3)
            else:
                # if they aren't, add them to the false isomorphism dictionary and add all already known isomorphisms as well
                falseIsomorphism[graph1.identifier].add(graph2)
                falseIsomorphism[graph2.identifier].add(graph1)
                for graph3 in correctIsomorphism[graph2.identifier]:
                    falseIsomorphism[graph3.identifier].add(graph1)
                    falseIsomorphism[graph1.identifier].add(graph3)
                for graph3 in correctIsomorphism[graph1.identifier]:
                    falseIsomorphism[graph3.identifier].add(graph2)
                    falseIsomorphism[graph2.identifier].add(graph3)

    # create a list of the isomorphic classes in an unnecessarily complicated way
    unique_classes = {frozenset(group) for group in correctIsomorphism.values()}
    return [sorted(list(group), key=lambda x: x.identifier) for group in unique_classes]


# make a copy of a graph
#@profile
def graphCopy(graph: Graph):
    newGraph = Graph(False, 0)
    newGraph.identifier = graph.identifier
    for vertex in graph.vertices:
        v = Vertex(newGraph)
        v.identifier = vertex.identifier
        v.label = vertex.label
        newGraph += v
    for edge in graph.edges:
        e = Edge(newGraph.vertices[edge.tail.identifier], newGraph.vertices[edge.head.identifier])
        newGraph.add_edge(e)
    return newGraph


X = set()

def update_generating_set(G, D, I, depth=0, seen=None):
    global X
    MAX_DEPTH = 8
    if depth > MAX_DEPTH:
        return

    if seen is None:
        seen = set()

    mapping = build_full_mapping(len(G.vertices), D, I)
    if mapping is None:
        return


    mapping_tuple = tuple(mapping)
    if mapping_tuple in seen:
        return
    seen.add(mapping_tuple)


    if len(set(mapping)) != len(mapping):
        print("Invalid permutation — skipping")
        return

    try:
        perm = permutation(len(G.vertices), mapping=mapping)
        if not hasattr(G, "generators"):
            G.generators = set()
        if perm not in G.generators:
            print(f"Confirmed automorphism: {perm}")
            G.generators.add(perm)
    except Exception as e:
        print(f" Error: {e}")
        return

    G_permuted = graphCopy(G)

    if USE_FAST_ALGORITHM:
        _, refined_list = colorrefPreColoredFast([G_permuted])
        G_permuted = refined_list[0]
    else:
        G_permuted = colorrefPreColored([G_permuted])[0]

    is_auto = countIsomorphism(G, G_permuted, 1, max(v.label for v in G.vertices) + 1)

    if is_auto:
        if perm not in X:
            print(f"Confirmed automorphism: {perm}")
            X.add(perm)
        else:
            print(f" Duplicate automorphism: {perm}")
    else:
        print(f" Not an automorphism: {perm}")


    color_dict = calculateColorDict([G_permuted])

    for color, verts in color_dict.items():
        if len(verts) < 2:
            continue
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                d = verts[i].identifier
                i_ = verts[j].identifier

                if d in D or i_ in I:
                    continue

                update_generating_set(G, D + [d], I + [i_], depth + 1, seen)
                update_generating_set(G, D + [i_], I + [d], depth + 1, seen)


def group_order(generators):
    if not generators:
        return 1

    el = FindNonTrivialOrbit(generators)
    if el is None:
        return 1

    orbit = Orbit(generators, el)
    stab_generators = Stabilizer(generators, el)
    return len(orbit) * group_order(stab_generators)


def build_full_mapping(n, D, I):
    if len(D) != len(I):
        return None

    mapping = [-1] * n
    used_targets = set()

    for d, i in zip(D, I):
        if mapping[d] != -1 or i in used_targets:
            return None
        mapping[d] = i
        used_targets.add(i)

    remaining_targets = [i for i in range(n) if i not in used_targets]
    unmapped_positions = [i for i, m in enumerate(mapping) if m == -1]

    if len(unmapped_positions) != len(remaining_targets):
        return None

    for i, pos in enumerate(unmapped_positions):
        mapping[pos] = remaining_targets[i]

    if len(set(mapping)) != n:
        return None

    return mapping



#@profile
def run_all(directory: str):
    total = 0
    file_num = 0
    for filename in os.listdir(directory):
        if filename.endswith(".grl") or filename.endswith(".gr"):
            file_path = os.path.join(directory, filename)
            start = time.time()
            print(f"Processing {filename}...")
            try:
                result = main(file_path)
                print(f"Result for {filename}: {result}")
            except Exception as e:
                print(f"Error {filename}: {e}")
            end = time.time()
            time_taken = end - start
            total += time_taken
            file_num += 1
            print(f"Time taken for {filename}: {time_taken:.4f} seconds\n")

    print(f"Total time: {total:.4f} seconds")
    print(file_num)



if __name__ == "__main__":
    startTime = time.time()
    print(main("Graphs/TestGraphs/basicAut1.gr"))
    endTime = time.time()
    totalTime = endTime - startTime
    print(f"Time was {totalTime} seconds")

    # directory_path = "Graphs/TestGraphs"
    # run_all(directory_path)