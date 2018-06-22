var WORLD_SIZE = 100;
var CITIES_COUNT = 26;
var CITY_POSSIBLE_NEIGHBOR_COUNT = 5;
var CITY_MIN_NEIGHBORS = 1;
var CITY_MAX_NEIGHBORS = 4;
var RANDOM_MAP_LAT = '-25.3449154';
var RANDOM_MAP_LNG = '-49.1854728';
var RANDOM_MAP_RADIUS = '300';


var totalNodesVisited = 0;
var totalNodesGenerated = 0;
var totalTime = 0;
var totalPathLength = 0;
var totalProblemsSolved = 0;
var depth = 0;

function GeoNamesIntegrator () {
  function normalizeToWorldSize (cities) {
    let lats = [];
    let lngs = [];
    for (let city of cities) {
      lats.push(city.lat);
      lngs.push(city.lng);
    }
    let maxLat = lats.reduce(function(a, b) { return Math.max(a, b) });
    let minLat = lats.reduce(function(a, b) { return Math.min(a, b) });
    let maxLng = lngs.reduce(function(a, b) { return Math.max(a, b) });
    let minLng = lngs.reduce(function(a, b) { return Math.min(a, b) });
    cities.map((city) => {
      city.lat = Math.max(Math.floor(((city.lat - minLat) / (maxLat - minLat)) * 100), 1);
      city.lng = Math.max(Math.floor(((city.lng - minLng) / (maxLng - minLng)) * 100), 1);
    })
  }

  function httpGetAsync (theUrl, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
        callback(xmlHttp.responseText);
    };
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
  }

  function getNearbyCitiesByCoordinates (lat, lng, limit, callback) {
    httpGetAsync('http://api.geonames.org/findNearbyPlaceNameJSON?lat=' +lat + '&lng=' + lng +
      '&style=short&radius=' + RANDOM_MAP_RADIUS + '&maxRows=' + limit + '&username=giancarlokc', (result) => {
      console.log('GeoName API result:', result);
      let cities = JSON.parse(result).geonames;
      cities = cities.map((city) => { return { lat: city.lat, lng: city.lng } });
      if (callback) callback(cities)
    })
  }

  function getNearbyCities (lat, lng, limit, callback) {
    getNearbyCitiesByCoordinates(lat, lng, limit, (cities) => {
      normalizeToWorldSize(cities);
      if (callback) callback(cities)
    })
  }

  return { getNearbyCities: getNearbyCities }
}

function ParameterCollector () {
  function get (id) { return document.getElementById(id).value }

  function collect () {
    CITIES_COUNT = get('city-count') || CITIES_COUNT;
    RANDOM_MAP_LAT = get('real-map-lat') || RANDOM_MAP_LAT;
    RANDOM_MAP_LNG = get('real-map-lng') || RANDOM_MAP_LNG;
    RANDOM_MAP_RADIUS = get('real-map-radius') || RANDOM_MAP_RADIUS;
  }

  return { collect: collect }
}

