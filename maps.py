import requests
import json
import time
key = "Wcd1FBNSPohUGDC19NBhPTcISaWzF1uE"

dataFile = open("capitals.txt", "r")

data = dataFile.read().split('\n')

for i in range(len(data)):
    data[i] = data[i].split(' ')
    data[i] = [int(data[i][0]),",".join([data[i][1],data[i][2]])]

routes = []

coordinates = [0]*len(data)

coordinatesFile = open("coordinates.txt","w")

for (num,f) in data:
    f = f.replace(',',"%2C")
    url = "https://api.tomtom.com/search/2/poiSearch/{0}.json?key={1}".format(f,key)
    r = requests.get(url)
    result = json.loads(r.text)
    lat = result["results"][0]["position"]["lat"]
    lon = result["results"][0]["position"]["lon"]
    coordinates[num] = [lat,lon]
    print(num,lat,lon,file=coordinatesFile)

edges = open("edges.txt","r")

edgesList = []
for i in edges.read().split('\n'):
    edgesList.append([int(i.split()[0]),int(i.split()[1])])


for (numOne,numTwo) in edgesList:
    first = str(coordinates[numOne][0])+"%2c"+str(coordinates[numOne][1])
    second = str(coordinates[numTwo][0])+"%2c"+str(coordinates[numTwo][1])
    url = "https://api.tomtom.com/routing/1/calculateRoute/{0}%3A{1}/json?avoid=unpavedRoads&key={2}".format(first,second,key)
    r = requests.get(url)
    result = json.loads(r.text)
    try:
        routes.append( [numOne, numTwo, int(result["routes"][0]["summary"]["lengthInMeters"])/1000])
        print("Route between {0} and {1} success".format(numOne,numTwo))
    except:
        print("Fail, going sleep")
        time.sleep(5)
        r = requests.get(url)
        result = json.loads(r.text)
        try:   
            routes.append( [numOne, numTwo, int(result["routes"][0]["summary"]["lengthInMeters"])/1000])
            print("Route between {0} and {1} success".format(numOne,numTwo))
        except:
            print("Can't get route between {0} and {1}".format(numOne,numTwo))

resultFile = open("resultDistances.txt","w")
for i in routes:
    print(*i)
    print(*i,file=resultFile)
    

#url = "https://api.tomtom.com/search/2/poiSearch/{0}.json?key={1}".format(f,key)

#r = requests.get(url)

#print(r.text)

#result = json.loads(r.text)

#print(result["results"][0]["position"]["lat"])