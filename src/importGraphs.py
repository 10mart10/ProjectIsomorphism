import time
from graph_io import *
from graph import *
from colorref import *
from copy import *

from src.colorref import *


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
        adIdentifier = []
        for result in results:
            adIdentifier.append(sorted([graph.identifier for graph in result]))
        return adIdentifier


# calculates the amount of automorphisms for a graph
def calculateAut(graph: Graph):
    setBase(graph)
    graphs = colorrefPreColored([graph])
    if len(set([v.label for v in graphs[0].vertices])) == len(graphs[0].vertices):
        return 1
    else:
        return brancher(graphs, 0)


# sets the colour of all vertices to it's base value
def setBase(graph: Graph):
    i = 0
    for vector in graph.vertices:
        vector.label = 0
        vector.identifier = i
        i += 1


def brancher(graphs, checkIsomorphism, colorsDict=None):
    if len(graphs) == 1:
        graphs.append(graphCopy(graphs[0]))
    if colorsDict is None:
        colorsDict = calculateColorDict(graphs)

    # choosing the color class with C>=4
    colorClass = None
    for color, vectors in colorsDict.items():
        if len(vectors) >= 4:
            colorClass = color
            break
    for vector in colorsDict[colorClass]:
        if vector in graphs[0].vertices:
            vector.label = len(colorsDict)
            break
    counter = 0
    for vector in colorsDict[colorClass]:
        if not vector in graphs[0].vertices:
            graphG = graphCopy(graphs[0])
            graphH = graphCopy(graphs[1])
            graphH.vertices[vector.identifier].label = len(colorsDict)
            counter += countIsomorphism(graphG, graphH, checkIsomorphism)
            if checkIsomorphism == 1 and (counter > 0 or counter):
                return True
    return counter


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


def calculateColorDict(coloredGraphs):
    colorsDict = {}
    for graph in coloredGraphs:
        for vertex in graph.vertices:
            color = vertex.label
            if color not in colorsDict:
                colorsDict[color] = []
            colorsDict[color].append(vertex)
    return colorsDict


def checkIsomorphism(graphs: [Graph]):
    if len(graphs) == 2:
        if brancher(graphs, 1):
            return [graphs]
        return [[graphs[0]], [graphs[1]]]
    falseIsomorphism = {}
    correctIsomorphism = {}
    for graph in graphs:
        falseIsomorphism[graph.identifier] = set()
        correctIsomorphism[graph.identifier] = set()

    for graph1 in graphs:
        for graph2 in graphs:
            if graph1 in correctIsomorphism[graph2.identifier] or graph1 in falseIsomorphism[graph2.identifier]:
                continue
            if graph1 == graph2:
                continue
            if brancher([graph1, graph2], 1):
                correctIsomorphism[graph1.identifier].add(graph2)
                correctIsomorphism[graph2.identifier].add(graph1)
                for graph3 in correctIsomorphism[graph2.identifier]:
                    correctIsomorphism[graph3.identifier].add(graph1)
                    correctIsomorphism[graph1.identifier].add(graph3)
                for graph3 in correctIsomorphism[graph1.identifier]:
                    correctIsomorphism[graph3.identifier].add(graph2)
                    correctIsomorphism[graph2.identifier].add(graph3)
            else:
                falseIsomorphism[graph1.identifier].add(graph2)
                falseIsomorphism[graph2.identifier].add(graph1)
                for graph3 in correctIsomorphism[graph2.identifier]:
                    falseIsomorphism[graph3.identifier].add(graph1)
                    falseIsomorphism[graph1.identifier].add(graph3)
                for graph3 in correctIsomorphism[graph1.identifier]:
                    falseIsomorphism[graph3.identifier].add(graph2)
                    falseIsomorphism[graph2.identifier].add(graph3)
    tempResult = []
    for graph in graphs:
        correctIsomorphism[graph.identifier].add(graph)
        tempResult.append(list(correctIsomorphism[graph.identifier]))
    result = []
    for graphs in tempResult:
        graphs.sort(key=lambda x: x.identifier)
        if graphs not in result:
            result.append(graphs)
    return result


def graphCopy(graph: Graph):
    newGraph = Graph(False, 0)
    for vertex in graph.vertices:
        v = Vertex(newGraph)
        v.identifier = vertex.identifier
        v.label = vertex.label
        newGraph += v
    for edge in graph.edges:
        e = Edge(newGraph.vertices[edge.tail.identifier], newGraph.vertices[edge.head.identifier])
        newGraph += e
    return newGraph



if __name__ == "__main__":
    startTime = time.time()
    print(main("Graphs/TestGraphs/basicGI2.grl"))
    endTime = time.time()
    totalTime = endTime - startTime
    print(f"Time was {totalTime} seconds")