function startSimulation (citiesFromMap = null) {

  function getPathLength (cities, path) {
    if (!path || path.length < 2) return 0;
    let length = 0;
    for (let i=1; i<path.length; i++) {
      length += euclideanDistance(cities.find((city) => city.id === path[i-1]), cities.find((city) => city.id === path[i]))
    }
    return length;
  }

  // Greedy Best-First Search functions ######################################################### //

  function performGreedyBestFirstSearch (cities, startCity, endCity, heuristic) {
    let heuristicFunction;
    switch (heuristic) {
      case 'euclidean': heuristicFunction = euclideanHeuristic; break;
      case 'constant': heuristicFunction = constantHeuristic; break;
      case 'manhattan': heuristicFunction = manhattanHeuristic; break;
    }
    let pathFound = greedyBestFirstSearch(cities, startCity, endCity, heuristicFunction);
    console.log('   GBF path:', pathFound ? pathFound.map((cityId => idToLabel(cityId))) : 'NOT FOUND', '( Using', heuristic, ')')
  }
  function greedyBestFirstSearch (cities, currentCity, endCity, heuristicFunction, visitedCities = [], path = [], currentDepth = 0) {
    currentCity = cities.find((city) => city.id === currentCity);
    endCity = cities.find((city) => city.id === endCity);

    path.push(currentCity.id);
    visitedCities.push(currentCity.id);

    if (currentCity.id === endCity.id){
      return path;
    }

    let possibleNodes = currentCity.paths
    .map((neighbor) => {
      neighbor = cities.find((city) => city.id === neighbor);
      neighbor.score = heuristicFunction(neighbor, endCity);
      return neighbor;
    })
    .filter((neighbor) => !visitedCities.find(id => id === neighbor.id))
    .sort((a, b) => a.score - b.score);

    for(let city of possibleNodes) {
      let foundPath = greedyBestFirstSearch(cities, city.id, endCity.id, heuristicFunction, visitedCities, path, currentDepth++);
      if (foundPath) return foundPath;
    }

    return false;
  }

  // A* Search functions ######################################################### //

  function performAStarSearch (cities, startCity, endCity, heuristic) {
    let heuristicFunction;
    switch (heuristic) {
      case 'euclidean': heuristicFunction = euclideanHeuristic; break;
      case 'constant': heuristicFunction = constantHeuristic; break;
      case 'manhattan': heuristicFunction = manhattanHeuristic; break;
    }
    let pathFound = aStarSearch(cities, startCity, endCity, heuristicFunction);
    console.log('   A* path:', pathFound ? pathFound.map((cityId => idToLabel(cityId))) : 'NOT FOUND', '( Using', heuristic, ')')
  }
  function aStarSearch (cities, startCity, endCity, heuristicFunction) {
    startCity = cities.find((city) => city.id === startCity);
    endCity = cities.find((city) => city.id === endCity);
    let closedSet = [];
    let openSet = [ startCity.id ];
    let cameFrom = {};

    let gScore = {};
    gScore[startCity.id] = 0;

    let fScore = {};
    fScore[startCity.id] = heuristicFunction(startCity, endCity);

    while (openSet.length > 0) {
      let lowToHighFScore = Object.entries(fScore).filter((score) => openSet.find(id => id === Number(score[0]))).sort((a, b) => a[1] - b[1]);
      let current = Number(lowToHighFScore[0][0]);
      if (current === endCity.id) {
        nodesGenerated = nodesGenerated + (closedSet.length || 0) + (cameFrom.length || 0) + (gScore.length || 0) + (fScore.length || 0);
        return recoverAStarSearchPath(cameFrom, current)
      };

      openSet.splice(openSet.findIndex((id) => id === current), 1);
      closedSet.push(current);

      for (let neighbor of cities.find((city) => city.id === current).paths) {
        neighbor = cities.find((city) => city.id === neighbor);

        if (closedSet.findIndex((id) => id === neighbor.id) > -1) continue;

        if (openSet.findIndex((id) => id === neighbor.id) < 0) {
          openSet.push(neighbor.id);
        }

        // The distance from start to a neighbor
        //the "dist_between" function may vary as per the solution requirements.
        let tentative_gScore = gScore[current] + euclideanDistance(cities.find((city) => city.id === current), neighbor);
        if (tentative_gScore >= gScore[neighbor.id]) continue;

        // This path is the best until now. Record it!
        cameFrom[neighbor.id] = current;
        gScore[neighbor.id] = tentative_gScore;
        fScore[neighbor.id] = gScore[neighbor.id] + heuristicFunction(neighbor, endCity);
      }
    }

    return false
  }
  function recoverAStarSearchPath (cameFrom, current) {
    let total_path = [ current ];
    while (Object.keys(cameFrom).find(id => Number(id) === current)) {
      current = cameFrom[current];
      total_path.unshift(current)
    }
    return total_path
  }
  function constantHeuristic () {
    return 0;
  }
  function euclideanHeuristic (a, b) {
    return euclideanDistance(a, b)
  }
  function manhattanHeuristic (a, b) {
    let distX = (a.x - b.x) < 0 ? (b.x - a.x) : (a.x - b.x);
    let distY = (a.y - b.y) < 0 ? (b.y - a.y) : (a.y - b.y);
    return Math.abs(distX) + Math.abs(distY);
  }

  // Iterative Deepening Depth First Search functions ######################################################### //

  function performIterativeDepthFirstSearch (cities, startCity, endCity) {
    depth = 0;
    let pathFound;
    for (let i=0; i<cities.length; i++) {
      pathFound = depthFirstSearch(cities, startCity, endCity, [], [], 1, i + 1);
      if (pathFound) break;
    }
    totalPathLength += getPathLength(cities, pathFound);
    console.log('Path length:', totalPathLength);
    totalProblemsSolved += pathFound.length ? 1 : 0;
    nodesGenerated = depth;
    console.log('   IDDFS path:', pathFound ? pathFound.map((cityId => idToLabel(cityId))) : 'NOT FOUND')
  }

  // Depth First Search functions ######################################################### //

  function performDepthFirstSearch (cities, startCity, endCity) {
    depth = 0;
    let pathFound = depthFirstSearch(cities, startCity, endCity);
    totalPathLength += getPathLength(cities, pathFound);
    console.log('Path length:', totalPathLength);
    totalProblemsSolved += pathFound.length ? 1 : 0;
    nodesGenerated = depth;
    console.log('   DFS path:', pathFound ? pathFound.map((cityId => idToLabel(cityId))) : 'NOT FOUND')
  }
  function depthFirstSearch (cities, currentCity, endCity, path = [], visited = [], currentDepth = 1, maxDepth = Infinity) {
    numberOfNodes++;
    if (currentDepth > depth) {
      depth = currentDepth;
    }
    // Mark city as visited and update path
    visited.push(currentCity);
    path = path.concat(currentCity);

    // Check if reached endCity
    if (currentCity === endCity) {
      return path;
    }

    if (currentDepth >= maxDepth) return false;

    // If not, then go to next city
    for (let neighbor of cities.find((city) => city.id === currentCity).paths) {
      if (!visited.includes(neighbor)) {
        let pathFound = depthFirstSearch(cities, neighbor, endCity, path, visited, currentDepth + 1, maxDepth);
        if (pathFound) return pathFound
      }
    }

    return false
  }

  // Breadth First Search functions ######################################################### //

  function performBreadthFirstSearch (cities, startCity, endCity) {
    depth = 0;
    let pathFound = breadthFirstSearch(cities, startCity, endCity);
    totalPathLength += getPathLength(cities, pathFound);
    console.log('Path length:', totalPathLength);
    console.log('   BFS path:', pathFound ? pathFound.map((cityId => idToLabel(cityId))) : 'NOT FOUND')
    nodesGenerated = depth;
  }
  function recoverBreadthFirstSearchPath (endCity, dict) {
    // console.log('recoverBreadthFirstSearchPath');
    // console.log('endCity', endCity);
    // console.log('dict', dict);
    let path = [];
    let currentCity = endCity;
    path.unshift(currentCity);
    while (true) {
      currentCity = dict[currentCity];
      if (currentCity === undefined) return path;
      path.unshift(currentCity);
    }
  }
  function breadthFirstSearch (cities, startCity, endCity) {
    let queue = [ startCity ];
    let visited = [];
    let dict = {};

    while (queue.length > 0) {
      if (queue.length > depth) {
        depth = queue.length;
      }
      numberOfNodes++;
      let currentCity = queue.shift();

      // Check if reached endCity
      if (currentCity === endCity) {
        return recoverBreadthFirstSearchPath(endCity, dict);
      }

      // Put neighbors in stack
      for (let neighbor of cities.find((city) => city.id === currentCity).paths) {
        if (visited.includes(neighbor) || queue.includes(neighbor)) continue;
        queue.push(neighbor);
        dict[neighbor] = currentCity;
      }

      // Mark city as visited
      visited.push(currentCity);
    }

    return false
  }

  // City functions ######################################################### //

  function generateCity (id, label, x, y) {
    return {
      id: id,
      label: label,
      x: x !== undefined ? x : Math.floor(Math.random() * (WORLD_SIZE)),
      y: y !== undefined ? y : Math.floor(Math.random() * (WORLD_SIZE))
    }
  }

  function generateCities (citiesFromMap) {
    var cityList = [];
    if (citiesFromMap) {
      for (let i=0; i<citiesFromMap.length; i++) {
        cityList.push(generateCity(i+1, idToLabel(i+1), citiesFromMap[i].lat, citiesFromMap[i].lng))
      }
    } else {
      for (let i = 1; i <= CITIES_COUNT; i++) {
        cityList.push(generateCity(i, idToLabel(i)))
      }
    }
    return cityList;
  }

  // Path functions ######################################################### //

  function euclideanDistance (a, b) {
    return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2))
  }

  function nearestNeighbors (city, cities, nNeighbors) {
    return cities.slice().sort(function (a, b) {
      return euclideanDistance(city, a) - euclideanDistance(city, b)
    }).slice(1, nNeighbors + 1);
  }

  function connectCities (from, to, cities) {
    let fromCity = cities.find(city => city.id === from);
    if (!fromCity.paths) {
      fromCity.paths = []
    }

    let toCity = cities.find(city => city.id === to);
    if (!toCity.paths) {
      toCity.paths = []
    }

    fromCity.paths.push(toCity.id);
    toCity.paths.push(fromCity.id);
  }

  function generateCityPaths (cities) {
    return cities.map(function (city) {
      // Get the 5 closest neighbors
      var closestNeighbors = nearestNeighbors(city, cities, CITY_POSSIBLE_NEIGHBOR_COUNT);

      // Randomly select [1, 4] of them
      var nRandomNeighbors = Math.floor(Math.random() * Math.min(closestNeighbors.length, (CITY_MAX_NEIGHBORS - CITY_MIN_NEIGHBORS))) + CITY_MIN_NEIGHBORS;
      for (var i=0; i<nRandomNeighbors; i++) {
        var randomIndex = Math.floor(Math.random() * closestNeighbors.length);
        connectCities(city.id, closestNeighbors.splice(randomIndex, 1)[0].id, cities);
      }
      return city;
    })
  }

  // UI specific functions ######################################################### //

  function idToLabel (id) {
    return String.fromCharCode(96 + id).toUpperCase();
  }

  function normalizeCitiesToUI (cities) {
    return cities.map(function (city) {
      city.x = city.x * 10;
      city.y = city.y * 10;
      return city
    });
  }

  function hasEdge (edge, edges) {
    edges.findIndex((e) => (e.from === edge.from && e.to === edge.to) || (e.from === edge.to && e.to === edge.from))
  }

  function computeEdges (cities) {
    var edges = [];
    for (var city of cities) {
      for (var path of city.paths) {
        // Check if path already exists
        var edge = {from: city.id, to: path};
        if (!hasEdge(edge, edges)) edges.push(edge);
      }
    }
    return edges;
  }

  function renderSimulation (simulation) {
    // create an array with nodes
    var cities = normalizeCitiesToUI(simulation.cities);
    var nodes = new vis.DataSet(cities);

    // create an array with edges
    var computedEdges = computeEdges(cities);
    var edges = new vis.DataSet(computedEdges);

    // create a network
    var container = document.getElementById('mynetwork');

    // provide the data in the vis format
    var data = { nodes: nodes, edges: edges };
    var options = { nodes: { fixed: { x: true, y: true }, widthConstraint: 20, heightConstraint: 20, shape: 'box' } };

    // initialize your network!
    new vis.Network(container, data, options);
  }

  // Simulation functions ######################################################### //

  function createSimulation (citiesFromMap) {
    var cities = generateCities(citiesFromMap);
    console.log('Cities:', cities);
    cities = generateCityPaths(cities);
    return { cities: cities };
  }

  console.log('Starting simulation');

  // Collect input from UI
  let cityCountInput = document.getElementById('city-count').value;
  if (cityCountInput) CITIES_COUNT = cityCountInput;

  var simulation = createSimulation(citiesFromMap);

  // Select 2 different cities for path search
  var startCity = Math.floor(Math.random() * simulation.cities.length) + 1;
  var endCity = startCity;
  while (startCity === endCity) {
    endCity = Math.floor(Math.random() * simulation.cities.length) + 1;
  }
  console.log('Search path:', idToLabel(startCity), '->', idToLabel(endCity));

  // console.log('# DFS ###########');
  //
  // // Perform path search using Depth-First Search
  var numberOfNodes = 0;
  var nodesGenerated = 0;
  let startTimeDFS = performance.now();
  performDepthFirstSearch(simulation.cities, startCity, endCity);
  let endTimeDFS = performance.now();
  let time = endTimeDFS - startTimeDFS;
  console.log('   DFS time:', time, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);
  totalTime += time;
  totalNodesVisited += numberOfNodes;
  totalNodesGenerated += nodesGenerated;

  //console.log('# BFS ###########');

  // // Perform path search using Breadth-First Search
  // numberOfNodes = 0;
  // nodesGenerated = 0;
  // let startTimeBFS = performance.now();
  // performBreadthFirstSearch(simulation.cities, startCity, endCity);
  // let endTimeBFS = performance.now();
  // console.log('   BFS time:', endTimeBFS - startTimeBFS, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);
  //
  //console.log('# IDDFS ###########');

  // Perform path search using Iterative Depth First Search
  // numberOfNodes = 0;
  // nodesGenerated = 0;
  // let startTimeIDDFS = performance.now();
  // performIterativeDepthFirstSearch(simulation.cities, startCity, endCity);
  // let endTimeIDDFS = performance.now();
  // console.log('   BFS time:', endTimeIDDFS - startTimeIDDFS, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);
  //
  //console.log('# A* ###########');

  // Perform path search using A* Search
  // numberOfNodes = 0;
  // nodesGenerated = 0;
  // let startTimeAStar = performance.now();
  // performAStarSearch(simulation.cities, startCity, endCity, 'euclidean');
  // let endTimeAStar = performance.now();
  // console.log('   A* time:', endTimeAStar - startTimeAStar, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);
  //
  // Perform path search using A* Search
  // numberOfNodes = 0;
  // nodesGenerated = 0;
  // let startTimeAStar = performance.now();
  // performAStarSearch(simulation.cities, startCity, endCity, 'constant');
  // let endTimeAStar = performance.now();
  // console.log('   A* time:', endTimeAStar - startTimeAStar, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);
  //
  // Perform path search using A* Search
  // numberOfNodes = 0;
  // nodesGenerated = 0;
  // let startTimeAStar = performance.now();
  // performAStarSearch(simulation.cities, startCity, endCity, 'manhattan');
  // let endTimeAStar = performance.now();
  // console.log('   A* time:', endTimeAStar - startTimeAStar, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);
  //
  // console.log('# GBF ###########');
  //
  // Perform path search using Greedy Best-First Search
  // numberOfNodes = 0;
  // nodesGenerated = 0;
  // let startTimeAStar = performance.now();
  // performGreedyBestFirstSearch(simulation.cities, startCity, endCity, 'euclidean');
  // let endTimeAStar = performance.now();
  // console.log('   GBF time:', endTimeAStar - startTimeAStar, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);
  //
  // Perform path search using Greedy Best-First Search
  // numberOfNodes = 0;
  // nodesGenerated = 0;
  // let startTimeAStar = performance.now();
  // performGreedyBestFirstSearch(simulation.cities, startCity, endCity, 'constant');
  // let endTimeAStar = performance.now();
  // console.log('   GBF time:', endTimeAStar - startTimeAStar, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);
  //
  // // Perform path search using Greedy Best-First Search
  // let startTimeAStar = performance.now();
  // performGreedyBestFirstSearch(simulation.cities, startCity, endCity, 'manhattan');
  // let endTimeAStar = performance.now();
  // console.log('   GBF time:', endTimeAStar - startTimeAStar, 'milliseconds | Number of nodes:', numberOfNodes, '| Complexity:', nodesGenerated);

  // Render world
  renderSimulation(simulation);

  console.log('\n');
}

