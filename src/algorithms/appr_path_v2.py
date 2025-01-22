import sys

def find_approximate_path(adj_matrix, start, mandatory, fuel_limit):
    def calculate_cost(path):
        return sum(adj_matrix[path[i - 1]][path[i]] for i in range(1, len(path))) if path and len(path) > 1 else 0

    all_nodes = set(range(len(adj_matrix)))
    refuel_nodes = list(all_nodes - set(mandatory) - {start})

    def solve_recursive(current_node, remaining_mandatory, current_fuel, current_path, visited_stops_recursive, refuel_nodes_since_last_mandatory_recursive):
        if not remaining_mandatory:
            return current_path, calculate_cost(current_path), visited_stops_recursive

        # Tentar ir diretamente para nós obrigatórios
        mandatory_alternatives = []
        for next_mandatory in remaining_mandatory:
            cost_to_mandatory = adj_matrix[current_node][next_mandatory]
            if cost_to_mandatory > 0 and cost_to_mandatory <= current_fuel:
                mandatory_alternatives.append((next_mandatory, cost_to_mandatory))
                break

        for next_mandatory, cost_to_mandatory in mandatory_alternatives:
            next_remaining_mandatory = remaining_mandatory - {next_mandatory}
            path_result, total_cost_result, visited_stops_result = solve_recursive(
                next_mandatory,
                next_remaining_mandatory,
                current_fuel - cost_to_mandatory,
                current_path + [next_mandatory],
                visited_stops_recursive,
                set()
            )
            if path_result:
                return path_result, total_cost_result, visited_stops_result

        # Se não conseguiu ir diretamente para nenhum obrigatório, tentar reabastecer
        refuel_alternatives = []
        for refuel_node in refuel_nodes:
            cost_to_refuel = adj_matrix[current_node][refuel_node]
            if cost_to_refuel > 0 and cost_to_refuel <= current_fuel:
                refuel_alternatives.append((refuel_node, cost_to_refuel))
                break
                
        for refuel_node, cost_to_refuel in refuel_alternatives:
            if refuel_node in refuel_nodes_since_last_mandatory_recursive:
                continue # Evitar loop infinito no mesmo nó de reabastecimento

            next_visited_stops = visited_stops_recursive + [refuel_node]
            path_result, total_cost_result, visited_stops_result = solve_recursive(
                refuel_node,
                remaining_mandatory,
                fuel_limit - cost_to_refuel, # Reabastece totalmente
                current_path + [refuel_node],
                next_visited_stops,
                refuel_nodes_since_last_mandatory_recursive.union({refuel_node})
            )
            if path_result: # Se encontrou um caminho a partir do reabastecimento
                return path_result, total_cost_result, visited_stops_result

        return None, 0, [] # Falhou em todas as opções a partir deste ponto

    initial_mandatory = set(mandatory) # Criar uma cópia para não modificar a original
    return solve_recursive(start, initial_mandatory, fuel_limit, [start], [], set())