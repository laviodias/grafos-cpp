import os
import json
from dotenv import load_dotenv
from src.maps.manager import MapManager
from src.maps.utils import MapUtils
from src.graph_utils import graph_to_adjacency_matrix
from src.algorithms.shortest_path import find_path_with_fuel_limit

load_dotenv()

LOCATION = "-12.9814,-38.4714"  # Salvador, Bahia
RADIUS = 5000  # 10 km
API_KEY = os.getenv("API_KEY")
BASES_FILE = "storage/bases_itau_distances.json"
ORIGIN_DESTINATIONS_FILE = "input/origin_and_destinations.json"
GRAPH_FILE = "input/graph_input.json"
LOAD_GRAPH_FROM_FILE = True
LOAD_ORIGIN_AND_DESTINATIONS_FROM_FILE = False
NUM_DESTINATIONS = 7
FUEL_LIMIT = 45

maps = MapManager(API_KEY, LOCATION, RADIUS, BASES_FILE, NUM_DESTINATIONS)
maps_utils = MapUtils(LOCATION, API_KEY)

if __name__ == "__main__":
    if not os.path.exists(BASES_FILE):
        maps.save_base_distances()

    data_bike_bases = maps._load_from_file(BASES_FILE)
    if data_bike_bases:
        bike_bases = data_bike_bases.get("locations", [])
        base_distances = data_bike_bases.get("distances", {})

    if os.path.exists(GRAPH_FILE) and LOAD_GRAPH_FROM_FILE:
        print(f"Loading graph from {GRAPH_FILE}...")
        with open(GRAPH_FILE, "r") as f:
            graph_data = json.load(f)
        graph, origin, destinations = maps.load_graph_from_data(graph_data)
        maps_utils.draw_map(graph, bike_bases, origin, destinations)
    else:
        print(
            "Graph file not found or LOAD_GRAPH_FROM_FILE is False. Creating graph..."
        )

        if (
            os.path.exists(ORIGIN_DESTINATIONS_FILE)
            and LOAD_ORIGIN_AND_DESTINATIONS_FROM_FILE
        ):
            origin, destinations = maps.load_origin_and_destinations(
                ORIGIN_DESTINATIONS_FILE
            )
        else:
            print("Origin and destinations file not found. Selecting randomly...")
            origin = maps._select_random_origin()
            if not origin:
                print("No origin found.")
                exit()

            destinations = maps._select_random_destinations()
            if not destinations:
                print("No destinations found.")
                exit()

        graph = maps.create_delivery_map(origin, destinations)

    if origin and destinations:
        maps.save_last_processed(origin, destinations)
        maps.save_graph(graph, origin, destinations)

    adjacency_matrix, nodes, node_coords = graph_to_adjacency_matrix(graph)

    node_index = {node: i for i, node in enumerate(nodes)}

    start_vertex = nodes.index(origin["name"])
    mandatory_vertices = [
        nodes.index(destination["name"]) for destination in destinations
    ]

    path, cost, stops = find_path_with_fuel_limit(
        adjacency_matrix, start_vertex, mandatory_vertices, FUEL_LIMIT
    )

    if path:
        print(f"Path: {path}")
        print(f"Cost: {cost}")
        print(f"Stops: {stops}")

        # Recriar o mapa com o menor caminho
        delivery_map = maps_utils.draw_final_map(
            path,
            stops,
            graph,
            bike_bases,
            start_vertex,
            mandatory_vertices,
            nodes,
            node_coords,
        )

        # Salvar o mapa
        output_path = "output/shortest_path_map.html"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        delivery_map.save(output_path)
        print(
            f"Map with shortest path saved as '{output_path}'. Open the file in a browser to view."
        )
    else:
        print("No path found.")
