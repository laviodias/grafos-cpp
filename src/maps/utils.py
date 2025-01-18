import folium


class MapUtils:
    def __init__(self, location):
        self.location = [float(coord) for coord in location.split(",")]

    def initialize_map(self):
        return folium.Map(location=self.location, zoom_start=12)

    def add_point_to_map(self, map_object, location, popup, icon_color, icon_type):
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=popup,
            icon=folium.Icon(color=icon_color, icon=icon_type),
        ).add_to(map_object)

    def add_line_to_map(self, map_object, location1, location2, color, weight, opacity):
        folium.PolyLine(
            [location1, location2],
            color=color,
            weight=weight,
            opacity=opacity,
        ).add_to(map_object)

    def connect_points_on_map(
        self, map_object, origin, destinations, google_api, bike_bases, base_distances
    ):

        for base_a in bike_bases:
            for base_b in bike_bases:
                if base_a != base_b:

                    key = f"Bike Base {bike_bases.index(base_a)} -> Bike Base {bike_bases.index(base_b)}"

                    if key in base_distances:
                        base_a_coord = [
                            base_a["location"]["lat"],
                            base_a["location"]["lng"],
                        ]
                        base_b_coord = [
                            base_b["location"]["lat"],
                            base_b["location"]["lng"],
                        ]

                        distance = base_distances[key]["distance"]
                        duration = base_distances[key]["duration"]

                        folium.PolyLine(
                            [base_a_coord, base_b_coord],
                            color="blue",
                            weight=2,
                            opacity=0.6,
                            tooltip=f"Distance: {distance / 1000:.2f} km, Time: {duration / 60:.1f} min",
                        ).add_to(map_object)

        origin_coord = f"{origin['location']['lat']},{origin['location']['lng']}"
        for base in bike_bases:
            base_coord = f"{base['location']['lat']},{base['location']['lng']}"

            response = google_api.directions(origin_coord, base_coord, mode="bicycling")
            if response["routes"]:
                distance = response["routes"][0]["legs"][0]["distance"]["value"]
                duration = response["routes"][0]["legs"][0]["duration"]["value"]

                if distance and duration:
                    folium.PolyLine(
                        [
                            [origin["location"]["lat"], origin["location"]["lng"]],
                            [base["location"]["lat"], base["location"]["lng"]],
                        ],
                        color="red",
                        weight=2,
                        opacity=0.6,
                        tooltip=f"Distance: {distance / 1000:.2f} km, Time: {duration / 60:.1f} min",
                    ).add_to(map_object)

        for destination in destinations:
            destination_coord = (
                f"{destination['location']['lat']},{destination['location']['lng']}"
            )

            response = google_api.directions(
                origin_coord, destination_coord, mode="bicycling"
            )
            if response["routes"]:
                distance = response["routes"][0]["legs"][0]["distance"]["value"]
                duration = response["routes"][0]["legs"][0]["duration"]["value"]

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

            for base in bike_bases:
                base_coord = f"{base['location']['lat']},{base['location']['lng']}"
                response = google_api.directions(
                    destination_coord, base_coord, mode="bicycling"
                )

                if response["routes"]:
                    distance = response["routes"][0]["legs"][0]["distance"]["value"]
                    duration = response["routes"][0]["legs"][0]["duration"]["value"]

                if distance and duration:
                    folium.PolyLine(
                        [
                            [
                                destination["location"]["lat"],
                                destination["location"]["lng"],
                            ],
                            [base["location"]["lat"], base["location"]["lng"]],
                        ],
                        color="green",
                        weight=2,
                        opacity=0.6,
                        tooltip=f"Distance: {distance / 1000:.2f} km, Time: {duration / 60:.1f} min",
                    ).add_to(map_object)
