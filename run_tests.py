import os
import folium
import json
import numpy as np
from src.algorithms.appr_path import find_approximate_path


def draw_final_map(
    path,
    stops,
    edges,
    bike_bases,
    start_vertex,
    mandatory_vertices,
    nodes,
    node_coords,
):
    delivery_map = folium.Map(
        location=[
            node_coords[nodes[start_vertex]][0],
            node_coords[nodes[start_vertex]][1],
        ],
        zoom_start=15,
    )

    for base in bike_bases:
        coords = (base["location"]["lat"], base["location"]["lng"])
        folium.Marker(
            coords,
            popup=base["name"],
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(delivery_map)

    origin_coords = node_coords[nodes[start_vertex]]
    folium.Marker(
        origin_coords,
        popup=f"Origin: {nodes[start_vertex]}",
        icon=folium.Icon(color="red", icon="cutlery"),
    ).add_to(delivery_map)

    for destination in mandatory_vertices:
        destination_coords = node_coords[nodes[destination]]
        folium.Marker(
            destination_coords,
            popup=f"Destination: {nodes[destination]}",
            icon=folium.Icon(color="green", icon="home"),
        ).add_to(delivery_map)

    for stop in stops:
        stop_coords = node_coords[nodes[stop]]
        folium.Marker(
            stop_coords,
            popup=f"Stop: {nodes[stop]}",
            icon=folium.Icon(color="purple", icon="flag"),
        ).add_to(delivery_map)

    for i in range(len(path) - 1):
        node1 = nodes[path[i]]
        node2 = nodes[path[i + 1]]
        coord1 = node_coords[node1]
        coord2 = node_coords[node2]

        duration = next(
            (
                edge["duration"]
                for edge in edges
                if (edge["source"] == path[i] and edge["target"] == path[i + 1])
                or (edge["source"] == path[i + 1] and edge["target"] == path[i])
            ),
            0,
        )

        folium.PolyLine(
            [coord1, coord2],
            color="blue",
            weight=3,
            opacity=0.7,
            popup=f"Duration: {duration / 60} minutes",
        ).add_to(delivery_map)

    return delivery_map


def _load_from_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        print(f"File {filepath} not found.")
        return None


def process_test_cases():
    data_bike_bases = _load_from_file("storage/bases_itau_distances.json")
    if data_bike_bases:
        bike_bases = data_bike_bases.get("locations", [])

    input_dir = "tests/input"
    output_base_dir = "tests/output"

    for filename in os.listdir(input_dir):
        if filename.endswith(".json") and filename.startswith("fuel_"):
            # Extraindo informações do arquivo
            parts = filename.split("_")
            fuel_limit = parts[1]
            graph_name = "_".join(parts[2:]).replace(".json", "")

            input_file_path = os.path.join(input_dir, filename)
            output_graph_dir = os.path.join(output_base_dir, graph_name)
            output_fuel_dir = os.path.join(output_graph_dir, f"fuel_{fuel_limit}")

            os.makedirs(output_fuel_dir, exist_ok=True)

            # Lendo o arquivo de entrada
            with open(input_file_path, "r") as f:
                test_data = json.load(f)

            # Extraindo dados do arquivo
            adjacency_matrix = np.array(test_data["adj_matrix"])
            start_vertex = test_data["start_vertex"]
            mandatory_vertices = test_data["mandatory_vertices"]
            fuel_limit = test_data["fuel_limit"]
            nodes = test_data["nodes"]
            node_coords = test_data["node_coords"]
            edges = test_data["edges"]

            # Executando o algoritmo
            apprx_path, apprx_cost, apprx_stops = find_approximate_path(
                adjacency_matrix, start_vertex, mandatory_vertices, fuel_limit * 60
            )

            # Salvando o resultado em JSON
            result_data = {
                "path": apprx_path if isinstance(apprx_path, list) else [],
                "cost": float(apprx_cost) if apprx_cost is not None else 0,
                "stops": apprx_stops if isinstance(apprx_stops, list) else [],
            }

            result_file_path = os.path.join(output_fuel_dir, "result.json")
            with open(result_file_path, "w") as result_file:
                json.dump(result_data, result_file, indent=4)

            if apprx_path:
                map_output_path = os.path.join(output_fuel_dir, "path.html")
                draw_final_map(
                    apprx_path,
                    apprx_stops,
                    edges,
                    bike_bases,
                    start_vertex,
                    mandatory_vertices,
                    nodes,
                    node_coords,
                ).save(map_output_path)


if __name__ == "__main__":
    process_test_cases()
