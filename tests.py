from src.algorithms.shortest_path import find_path_with_fuel_limit

test_cases = {
    "caso_1_grafo_pouco_denso": {
        "adj_matrix": [
            [0, 10, 0, 0, 0],
            [10, 0, 15, 0, 0],
            [0, 15, 0, 20, 0],
            [0, 0, 20, 0, 25],
            [0, 0, 0, 25, 0],
        ],
        "start_vertex": 0,
        "mandatory_vertices": [2, 4],
        "fuel_limit": 40,
        "expected_output": ([0, 1, 2, 3, 4], 70, [2, 3]),
    },
    "caso_2_grafo_denso": {
        "adj_matrix": [
            [0, 5, 10, 15, 20],
            [5, 0, 7, 12, 18],
            [10, 7, 0, 9, 14],
            [15, 12, 9, 0, 8],
            [20, 18, 14, 8, 0],
        ],
        "start_vertex": 0,
        "mandatory_vertices": [2, 4],
        "fuel_limit": 40,
        "expected_output": ([0, 2, 4], 24, []),
    },
    "caso_3_impossivel_por_combustivel": {
        "adj_matrix": [[0, 50, 0, 0], [50, 0, 10, 0], [0, 10, 0, 50], [0, 0, 50, 0]],
        "start_vertex": 0,
        "mandatory_vertices": [3],
        "fuel_limit": 20,
        "expected_output": (None, 0, 0),
    },
    "caso_4_sem_pontos_abastecimento": {
        "adj_matrix": [
            [0, 10, 0, 0, 0],
            [10, 0, 15, 0, 0],
            [0, 15, 0, 20, 0],
            [0, 0, 20, 0, 25],
            [0, 0, 0, 25, 0],
        ],
        "start_vertex": 0,
        "mandatory_vertices": [1, 3, 4],
        "fuel_limit": 60,
        "expected_output": ([0, 1, 2, 3, 4], 70, [3]),
    },
    "caso_5_abastecimento_necessario": {
        "adj_matrix": [
            [0, 10, 20, 0, 0, 0, 0, 0, 0, 0],  # Vértice 0
            [10, 0, 0, 15, 0, 0, 0, 0, 0, 0],  # Vértice 1
            [20, 0, 0, 25, 0, 0, 0, 0, 0, 0],  # Vértice 2
            [0, 15, 25, 0, 10, 0, 0, 0, 0, 0],  # Vértice 3
            [0, 0, 0, 10, 0, 30, 0, 0, 0, 0],  # Vértice 4
            [0, 0, 0, 0, 30, 0, 5, 0, 0, 0],  # Vértice 5
            [0, 0, 0, 0, 0, 5, 0, 15, 0, 0],  # Vértice 6
            [0, 0, 0, 0, 0, 0, 15, 0, 10, 0],  # Vértice 7
            [0, 0, 0, 0, 0, 0, 0, 10, 0, 5],  # Vértice 8
            [0, 0, 0, 0, 0, 0, 0, 0, 5, 0],  # Vértice 9
        ],
        "start_vertex": 0,
        "mandatory_vertices": [3, 6, 8],
        "fuel_limit": 30,
        "expected_output": ([0, 1, 3, 4, 5, 6, 7, 8], 95, [3, 4, 5]),
    },
    "caso_6_varias_permutações": {
        "adj_matrix": [
            [0, 1, 5, 20, 0, 0],
            [1, 0, 2, 10, 0, 0],
            [5, 2, 0, 15, 10, 0],
            [20, 10, 15, 0, 5, 5],
            [0, 0, 10, 5, 0, 2],
            [0, 0, 0, 5, 2, 0],
        ],
        "start_vertex": 0,
        "mandatory_vertices": [3, 5],
        "fuel_limit": 20,
        "expected_output": ([0, 1, 3, 5], 16, []),
    },
    "caso_7_mais_vertices_obrigatórios": {
        "adj_matrix": [
            [0, 1, 5, 20, 0, 0, 0, 0],
            [1, 0, 2, 10, 0, 0, 0, 0],
            [5, 2, 0, 15, 10, 0, 0, 0],
            [20, 10, 15, 0, 5, 5, 0, 0],
            [0, 0, 10, 5, 0, 2, 1, 0],
            [0, 0, 0, 5, 2, 0, 5, 10],
            [0, 0, 0, 0, 1, 5, 0, 2],
            [0, 0, 0, 0, 0, 10, 2, 0],
        ],
        "start_vertex": 0,
        "mandatory_vertices": [3, 5, 6, 7],
        "fuel_limit": 30,
        "expected_output": ([0, 1, 3, 5, 4, 6, 7], 21, []),
    },
    "caso_8_grafo_desconectado": {
        "adj_matrix": [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
        "start_vertex": 0,
        "mandatory_vertices": [3],
        "fuel_limit": 10,
        "expected_output": (None, 0, 0),
    },
    "caso_9_ciclo": {
        "adj_matrix": [
            [0, 10, 0, 0, 0],
            [10, 0, 10, 0, 0],
            [0, 10, 0, 10, 0],
            [0, 0, 10, 0, 10],
            [0, 0, 0, 10, 0],
        ],
        "start_vertex": 0,
        "mandatory_vertices": [2, 4],
        "fuel_limit": 25,
        "expected_output": ([0, 1, 2, 3, 4], 40, [2]),
    },
}


def run_tests():
    for test_name, test_data in test_cases.items():
        print(f"Running test: {test_name}")
        adj_matrix = test_data["adj_matrix"]
        start_vertex = test_data["start_vertex"]
        mandatory_vertices = test_data["mandatory_vertices"]
        fuel_limit = test_data["fuel_limit"]
        expected_output = test_data["expected_output"]

        path, cost, stops = find_path_with_fuel_limit(
            adj_matrix, start_vertex, mandatory_vertices, fuel_limit
        )

        if (path, cost, stops) == expected_output:
            print(
                f"  ✅ Test passed! Expected: {expected_output}, Got: {(path,cost,stops)}"
            )
        else:
            print(
                f"  ❌ Test failed! Expected: {expected_output}, Got: {(path,cost,stops)}"
            )


if __name__ == "__main__":
    run_tests()
