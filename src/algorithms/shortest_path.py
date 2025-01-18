import sys
from itertools import permutations


# Floyd-Warshall com suporte para predecessores
def floyd_warshall_with_predecessors(adj_matrix):
    n = len(adj_matrix)
    dist = [[sys.maxsize] * n for _ in range(n)]
    pred = [[-1] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                dist[i][j] = 0
            elif adj_matrix[i][j] > 0:
                dist[i][j] = adj_matrix[i][j]
                pred[i][j] = i

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] != sys.maxsize and dist[k][j] != sys.maxsize:
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        pred[i][j] = pred[k][j]

    return dist, pred


# Reconstrói o caminho mínimo usando a matriz de predecessores
def reconstruct_path(pred, start, end):
    if pred[start][end] == -1:
        return None
    path = []
    while end != start:
        path.append(end)
        end = pred[start][end]
    path.append(start)
    path.reverse()
    return path


# Função para calcular o caminho mínimo com restrições de combustível
def find_path_with_fuel_limit(adj_matrix, start, mandatory, fuel_limit):
    dist, pred = floyd_warshall_with_predecessors(adj_matrix)
    best_path = None
    min_cost = sys.maxsize
    min_stops = sys.maxsize
    min_visited_stops = []

    for perm in permutations(mandatory):
        current_path = [start]
        current_fuel = 0
        total_cost = 0
        stops_count = 0
        visited_stops = []
        valid_path = True

        for i in range(len(perm)):
            next_vertex = perm[i]
            path_segment = reconstruct_path(pred, current_path[-1], next_vertex)

            if path_segment is None:
                valid_path = False
                break

            for j in range(1, len(path_segment)):

                weight = adj_matrix[path_segment[j - 1]][path_segment[j]]
                if current_fuel + weight > fuel_limit:
                    if current_path[-1] != path_segment[j - 1]:
                        current_path.append(path_segment[j - 1])
                    current_fuel = 0
                    stops_count += 1
                    visited_stops.append(path_segment[j - 1])

                current_path.append(path_segment[j])
                current_fuel += weight
                total_cost += weight

        if valid_path and current_fuel <= fuel_limit:
            if total_cost < min_cost:
                min_cost = total_cost
                min_stops = stops_count
                best_path = current_path
                min_visited_stops = visited_stops

    if best_path is None:
        return None, 0, 0
    return best_path, min_cost, min_visited_stops
