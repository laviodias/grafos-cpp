import sys
from itertools import permutations

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

def find_path_with_fuel_limit(adj_matrix, start, mandatory, fuel_limit):
    dist, pred = floyd_warshall_with_predecessors(adj_matrix)
    best_path = None
    min_cost = sys.maxsize
    min_stops = sys.maxsize
    min_visited_stops = []
    reason = None

    all_nodes = set(range(len(adj_matrix)))
    refuel_nodes = list(all_nodes - set(mandatory) - {start})

    for perm in permutations(mandatory):
        current_path = [start]
        current_fuel = 0
        total_cost = 0
        stops_count = 0
        visited_stops = []
        valid_path = True

        remaining_mandatory = list(perm)
        current_node = start

        while remaining_mandatory:
            next_vertex = None
            min_cost_to_next = sys.maxsize
            best_refuel_path = None
            best_path_to_next = None

            for next_mand in remaining_mandatory:
                path_to_next = reconstruct_path(pred, current_node, next_mand)
                if path_to_next:
                    cost_to_next = 0
                    for l in range(1, len(path_to_next)):
                        cost_to_next += adj_matrix[path_to_next[l - 1]][path_to_next[l]]
                    if current_fuel + cost_to_next <= fuel_limit:
                        if cost_to_next < min_cost_to_next:
                            min_cost_to_next = cost_to_next
                            next_vertex = next_mand
                            best_path_to_next = path_to_next
                    else:
                        for refuel_node in refuel_nodes:
                            path_to_refuel = reconstruct_path(pred, current_node, refuel_node)
                            if path_to_refuel:
                                refuel_cost = 0
                                for l in range(1, len(path_to_refuel)):
                                    refuel_cost += adj_matrix[path_to_refuel[l - 1]][path_to_refuel[l]]

                                if current_fuel + refuel_cost <= fuel_limit:
                                    path_from_refuel_to_next = reconstruct_path(pred, refuel_node, next_mand)
                                    if path_from_refuel_to_next:
                                        from_refuel_cost = 0
                                        for l in range(1, len(path_from_refuel_to_next)):
                                            from_refuel_cost += adj_matrix[path_from_refuel_to_next[l - 1]][
                                                path_from_refuel_to_next[l]]
                                        if from_refuel_cost <= fuel_limit:
                                            if refuel_cost + from_refuel_cost < min_cost_to_next:
                                                min_cost_to_next = refuel_cost + from_refuel_cost
                                                next_vertex = next_mand
                                                best_refuel_path = path_to_refuel
                                                best_path_to_next = path_from_refuel_to_next

            if next_vertex is None:
                valid_path = False
                reason = f"Não foi possível encontrar um caminho para nenhum dos nós obrigatórios."
                break

            if best_refuel_path:
                current_path.extend(best_refuel_path[1:])
                current_fuel = 0
                stops_count += 1
                visited_stops.append(best_refuel_path[-1])

            path_segment = reconstruct_path(pred, current_node, next_vertex)
            for j in range(1, len(path_segment)):
                weight = adj_matrix[path_segment[j - 1]][path_segment[j]]
                current_fuel += weight
                total_cost += weight
            current_path.append(path_segment[-1])

            current_node = next_vertex
            remaining_mandatory.remove(next_vertex)

        if valid_path and (len(visited_stops) < min_stops or (len(visited_stops) == min_stops and total_cost < min_cost)):
            min_cost = total_cost
            min_stops = stops_count
            best_path = current_path
            min_visited_stops = visited_stops
            reason = None

    if best_path is None:
        print("Não foi possível encontrar um caminho válido.")
        if reason:
            print(f"Motivo: {reason}")
        return None, 0, 0
    return best_path, min_cost, min_visited_stops
