import time
from graph_io import *
from colorref import *
from copy import *


# main function, does all the steps necessary for the project
def main(path: str):
    if "grl" not in path:
        # opens singular graph and calculate the amount of automorphisms
        with open(path) as f:
            G = load_graph(f)
            return calculateAut(G)
    else:
        with open(path) as f:
            graphs = load_graph(f, read_list=True)[0]
        # get basic color refinement results
        refinedGraphs = basic_colorref(path)
        print(refinedGraphs)
        results = []
        for graphs in refinedGraphs:
            if graphs[3] or len(graphs[0]) <= 1:
                results.append(graphs[0])
            else:
                results += checkIsomorphism(graphs[0])
        if "Aut" in path:
            # if the file is an Aut file, calculate the automorphisms
            autResults = []
            for result in results:
                autResults.append((graphs[0], calculateAut(graphs[result[0][0]])))
            return autResults
        return graphs


# calculates the amount of automorphisms for a graph
def calculateAut(graph: Graph):
    setBase(graph)
    graph = colorrefPreColored([graph])
    if len(set([v.label for v in graph[0].vertices])) == len(graph[0].vertices):
        return 1
    else:
        return brancher(graph, 0)


# sets the colour of all vertices to it's base value
def setBase(graph: Graph):
    for vector in graph.vertices:
        vector.label = 0


def brancher(graph, checkIsomorphism):
    # TODO start branching
    pass


def countIsomorphism(graphG, graphH):
    colorsDict = {}
    counter = 0
    coloredGraphs = colorrefPreColored([graphG, graphH])
    for graph in coloredGraphs:
        for vertex in graph.vertices:
            color = vertex.label
            if color not in colorsDict:
                colorsDict[color] = [[], []]
            if vertex in graphG.vertices:
                colorsDict[color][0].append(vertex)
            else:
                colorsDict[color][1].append(vertex)

    # balanced or not
    for colorOfG, colorOfH in colorsDict.values():
        if len(colorOfG.vertices) != len(graphG.vertices):
            return 0

    # bijection or not
    if all(len(classG) == 1 for classG, classH in colorsDict.values()):
        return 1

    # choosing the color class with C>=4
    colorClass = None
    for color, (colorOfG, colorOfH) in colorsDict.items():
        if len(colorOfG) >= 4:
            colorClass = (colorOfG, colorOfH)
            break

    if not colorClass:
        return 0

    counter += brancher([graphG, graphH], 0)

    return counter


def checkIsomorphism(graphs: [Graph]):
    if len(graphs) == 2:
        if brancher(graphs, 1):
            return graphs
        return [[graphs[0]], [graphs[1]]]
    falseIsomorphism = {}
    correctIsomorphism = {}
    for graph in graphs:
        falseIsomorphism[graph] = set()
        correctIsomorphism[graph] = set()

    for graph1 in graphs:
        if len(correctIsomorphism[graph1]) > 0:
            continue
        for graph2 in graphs:
            if graph2 in falseIsomorphism[graph1]:
                break
            if brancher([graph1, graph2], 1):
                correctIsomorphism[graph1].add(graph2)
                correctIsomorphism[graph2].add(graph1)
                for graph3 in correctIsomorphism[graph2]:
                    correctIsomorphism[graph3].add(graph1)
                    correctIsomorphism[graph1].add(graph3)
            else:
                falseIsomorphism[graph1].add(graph2)
                falseIsomorphism[graph2].add(graph1)
                for graph3 in correctIsomorphism[graph2]:
                    falseIsomorphism[graph3].add(graph1)
                    falseIsomorphism[graph1].add(graph3)
    result = set()
    for graph in graphs:
        correctIsomorphism[graph].add(graph)
        result.add(correctIsomorphism[graph])
    return [result]


if __name__ == "__main__":
    startTime = time.time()
    print(main("Graphs/TestGraphs/basicGI1.grl"))
    endTime = time.time()
    totalTime = endTime - startTime
    print(f"Time was {totalTime} seconds")