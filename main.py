import os
from dotenv import load_dotenv
from src.maps.manager import MapManager
from src.graph_utils import graph_to_adjacency_matrix
from src.algorithms.shortest_path import find_path_with_fuel_limit
import folium

load_dotenv()

LOCATION = "-12.9814,-38.4714"  # Salvador, Bahia
RADIUS = 10000  # 10 km
API_KEY = os.getenv("API_KEY")
BASES_FILE = "storage/bases_itau_distances.json"
NUM_DESTINATIONS = 6
FUEL_LIMIT = 30

maps = MapManager(API_KEY, LOCATION, RADIUS, BASES_FILE, NUM_DESTINATIONS)

if __name__ == "__main__":
    if not os.path.exists(BASES_FILE):
        maps.save_base_distances()

    origin = maps._select_random_origin()
    if not origin:
        print("No origin found.")
        exit()

    destinations = maps._select_random_destinations()
    if not destinations:
        print("No destinations found.")
        exit()

    data_bike_bases = maps._load_from_file(BASES_FILE)
    if data_bike_bases:
        bike_bases = data_bike_bases.get("locations", [])
        base_distances = data_bike_bases.get("distances", {})

    graph = maps.create_delivery_map(origin, destinations)

    adjacency_matrix, nodes, node_coords = graph_to_adjacency_matrix(graph)

    node_index = {node: i for i, node in enumerate(nodes)}

    print("Nodes:", nodes)

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
        delivery_map = maps.map_utils.initialize_map()

        # Adicionar a origem
        origin_coords = node_coords[nodes[start_vertex]]
        folium.Marker(
            origin_coords,
            popup=f"Origin: {nodes[start_vertex]}",
            icon=folium.Icon(color="red", icon="cutlery"),
        ).add_to(delivery_map)

        # Adicionar os destinos no caminho
        for destination in mandatory_vertices:
            destination_coords = node_coords[nodes[destination]]
            folium.Marker(
                destination_coords,
                popup=f"Destination: {nodes[destination]}",
                icon=folium.Icon(color="green", icon="home"),
            ).add_to(delivery_map)

        # Adicionar os stops (reabastecimentos)
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

            duration = graph[node1][node2]["duration"]
            duration_minutes = duration // 60

            folium.PolyLine(
                [coord1, coord2],
                color="blue",
                weight=3,
                opacity=0.7,
                popup=f"duration: {duration_minutes} minutes",
            ).add_to(delivery_map)

        # Salvar o mapa
        output_path = "output/shortest_path_map.html"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        delivery_map.save(output_path)
        print(
            f"Map with shortest path saved as '{output_path}'. Open the file in a browser to view."
        )
    else:
        print("No path found.")
