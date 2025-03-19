import time
from graph_io import *
from graph import *
from colorref import *
from copy import *

from src.colorref import *


# main function, does all the steps necessary for the project
@profile
def main(path: str):
    if "grl" not in path:
        # opens singular graph and calculate the amount of automorphisms
        with open(path) as f:
            G = load_graph(f)
            return calculateAut(G)
    else:
        # get basic color refinement results
        refinedGraphs = basic_colorref(path)
        results = []
        for graphs in refinedGraphs:
            if graphs[3] or len(graphs[0]) <= 1:
                results.append(graphs[0])
            else:
                results += checkIsomorphism(graphs[0])
        # if "Aut" in path:
            # if the file is an Aut file, calculate the automorphisms
        autResults = []
        for result in results:
            autResults.append((sorted([graph.identifier for graph in result]),
                               calculateAut(result[0])))
        return autResults
        adIdentifier = []
        for result in results:
            adIdentifier.append(sorted([graph.identifier for graph in result]))
        return adIdentifier


# calculates the amount of automorphisms for a graph
@profile
def calculateAut(graph: Graph):
    setBase(graph)
    graphs = colorrefPreColored([graph])
    # if the graph is discrete return 1
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


# brancher function, does the branching for the calls count isomorphisms for all vectors of a certain color
@profile
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
    # Save the old colors
    colors = []
    for index in range(2):
        colors.append([v.label for v in graphs[index].vertices])
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
@profile
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
@profile
def calculateColorDict(coloredGraphs):
    colorsDict = {}
    for graph in coloredGraphs:
        for vertex in graph.vertices:
            color = vertex.label
            if color not in colorsDict:
                colorsDict[color] = []
            colorsDict[color].append(vertex)
    return colorsDict


# Given equivalence classes, check if they are isomorphic and return isomorphic classes as a list of lists
@profile
def checkIsomorphism(graphs: [Graph]):
    # if there are only two graphs, check if they are isomorphic
    if len(graphs) == 2:
        if brancher(graphs, 1):
            return [graphs]
        return [[graphs[0]], [graphs[1]]]
    # else check if they are isomorphic in pairs, and ensure that no graphs are checked unnecessarily
    # start by creating two dictionaries, one for false isomorphisms and one for correct isomorphisms
    falseIsomorphism = {}
    correctIsomorphism = {}
    for graph in graphs:
        falseIsomorphism[graph.identifier] = set()
        correctIsomorphism[graph.identifier] = set()

    # go over the graphs
    for graph1 in graphs:
        for graph2 in graphs:
            # if the graphs are already checked, directly or indirectly, skip them
            if graph1 in correctIsomorphism[graph2.identifier] or graph1 in falseIsomorphism[graph2.identifier]:
                continue
            if graph1 == graph2:
                continue
            # check if the graphs are isomorphic
            if brancher([graph1, graph2], 1):
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


# make a copy of a graph
@profile
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


if __name__ == "__main__":
    startTime = time.time()
    print(main("Graphs/SampleGraphSetBranching/cubes3.grl"))
    endTime = time.time()
    totalTime = endTime - startTime
    print(f"Time was {totalTime} seconds")
