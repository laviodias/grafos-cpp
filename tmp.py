import random
import json
import os
import folium
from src.services.google_api import GoogleMapsAPI
from src.maps.utils import initialize_map, add_marker_to_map


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
            return

        origin = self._select_random_origin()
        if not origin:
            return

        destinations = self._select_random_destinations()
        if not destinations:
            return

        self._add_bases_to_map(map_object)
        self._add_origin_to_map(map_object, origin)
        self._add_destinations_to_map(map_object, destinations)
        self._connect_points_on_map(map_object, origin, destinations)

        output_file = "output/delivery_map.html"
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
        return destinations

    def _add_bases_to_map(self, map_object):
        for base in self.bike_bases:
            folium.Marker(
                location=[base["location"]["lat"], base["location"]["lng"]],
                popup=f"{base['name']}",
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(map_object)

    def _add_origin_to_map(self, map_object, origin):
        folium.Marker(
            location=[origin["location"]["lat"], origin["location"]["lng"]],
            popup=f"Origin: {origin['name']}",
            icon=folium.Icon(color="red", icon="cutlery"),
        ).add_to(map_object)

    def _add_destinations_to_map(self, map_object, destinations):
        for destination in destinations:
            folium.Marker(
                location=[
                    destination["location"]["lat"],
                    destination["location"]["lng"],
                ],
                popup=f"Destination: {destination['name']}",
                icon=folium.Icon(color="green", icon="home"),
            ).add_to(map_object)

    def _connect_points_on_map(self, map_object, origin, destinations):
        for destination in destinations:
            origin_coord = f"{origin['location']['lat']},{origin['location']['lng']}"
            destination_coord = (
                f"{destination['location']['lat']},{destination['location']['lng']}"
            )

            distance, duration = self.google_api.directions(
                origin_coord, destination_coord, mode="bicycling"
            )
            if distance and duration:
                folium.PolyLine(
                    [
                        [origin["location"]["lat"], origin["location"]["lng"]],
                        [
                            destination["location"]["lat"],
                            destination["location"]["lng"],
                        ],
                    ],
                    color="red",
                    weight=2,
                    opacity=0.6,
                    tooltip=f"Distance: {distance / 1000:.2f} km, Time: {duration / 60:.1f} min",
                ).add_to(map_object)

            for base in self.bike_bases:
                base_coord = f"{base['location']['lat']},{base['location']['lng']}"
                distance, duration = self.google_api.directions(
                    destination_coord, base_coord, mode="bicycling"
                )
                if distance and duration:
                    folium.PolyLine(
                        [
                            [
                                destination["location"]["lat"],
                                destination["location"]["lng"],
                            ],
                            [base["location"]["lat"], base["location"]["lng"]],
                        ],
                        color="blue",
                        weight=2,
                        opacity=0.6,
                        tooltip=f"Distance: {distance / 1000:.2f} km, Time: {duration / 60:.1f} min",
                    ).add_to(map_object)
