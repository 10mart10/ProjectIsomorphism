import time
from graph_io import *
from colorref import *


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
        results = basic_colorref(path)
        if "Aut" in path:
            # if the file is an Aut file, calculate the automorphisms
            autResults = []
            for result in results:
                autResults.append((result[0], calculateAut(graphs[result[0][0]])))
            return autResults
        return results


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


def countIsomorphism(graph, checkIsomorphism):
    # TODO count the amount of isomorphisms
    pass

if __name__ == "__main__":
    startTime = time.time()
    print(main("Graphs/TestGraphs/basicAut1.gr"))
    endTime = time.time()
    totalTime = endTime - startTime
    print(f"Time was {totalTime} seconds")