// UI setup
function handleRandomMapSimulation () {
  ParameterCollector().collect();
  totalNodesVisited = 0;
  totalNodesGenerated = 0;
  totalTime = 0;
  totalPathLength = 0;
  totalProblemsSolved = 0;
  for(let i=0; i<100; i++) {
    startSimulation()
  }
  console.log('totalNodesVisited:', totalNodesVisited/100);
  console.log('totalNodesGenerated:', totalNodesGenerated/100);
  console.log('totalTime:', totalTime/100);
  console.log('totalPathLength:', totalPathLength/100);
  console.log('totalProblemsSolved:', totalProblemsSolved);
}
function handleRealMapSimulation () {
  ParameterCollector().collect();
  GeoNamesIntegrator().getNearbyCities(RANDOM_MAP_LAT, RANDOM_MAP_LNG, CITIES_COUNT, (cities) => {
    startSimulation(cities);
  });
}

document.addEventListener('DOMContentLoaded', function () {
  // Simulate Random Map
  var simulateButton = document.getElementById('simulate');
  simulateButton.onclick = function () { handleRandomMapSimulation() };

  // Simulate Real Map
  var simulateRealMap = document.getElementById('simulaterealmap');
  simulateRealMap.onclick = () => { handleRealMapSimulation() };
});