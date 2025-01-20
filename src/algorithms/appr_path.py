import sys

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

def find_approximate_path(adj_matrix, start, mandatory, fuel_limit):
    def find_closest_node(current, targets, fuel):
        # Encontra o nó mais próximo dos alvos dentro do combustível disponível.
        min_cost = sys.maxsize
        best_node = None
        best_path = None
        for target in targets:
            path = reconstruct_path(pred, current, target)
            if path:
                cost = sum(adj_matrix[path[i - 1]][path[i]] for i in range(1, len(path)))
                if cost <= fuel and cost < min_cost:
                    min_cost = cost
                    best_node = target
                    best_path = path
        return best_node, best_path, min_cost

    def find_refuel_path(current, target, fuel):
        # Encontra um caminho viável com reabastecimento.
        for refuel_node in refuel_nodes:
            refuel_path = reconstruct_path(pred, current, refuel_node)
            if refuel_path:
                refuel_cost = sum(adj_matrix[refuel_path[i - 1]][refuel_path[i]] for i in range(1, len(refuel_path)))
                if fuel >= refuel_cost:
                    post_refuel_path = reconstruct_path(pred, refuel_node, target)
                    if post_refuel_path:
                        post_refuel_cost = sum(
                            adj_matrix[post_refuel_path[i - 1]][post_refuel_path[i]] for i in range(1, len(post_refuel_path))
                        )
                        if post_refuel_cost <= fuel_limit:
                            return refuel_path, post_refuel_path, refuel_cost + post_refuel_cost
        return None, None, sys.maxsize

    # Floyd-Warshall para calcular menores distâncias e predecessores
    dist, pred = floyd_warshall_with_predecessors(adj_matrix)

    # Inicialização
    all_nodes = set(range(len(adj_matrix)))
    refuel_nodes = list(all_nodes - set(mandatory) - {start})
    remaining_mandatory = set(mandatory)
    current_node = start
    current_fuel = 0
    total_cost = 0
    stops_count = 0
    visited_stops = []
    current_path = [start]

    # Construção gulosa do caminho
    while remaining_mandatory:
        # Tentar ir diretamente ao próximo nó obrigatório
        next_node, direct_path, direct_cost = find_closest_node(current_node, remaining_mandatory, fuel_limit - current_fuel)

        if next_node:
            # Caminho direto encontrado
            current_path.extend(direct_path[1:])
            current_fuel += direct_cost
            total_cost += direct_cost
            current_node = next_node
            remaining_mandatory.remove(next_node)
        else:
            # Caminho direto inviável, tentar reabastecimento
            next_node, best_refuel_path, refuel_cost = None, None, sys.maxsize
            for target in remaining_mandatory:
                refuel_path, post_refuel_path, cost = find_refuel_path(current_node, target, current_fuel)
                if cost < refuel_cost:
                    next_node = target
                    best_refuel_path = refuel_path + post_refuel_path[1:]
                    refuel_cost = cost

            if next_node:
                # Caminho com reabastecimento encontrado
                current_path.extend(best_refuel_path[1:])
                current_fuel = 0
                stops_count += 1
                visited_stops.append(best_refuel_path[len(best_refuel_path) // 2])  # Nó de reabastecimento
                current_node = next_node
                remaining_mandatory.remove(next_node)
                total_cost += refuel_cost
            else:
                print("Não foi possível encontrar um caminho viável com a heurística gulosa.")
                return None, 0, []

    return current_path, total_cost, visited_stops
