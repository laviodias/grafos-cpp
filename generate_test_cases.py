import os
import json
import numpy as np
from src.graph_utils import graph_to_adjacency_matrix
from src.algorithms.appr_path import find_approximate_path
from src.algorithms.shortest_path import find_path_with_fuel_limit
import networkx as nx
import folium

LOCATION = "-12.9814,-38.4714"  # Salvador, Bahia


def draw_map(graph, bike_bases, origin, destinations, output_path):
    delivery_map = folium.Map(
        location=[float(coord) for coord in LOCATION.split(",")], zoom_start=15
    )

    origin_coords = (origin["location"]["lat"], origin["location"]["lng"])
    folium.Marker(
        origin_coords,
        popup=f"Origin: {origin['name']}",
        icon=folium.Icon(color="red", icon="cutlery"),
    ).add_to(delivery_map)

    for destination in destinations:
        coords = (destination["location"]["lat"], destination["location"]["lng"])
        folium.Marker(
            coords,
            popup=f"Destination: {destination['name']}",
            icon=folium.Icon(color="green", icon="home"),
        ).add_to(delivery_map)

    for base in bike_bases:
        coords = (base["location"]["lat"], base["location"]["lng"])
        folium.Marker(
            coords,
            popup=base["name"],
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(delivery_map)

    for edge in graph.edges(data=True):
        folium.PolyLine(
            [
                (graph.nodes[edge[0]]["coords"][0], graph.nodes[edge[0]]["coords"][1]),
                (graph.nodes[edge[1]]["coords"][0], graph.nodes[edge[1]]["coords"][1]),
            ],
            color="blue",
            weight=2,
            opacity=0.5,
        ).add_to(delivery_map)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    delivery_map.save(output_path)


def load_graph_from_data(graph_data):
    graph = nx.Graph()

    origin = graph_data.get("origin")
    destinations = graph_data.get("destinations", [])

    for node, attrs in graph_data.get("nodes", []):
        graph.add_node(node, **attrs)

    for source, target, attrs in graph_data.get("edges", []):
        graph.add_edge(source, target, **attrs)

    return graph, origin, destinations


def _load_from_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        print(f"File {filepath} not found.")
        return None


def process_graph_files():
    input_dir = "storage"
    tests_input_dir = "tests/input"
    output_dir = "tests/output/"
    os.makedirs(output_dir, exist_ok=True)

    data_bike_bases = _load_from_file("storage/bases_itau_distances.json")
    if data_bike_bases:
        bike_bases = data_bike_bases.get("locations", [])

    fuel_limits = [20, 35, 45]

    for filename in os.listdir(input_dir):
        if filename.startswith("graph"):
            input_path = os.path.join(input_dir, filename)
            output_subdir = os.path.join(output_dir, filename.replace(".json", ""))

            with open(input_path, "r") as f:
                graph_data = json.load(f)

            # Carregar grafo a partir dos dados
            graph, origin, destinations = load_graph_from_data(graph_data)

            map_output_path = os.path.join(output_subdir, "map.html")
            draw_map(graph, bike_bases, origin, destinations, map_output_path)

            # Gerar matriz de adjacência, nós e coordenadas
            adjacency_matrix, nodes, node_coords = graph_to_adjacency_matrix(graph)

            # Determinar o vértice inicial e os vértices obrigatórios
            start_vertex = nodes.index(origin["name"])
            mandatory_vertices = [
                nodes.index(destination["name"]) for destination in destinations
            ]

            edges = [
                {
                    "source": nodes.index(u),
                    "target": nodes.index(v),
                    "duration": data.get("duration", 0),
                }
                for u, v, data in graph.edges(data=True)
            ]

            for fuel_limit in fuel_limits:
                apprx_path, apprx_cost, apprx_stops = find_approximate_path(
                    adjacency_matrix, start_vertex, mandatory_vertices, fuel_limit
                )

                apprx_path = apprx_path if isinstance(apprx_path, list) else []
                apprx_stops = apprx_stops if isinstance(apprx_stops, list) else []
                apprx_cost = apprx_cost if apprx_cost is not None else 0

                formatted_data = {
                    "adj_matrix": (
                        adjacency_matrix.tolist()
                        if isinstance(adjacency_matrix, np.ndarray)
                        else adjacency_matrix
                    ),
                    "nodes": nodes,
                    "node_coords": node_coords,
                    "edges": edges,
                    "start_vertex": int(start_vertex),
                    "mandatory_vertices": [int(v) for v in mandatory_vertices],
                    "fuel_limit": int(fuel_limit),
                    "expected_result": (
                        [int(v) for v in apprx_path],
                        float(apprx_cost),
                        [int(s) for s in apprx_stops],
                    ),
                }

                output_path = os.path.join(
                    tests_input_dir,
                    f"fuel_{fuel_limit}_{filename.replace('.json', '.json')}",
                )
                with open(output_path, "w") as test_file:
                    json.dump(formatted_data, test_file, indent=4)


if __name__ == "__main__":
    process_graph_files()
