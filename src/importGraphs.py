import time
import os
from graph_io import *
from graph import *
from colorref import *
from copy import *
from basicpermutationgroup import Orbit, Stabilizer, Reduce
from permv2 import *
from collections import deque

from colorref import *


# main function, does all the steps necessary for the project
#@profile
# def main(path: str):
#     if "grl" not in path:
#         # opens singular graph and calculate the amount of automorphisms
#         with open(path) as f:
#             G = load_graph(f)
#             return calculateAut(G)
#     else:
#         # get basic color refinement results
#         refinedGraphs = basic_colorref(path)
#         # refinedGraphs = fast_colorref(path)
#
#         results = []
#         for graphs in refinedGraphs:
#             if graphs[3] or len(graphs[0]) <= 1:
#                 results.append(graphs[0])
#             else:
#                 results += checkIsomorphism(graphs[0])
#         if "Aut" in path:
#             # if the file is an Aut file, calculate the automorphisms
#             autResults = []
#             for result in results:
#                 autResults.append((sorted([graph.identifier for graph in result]),
#                                    calculateAut(result[0])))
#             return autResults
#         adIdentifier = []
#         for result in results:
#             adIdentifier.append(sorted([graph.identifier for graph in result]))
#         return adIdentifier

def main(path: str, include_generators: bool = False):
    if "grl" not in path:
        with open(path) as f:
            G = load_graph(f)
            aut_count = calculateAut(G)

            if include_generators:
                generators = update_generating_set(G)
                return aut_count, generators
            else:
                return aut_count
    else:
        refinedGraphs = basic_colorref(path)

        results = []
        for graphs in refinedGraphs:
            if graphs[3] or len(graphs[0]) <= 1:
                results.append(graphs[0])
            else:
                results += checkIsomorphism(graphs[0])

        if "Aut" in path:
            autResults = []
            for result in results:
                aut_count = calculateAut(result[0])
                if include_generators:
                    generators = update_generating_set(result[0])
                    autResults.append((sorted([graph.identifier for graph in result]),
                                       aut_count,
                                       generators))
                else:
                    autResults.append((sorted([graph.identifier for graph in result]),
                                       aut_count))
            return autResults

        adIdentifier = []
        for result in results:
            adIdentifier.append(sorted([graph.identifier for graph in result]))
        return adIdentifier


# calculates the amount of automorphisms for a graph
#@profile
# def calculateAut(graph: Graph):
#     setBase(graph)
#     graphs = colorrefPreColored([graph])
#     # if the graph is discrete return 1
#     if len(set([v.label for v in graphs[0].vertices])) == len(graphs[0].vertices):
#         return 1
#     return brancher(graphs, 0)

def calculateAut(graph: Graph):
    setBase(graph)
    graphs = colorrefPreColored([graph])
    if len(set([v.label for v in graphs[0].vertices])) == len(graphs[0].vertices):
        return 1

    global X
    X = set()
    update_generating_set(graphs[0], [], [])

    generators = list(X)
    generators = Reduce(generators)

    return group_order(generators)


# sets the colour of all vertices to it's base value
#@profile
def setBase(graph: Graph):
    for i, vertex in enumerate(graph.vertices):
        vertex.label = 0
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
    # set a random vector with color colorClass of graphG to the new color
    for vector in colorsDict[colorClass]:
        if vector in graphs[0].vertices:
            vector.label = len(colorsDict)
            break
    # Save the basic color of graphG
    colors.append([v.label for v in graphs[0].vertices])
    counter = 0
    # set all vectors with color colorClass of graphH to the new color and count the isomorphisms
    for vector in colorsDict[colorClass]:
        if not vector in graphs[0].vertices:
            graphs[1].vertices[vector.identifier].label = len(colorsDict)
            # call countIsomorphism for the new colors
            counter += countIsomorphism(graphs[0], graphs[1], checkIsomorphism)
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
def countIsomorphism(graphG, graphH, checkIsomorphism):
    coloredGraphs = colorrefPreColored([graphG, graphH])
    colorsDict = calculateColorDict(coloredGraphs)
    graphGcolors = sorted([v.label for v in graphG.vertices])
    # balanced or not
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
            if graph1 in correctIsomorphism[graph2.identifier] or graph1 in falseIsomorphism[graph2.identifier]:
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
    for vertex in graph.vertices:
        v = Vertex(newGraph)
        v.identifier = vertex.identifier
        v.label = vertex.label
        newGraph += v
    for edge in graph.edges:
        e = Edge(newGraph.vertices[edge.tail.identifier], newGraph.vertices[edge.head.identifier])
        newGraph.add_edge(e)
    return newGraph

def apply_initial_coloring(graph, D, I):
    new_graph = graphCopy(graph)
    for color, (d_id, i_id) in enumerate(zip(D, I)):
        for v in new_graph.vertices:
            if v.identifier == d_id or v.identifier == i_id:
                v.label = len(new_graph.vertices) + color + 1
    return new_graph


X = set()

def update_generating_set(G, D, I):
    global X
    if len(D) > 10:
        return

    mapping = list(range(len(G.vertices)))
    for d, i in zip(D, I):
        mapping[d] = i
    mapping = build_full_mapping(len(G.vertices), D, I)
    if mapping is None:
        return
    perm = permutation(len(G.vertices), mapping=mapping)

    if perm in X:
        return
    X.add(perm)


    G_colored = apply_initial_coloring(G, D, I)
    G_refined = colorrefPreColored([G_colored])[0]

    labels = [v.label for v in G_refined.vertices]
    if sorted(labels) != sorted([v.label for v in G.vertices]):
        return

    if len(set(labels)) == len(labels):
        mapping = list(range(len(G.vertices)))
        for d, i in zip(D, I):
            mapping[d] = i
        perm = permutation(len(G.vertices), mapping=mapping)
        if not any(p == perm for p in X):
            X.add(perm)
        return


    color_dict = calculateColorDict([G_refined])
    C = next((v_list for v_list in color_dict.values() if len(v_list) >= 2), None)
    if not C:
        return

    for i, x in enumerate(C):
        for j, y in enumerate(C):
            if j <= i:
                continue
            update_generating_set(G, D + [x.identifier], I + [y.identifier])


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
    mapping = list(range(n))
    used_targets = set()

    for d, i in zip(D, I):
        if i in used_targets:
            return None
        mapping[d] = i
        used_targets.add(i)

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

    #directory_path = "Graphs/TestGraphs"
    #run_all(directory_path)
