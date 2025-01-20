import random
import json
import os
import networkx as nx
from src.services.google_api import GoogleMapsAPI
from src.maps.utils import MapUtils


colors = {
    "bike": "blue",
    "origin": "red",
    "destination": "green",
}


class MapManager:
    def __init__(
        self,
        api_key,
        location,
        radius,
        bases_file,
        num_destinations,
    ):
        self.api_key = api_key
        self.location = location
        self.radius = radius
        self.bases_file = bases_file
        self.num_destinations = num_destinations
        self.google_api = GoogleMapsAPI(api_key)
        self.bike_bases = []
        self.base_distances = {}
        self.map_utils = MapUtils(location, self.google_api)

    def save_base_distances(self):
        print("Calculating distances between bike bases...")
        data = self.google_api.nearby_search(
            self.location, self.radius, keyword="Bike Itaú"
        )
        if not data:
            return

        self.bike_bases = [
            {"name": f"Bike Base {i}", "location": place["geometry"]["location"]}
            for i, place in enumerate(data.get("results", []))
        ]

        print(f"Found {len(self.bike_bases)} bike bases:")
        for base in self.bike_bases:
            print(f"- {base['name']} at {base['location']}")

        for i, origin in enumerate(self.bike_bases):
            origin_coord = f"{origin['location']['lat']},{origin['location']['lng']}"
            for j, destination in enumerate(self.bike_bases):
                if i != j:
                    destination_coord = f"{destination['location']['lat']},{destination['location']['lng']}"
                    response = self.google_api.directions(
                        origin_coord, destination_coord, mode="bicycling"
                    )
                    if response["routes"]:
                        routes = response["routes"][0]["legs"][0]
                        distance = routes["distance"]["value"]
                        duration = routes["duration"]["value"]

                    if distance and duration:
                        key = f"{origin['name']} -> {destination['name']}"
                        self.base_distances[key] = {
                            "distance": distance,
                            "duration": duration,
                            "origin": origin_coord,
                            "destination": destination_coord,
                        }
                        print(
                            f"Distance calculated: {key} - {distance} meters, {duration} seconds"
                        )

        self._save_to_file(
            self.bases_file,
            {
                "locations": self.bike_bases,
                "distances": self.base_distances,
            },
        )
        print(f"Distances saved to {self.bases_file}.")

    def load_origin_and_destinations(self, filepath):
        if not os.path.exists(filepath):
            print(f"File '{filepath}' not found.")
            return None, None

        with open(filepath, "r") as file:
            data = json.load(file)

        origin = data.get("origin")
        destinations = data.get("destinations", [])

        if origin:
            print(f"Loaded origin: {origin['name']} - Location: {origin['location']}")
        if destinations:
            print(f"Loaded {len(destinations)} destinations:")
            for destination in destinations:
                print(f"- {destination['name']} at {destination['location']}")

        return origin, destinations

    def save_last_processed(self, origin, destinations):
        last_processed_data = {
            "origin": {
                "name": origin["name"],
                "location": origin["location"],
            },
            "destinations": [
                {"name": destination["name"], "location": destination["location"]}
                for destination in destinations
            ],
        }

        storage_dir = "./storage"
        os.makedirs(storage_dir, exist_ok=True)
        file_path = os.path.join(storage_dir, "last_processed.json")

        with open(file_path, "w") as f:
            json.dump(last_processed_data, f, indent=4)
        print(f"Last processed data saved to {file_path}.")

    def save_graph(self, graph, origin, destinations):
        origin_name = origin["name"].replace(" ", "_").lower()
        num_destinations = len(destinations)
        file_name = f"graph_{origin_name}_{num_destinations}_destinations.json"
        storage_dir = "./storage"
        os.makedirs(storage_dir, exist_ok=True)
        file_path = os.path.join(storage_dir, file_name)

        graph_data = {
            "origin": {
                "name": origin["name"],
                "location": origin["location"],
            },
            "destinations": [
                {"name": destination["name"], "location": destination["location"]}
                for destination in destinations
            ],
            "nodes": list(graph.nodes(data=True)),
            "edges": list(graph.edges(data=True)),
        }

        with open(file_path, "w") as f:
            json.dump(graph_data, f, indent=4)
        print(f"Graph saved to {file_path}.")

    def load_graph_from_data(self, graph_data):
        graph = nx.Graph()

        origin = graph_data.get("origin")
        destinations = graph_data.get("destinations", [])

        for node, attrs in graph_data.get("nodes", []):
            graph.add_node(node, **attrs)

        for source, target, attrs in graph_data.get("edges", []):
            graph.add_edge(source, target, **attrs)

        return graph, origin, destinations

    def _save_to_file(self, filepath, data):
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    def _load_from_file(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        else:
            print(f"File {filepath} not found.")
            return None

    def load_base_distances(self):
        data = self._load_from_file(self.bases_file)
        if data:
            self.bike_bases = data.get("locations", [])
            self.base_distances = data.get("distances", {})

    def _select_random_origin(self):
        print("Fetching a random restaurant as the origin...")
        restaurant_data = self.google_api.nearby_search(
            self.location, self.radius, place_type="restaurant"
        )
        if not restaurant_data:
            return None

        restaurants = restaurant_data.get("results", [])
        origin = random.choice(restaurants)
        origin["location"] = origin["geometry"]["location"]
        print(f"Selected origin: {origin['name']} - Location: {origin['location']}")
        return origin

    def _select_random_destinations(self):
        print("Fetching random destinations...")
        destination_data = self.google_api.nearby_search(
            self.location, self.radius, place_type="establishment"
        )
        if not destination_data:
            return None

        destinations = random.sample(
            destination_data.get("results", []), self.num_destinations
        )
        for destination in destinations:
            destination["location"] = destination["geometry"]["location"]
            print(
                f"Selected destination: {destination['name']} - Location: {destination['location']}"
            )
        return destinations

    def create_delivery_map(self, origin, destinations):
        self.load_base_distances()

        map_object = self.map_utils.initialize_map()
        graph = nx.Graph()

        if not self.bike_bases:
            print("No bike bases found. Run 'save_base_distances' first.")
            return

        # Add bike bases to the map
        for base in self.bike_bases:
            graph.add_node(
                base["name"], coords=(base["location"]["lat"], base["location"]["lng"])
            )
            self.map_utils.add_point_to_map(
                map_object,
                location=base["location"],
                popup=f"{base['name']}",
                icon_color="blue",
                icon_type="info-sign",
            )

        # Add origin to the map
        graph.add_node(
            origin["name"],
            coords=(origin["location"]["lat"], origin["location"]["lng"]),
        )
        self.map_utils.add_point_to_map(
            map_object,
            location=origin["location"],
            popup=f"Origin: {origin['name']}",
            icon_color="red",
            icon_type="cutlery",
        )

        # Add destinations to the map
        for destination in destinations:
            graph.add_node(
                destination["name"],
                coords=(destination["location"]["lat"], destination["location"]["lng"]),
            )
            self.map_utils.add_point_to_map(
                map_object,
                location=destination["location"],
                popup=f"Destination: {destination['name']}",
                icon_color="green",
                icon_type="home",
            )

        self.map_utils.connect_points_on_map(
            origin,
            destinations,
            self.bike_bases,
            self.base_distances,
            graph,
        )

        for edge in graph.edges(data=True):
            self.map_utils.add_edge_to_map(
                map_object,
                edge,
                color=colors[edge[2]["type"]],
                weight=2,
                opacity=0.5,
            )

        output_file = "output/graph_map.html"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        map_object.save(output_file)
        print(f"Map saved as '{output_file}'. Open the file in a browser to view.")

        return graph
