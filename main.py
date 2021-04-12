from igraph import *
import codecs
import networkx as nx

# http://graphonline.ru/?graph=PwDAJuJcAiDEkSaU

# http://graphonline.ru/?graph=hfwGjbVrfsMzucrg

def addEdge(one,two,graph, edgesList,weight=-1):
    if ([one,two] in edgesList) or ([two,one] in edgesList):
        return
    if (weight==-1):
        edgesList.append([one,two])
    else:
        edgesList.append([one,two,weight])
    graph.add_edges([(one,two)])

def loadCountries(g, gw,filename):
    with open(filename, "r") as countries:
        for countrie in countries.read().split("\n"):
            number, name = countrie.split(".")
            number = int(number)
            g.vs[number]["label"] = name
            gw.vs[number]["label"] = name

def loadMapper(mapper):
    with codecs.open("mapper.txt", encoding="utf-8") as mapList:
        for i in mapList.read().replace("\r","").split('\n'):
            ls = i.split(" ")
            number = int(ls.pop(0))
            mapper[number] = ls[0]
            for variant in ls:
                mapper[variant] = number

def loadBordersRaw(graph,edgesList,filename):
    with codecs.open(filename,encoding="utf-8") as borders:
        for i in borders.read().replace("\r","").split('\n'):
            ls = i.split(",")
            fNum = mapper[ls.pop(0)]
            for j in ls:
                to = j.strip().split(' ')[0]
                tNum = mapper[to]
                addEdge(fNum,tNum,g,edgesList)

def loadBordersPrepaired(graph, graphW, edgesList, edgesListW, filename):
    with open(filename,"r") as distances:
        weight = []
        for i in distances.read().split("\n"):
            (f,t,w) = i.split()
            f = int(f)
            t = int(t)
            w = float(w)
            weight.append(w)
            addEdge(f,t,graph,edgesList)
            addEdge(f,t,graphW,edgesListW, weight=w)
        gw.es["weight"] = weight
        gw.es["label"] = weight

def calculateDegrees(edgesList, V):
    degrees = [0] * V
    for (f,t) in edgesList:
        degrees[f]+=1
        degrees[t]+=1
    return degrees

def getMatrix(edgesList,V):
    matrix = []
    for i in range(V):
        matrix.append([0]*V)
    for i in edgesList:
        matrix[i[0]][i[1]] = 1
        matrix[i[1]][i[0]] = 1
    return matrix

def getEdgesListStructured(edgesList,V):
    edgesListStructured = []
    for i in range(V):
        edgesListStructured.append([])
    for i in edgesList:
        edgesListStructured[i[0]].append(i[1])
        edgesListStructured[i[1]].append(i[0])
    return edgesListStructured

def getEpsilonList(edgesListStructured, V):
    epsilonList = [0]*V
    for i in range(V):
        used = [0]*V

        def Bfs(num, edgesListStructured, n):
            used[num] = 1
            q = [num]
            iterations = [0]*V
            while 0 in used:
                current = q.pop(0)
                for i in edgesListStructured[current]:
                    if used[i]==0:
                        used[i] = 1
                        q.append(i)
                        iterations[i] = iterations[current]+1
            return max(iterations)
        n = Bfs(i,edgesListStructured,0)
        epsilonList[i] = n
    return epsilonList

def getBranchW(node, ignoreNode, edges):
    curW = 0
    for i in edges:
        if node in i and not ignoreNode in i:
            secNode = -1
            if node==i[0]:
                secNode = i[1]
            else:
                secNode = i[0]
            curW+=getBranchW(secNode,node,edges)
    return curW+1


V = 42
Vfull = 47

g = Graph()
g.add_vertices(42)

gw = Graph()
gw.add_vertices(42)

gFull = Graph()
gFull.add_vertices(47)

gFullW = Graph()
gFullW.add_vertices(47)

mapper = dict()
edgesList = []
edgesListW = []

edgesListFull = []
edgesListFullW = []

loadCountries(g,gw, "europe.txt")
loadMapper(mapper)
loadBordersPrepaired(g,gw,edgesList,edgesListW, "distances.txt")

loadCountries(gFull,gFullW, "europeExtra.txt")
loadBordersPrepaired(gFull,gFullW,edgesListFull,edgesListFullW, "distancesExtra.txt")

ng = nx.Graph()
ng.add_nodes_from(range(V))
ng.add_edges_from(edgesList)

ngFull = nx.Graph()
ngFull.add_nodes_from(range(Vfull))
ngFull.add_edges_from(edgesListFull)

matrixFile = open("matrix.txt","w")

matrix = getMatrix(edgesList,V)

