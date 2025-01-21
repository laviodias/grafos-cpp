import sys

def find_approximate_path(adj_matrix, start, mandatory, fuel_limit):
    def calculate_cost(path):
        return sum(adj_matrix[path[i - 1]][path[i]] for i in range(1, len(path))) if path else 0

    # Inicialização
    all_nodes = set(range(len(adj_matrix)))
    refuel_nodes = list(all_nodes - set(mandatory) - {start})
    remaining_mandatory = set(mandatory)
    current_node = start
    current_time_traveled = 0
    total_cost = 0
    visited_stops = []
    current_path = [start]
    last_mandatory_visited = start
    refuel_nodes_since_last_mandatory = set()

    while remaining_mandatory:
        best_next_mandatory = None
        min_cost_to_mandatory = sys.maxsize

        # Tentar ir diretamente para um nó obrigatório
        for next_mandatory in remaining_mandatory:
            if adj_matrix[current_node][next_mandatory] > 0 and adj_matrix[current_node][next_mandatory] <= fuel_limit - current_time_traveled:
                if adj_matrix[current_node][next_mandatory] < min_cost_to_mandatory:
                    min_cost_to_mandatory = adj_matrix[current_node][next_mandatory]
                    best_next_mandatory = next_mandatory

        if best_next_mandatory:
            # Ir diretamente para o próximo nó obrigatório
            current_path.append(best_next_mandatory)
            current_time_traveled += min_cost_to_mandatory
            total_cost += min_cost_to_mandatory
            current_node = best_next_mandatory
            remaining_mandatory.remove(best_next_mandatory)
            refuel_nodes_since_last_mandatory = set() # Reset refuel nodes since a mandatory was reached
            last_mandatory_visited = current_node
        else:
            # Não é possível ir diretamente para nenhum nó obrigatório, tentar reabastecer
            best_refuel_node = None
            min_cost_to_refuel = sys.maxsize

            for refuel_node in refuel_nodes:
                if adj_matrix[current_node][refuel_node] > 0 and adj_matrix[current_node][refuel_node] < min_cost_to_refuel:
                    min_cost_to_refuel = adj_matrix[current_node][refuel_node]
                    best_refuel_node = refuel_node

            if best_refuel_node:
                if best_refuel_node in refuel_nodes_since_last_mandatory:
                    print("Possível loop infinito detectado. O algoritmo está revisitando nós de reabastecimento sem progredir para os nós obrigatórios.")
                    return None, 0, []

                # Ir para o nó de reabastecimento
                current_path.append(best_refuel_node)
                total_cost += min_cost_to_refuel
                current_time_traveled += min_cost_to_refuel
                visited_stops.append(best_refuel_node)
                refuel_nodes_since_last_mandatory.add(best_refuel_node)
                current_node = best_refuel_node
                current_time_traveled = 0
            else:
                print("Não foi possível encontrar um caminho viável (sem combustível ou sem rota).")
                return None, 0, []

    return current_path, total_cost, visited_stops