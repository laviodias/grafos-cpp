import random
import json
import os
from src.services.google_api import GoogleMapsAPI
from src.maps.utils import MapUtils


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
        self.map_utils = MapUtils(location)

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

    def create_delivery_map(self):
        self.load_base_distances()
        if not self.bike_bases:
            print("No bike bases found. Run 'save_base_distances' first.")
            return

        origin = self._select_random_origin()
        if not origin:
            return

        destinations = self._select_random_destinations()
        if not destinations:
            return

        map_object = self.map_utils.initialize_map()

        # Add bike bases to the map
        for base in self.bike_bases:
            self.map_utils.add_point_to_map(
                map_object,
                location=base["location"],
                popup=f"{base['name']}",
                icon_color="blue",
                icon_type="info-sign",
            )

        # Add origin to the map
        self.map_utils.add_point_to_map(
            map_object,
            location=origin["location"],
            popup=f"Origin: {origin['name']}",
            icon_color="red",
            icon_type="cutlery",
        )

        # Add destinations to the map
        for destination in destinations:
            self.map_utils.add_point_to_map(
                map_object,
                location=destination["location"],
                popup=f"Destination: {destination['name']}",
                icon_color="green",
                icon_type="home",
            )

        self.map_utils.connect_points_on_map(
            map_object,
            origin,
            destinations,
            self.google_api,
            self.bike_bases,
            self.base_distances,
        )

        output_file = "output/delivery_map.html"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        map_object.save(output_file)
        print(f"Map saved as '{output_file}'. Open the file in a browser to view.")

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