for i in matrix:
    print(*i,file=matrixFile)
matrixFile.close()

E = len(edgesList)

resultFile = open("result.txt","w")

degrees = calculateDegrees(edgesList, V)

sigma = min(degrees)
delta = max(degrees)

edgesListStructured = getEdgesListStructured(edgesList,V)

epsilonsList = getEpsilonList(edgesListStructured, V)

radius = min(epsilonsList)
diameter = max(epsilonsList)

girth = g.girth()

center = []
centerNums = []
for i in range(V):
    if epsilonsList[i] == radius:
        center.append(mapper[i])
        centerNums.append(str(i))

maxClique = max(g.cliques(), key=len)

independentVertexSet = g.largest_independent_vertex_sets()[0]

matching = nx.maximal_matching(ng)

used = []

pathThroughtAllEdges = nx.eulerian_circuit(nx.eulerize(ng))

vertexBiconnectedComponents = list(nx.biconnected_components(ngFull))

edgeBiconnectedComponents = list(nx.k_edge_components(ngFull,2))

maxBiconnectedComponent = max(vertexBiconnectedComponents,key=len)

maxBiconnectedCompEdges = [i for i in edgesList if i[0] in maxBiconnectedComponent and i[1] in maxBiconnectedComponent]

# print(maxBiconnectedCompEdges)

ngW = nx.Graph()

for i in edgesListW:
    ngW.add_edge(i[0],i[1], weight=i[2])

minSpanningTree = nx.minimum_spanning_tree(ngW)

treeFile = open("tree.dot","w")
print("graph {",file=treeFile)

treeNodes = minSpanningTree.nodes
treeEdges = minSpanningTree.edges
for i in treeNodes:
    print("{};".format(i),file=treeFile)
for i in treeEdges:
    print("{} -- {};".format(i[0],i[1]),file=treeFile)

print("}",file=treeFile)

treeW = dict()

for i in treeNodes:
    for j in treeEdges:
        if not i in j:
            continue
        secNode = -1
        if i==j[0]:
            secNode = j[1]
        else:
            secNode = j[0]
        brW = getBranchW(secNode,i,treeEdges)
        if (not i in treeW.keys()) or treeW[i]<brW:
            treeW[i] = brW 

treeCentroid = []

centroidVal = min(treeW.values())

for i in treeW.keys():
    if treeW[i] == centroidVal:
        treeCentroid.append(i)

curN = 0
labels = dict()
for i in minSpanningTree.nodes:
    if not i in labels.keys():
        labels[i] = curN
        curN+=1

revLabels = dict()

for i in labels.keys():
    to = labels[i]
    revLabels[to] = i

minSpanningTree = nx.relabel_nodes(minSpanningTree,labels)

pruferCode = nx.to_prufer_sequence(minSpanningTree)

pruferCode = [revLabels[i] for i in pruferCode]

print("V - "+str(V), file=resultFile)
print("E - "+str(E), file=resultFile)
print("Sigma - "+str(sigma), file=resultFile)
print("Delta - "+str(delta), file=resultFile)
print("Rad - "+str(radius), file=resultFile)
print("Diam - "+ str(diameter), file=resultFile)
print("Center - {"+", ".join(center)+"} {"+", ".join(centerNums)+"}", file=resultFile)
print("Girth - {0}".format(girth), file=resultFile) #Graph is simple, so no self-loops, no multiple edges, so no loops with len 2, example of loop wwith len 3: Norway - Sweden - Finland
print("k - 1", file=resultFile) #If you delete Italy, you will get 2 components: Vatican and other
print("lambda - 1", file=resultFile) #If you delete edge between Italy and Vatican, you will get 2 components: Vatican and other
print("Maximum clique - {0}".format(maxClique), file=resultFile) #Graph is planar, so there are no Clique with size 5 or more
#clicue - https://en.wikipedia.org/wiki/Kuratowski%27s_theorem

print("Maximum stable set - {0}".format(g.largest_independent_vertex_sets()[0]), file=resultFile)
print("Maximum matching - {0}".format(matching), file=resultFile)

print("Shortest closed path throught all edges - {0}".format(list(pathThroughtAllEdges)), file=resultFile)

print("2-vertex-connected components - {0}".format(vertexBiconnectedComponents), file=resultFile)
print("2-edge-connected components - {0}".format(edgeBiconnectedComponents), file=resultFile)

print("Centroid - {}".format(treeCentroid),file=resultFile)

print("Prufer code - {0}".format(pruferCode),file=resultFile)

resultFile.close()

g.write("graph.dot")
gw.write("graphW.dot")

gFull.write("graphFull.dot")
