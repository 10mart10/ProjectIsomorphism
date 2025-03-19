import time
import os
from graph_io import *
from graph import *
from colorref import *
from multiprocessing import Pool, Queue, Process, Value
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
    amountOfProcesses = Value('i', 0)
    # if the graph is discrete return 1
    if len(set([v.label for v in graphs[0].vertices])) == len(graphs[0].vertices):
        return 1
    else:
        return brancher(graphs, 0, amountOfProcesses)


# sets the colour of all vertices to it's base value
def setBase(graph: Graph):
    i = 0
    for vector in graph.vertices:
        vector.label = 0
        vector.identifier = i
        i += 1


# brancher function, does the branching for the calls count isomorphisms for all vectors of a certain color
@profile
def brancher(graphs, checkIsomorphism, amountOfProcesses, colorsDict=None):
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
    # set a random vector with color colorClass of graphG to the new color
    for vector in colorsDict[colorClass]:
        if vector in graphs[0].vertices:
            vector.label = len(colorsDict)
            break
    counter = 0
    queue = Queue()
    processes = []
    # set all vectors with color colorClass of graphH to the new color and count the isomorphisms
    for vector in colorsDict[colorClass]:
        if not vector in graphs[0].vertices:
            graphG = graphCopy(graphs[0])
            graphH = graphCopy(graphs[1])
            graphH.vertices[vector.identifier].label = len(colorsDict)
            # call countIsomorphism for the new colors
            if amountOfProcesses.value < 10:
                amountOfProcesses.value += 1
                p = Process(target=queue.put, args=(countIsomorphism(graphG, graphH, checkIsomorphism, amountOfProcesses),))
                p.start()
                processes.append(p)
            else:
                counter += countIsomorphism(graphG, graphH, checkIsomorphism, amountOfProcesses)
            # if you're looking for isomorphisms and you find one, return True
            if checkIsomorphism == 1 and (counter > 0 or counter):
                return True
    for p in processes:
        p.join()
        amountOfProcesses.value -= 1
    while not queue.empty():
        counter += queue.get()
    return counter


# countIsomorphism function, stops if it's unbalanced or bijection and increase by one if it's an isomorphism.
# If not it calls brancher to look deeper
@profile
def countIsomorphism(graphG, graphH, checkIsomorphism, amountOfProcesses):
    coloredGraphs = colorrefPreColored([graphG, graphH])
    colorsDict = calculateColorDict(coloredGraphs)
    graphGcolors = sorted([v.label for v in graphG.vertices])
    # balanced or not
    if graphGcolors != sorted([v.label for v in graphH.vertices]):
        return 0
    # bijection or not
    if len(set(graphGcolors)) == len(graphGcolors):
        print("+1")
        return 1

    return brancher([graphG, graphH], checkIsomorphism, amountOfProcesses, colorsDict=colorsDict)


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
        toPoolOver = []
        for graph2 in graphs:
            # if the graphs are already checked, directly or indirectly, skip them
            if graph1 in correctIsomorphism[graph2.identifier] or graph1 in falseIsomorphism[graph2.identifier]:
                continue
            if graph1 == graph2:
                continue
            toPoolOver.append((graph1, graph2))
        if not toPoolOver:
            continue
        with Pool(processes=len(toPoolOver)) as pool:
            results = pool.starmap(GIMultiProcessing, toPoolOver)
            for i, result in enumerate(results):
                graph2 = toPoolOver[i][1]
                if result:
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


def GIMultiProcessing(graph1, graph2,):
    # check if the graphs are isomorphic
    return graph2, brancher([graphCopy(graph1), graphCopy(graph2)], 1)




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

@profile
def run_all(directory: str):
    total = 0
    file_num = 0
    for filename in os.listdir(directory):
        if filename.endswith(".grl"):
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

    #directory_path = "Graphs/LastYearTests"
    #run_all(directory_path)
