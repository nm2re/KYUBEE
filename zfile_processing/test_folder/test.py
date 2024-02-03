import heapq
from random import randrange


def dijkstra(graph, start):
    # Initialize distances and predecessors
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    predecessors = {node: None for node in graph}

    # Priority queue to store (distance, node) pairs
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Check if current path is shorter than stored distance
        if current_distance > distances[current_node]:
            continue

        # Explore neighbors
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            # Update distance and predecessor if a shorter path is found
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, predecessors

def get_shortest_paths(predecessors, start):
    shortest_paths = {}
    for node in predecessors:
        if node == start:
            continue
        path = []
        current_node = node
        while current_node is not None:
            path.insert(0, current_node)
            current_node = predecessors[current_node]
        shortest_paths[node] = {"path": path, "distance": distances[node]}
    return shortest_paths

# Example usage:
# graph = {
#     'A': {'B': 1, 'D': 3, 'E': 5, 'F': 8},
#     'B': {'A': 1, 'C': 2, 'D': 4, 'E': 6, 'F': 9},
#     'C': {'B': 2, 'D': 5, 'E': 7, 'F': 10},
#     'D': {'A': 3, 'B': 4, 'C': 5, 'E': 8, 'F': 11},
#     'E': {'D': 2, 'F': 3, 'A': 5, 'B': 6, 'C': 7},
#     'F': {'C': 1, 'E': 3, 'A': 8, 'B': 9, 'D': 11}
# }

graph = {}

for LETTER in range(ord("A"), ord("Z")+1):
    inside = {}
    for count in range(randrange(1,26)):
        inside[chr(randrange(ord('A'),ord("Z")+1))] = randrange(1,800)
    graph[chr(LETTER)] = inside
    print(chr(LETTER),inside)



start_node = 'D'
distances, predecessors = dijkstra(graph, start_node)

# Get and print shortest paths
shortest_paths = get_shortest_paths(predecessors, start_node)
for node, data in shortest_paths.items():
    print(f'Shortest path from {start_node} to {node}: {data["path"]}, Distance: {data["distance"]}')
