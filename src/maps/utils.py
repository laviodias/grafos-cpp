import folium


class MapUtils:
    def __init__(self, location, google_api):
        self.location = [float(coord) for coord in location.split(",")]
        self.google_api = google_api

    def initialize_map(self):
        return folium.Map(location=self.location, zoom_start=12)

    def add_point_to_map(self, map_object, location, popup, icon_color, icon_type):
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=popup,
            icon=folium.Icon(color=icon_color, icon=icon_type),
        ).add_to(map_object)

    def add_edge_to_map(self, map_object, edge, color, weight, opacity):
        coords = edge[2]["coords"]

        folium.PolyLine(
            [coords[0], coords[1]],
            color=color,
            weight=weight,
            opacity=opacity,
            popup=f"Duration: {edge[2]['duration'] // 60} minutes",
        ).add_to(map_object)

    def connect_bases_between_each_other(self, bike_bases, base_distances, graph):
        for base_a in bike_bases:
            for base_b in bike_bases:
                if base_a != base_b:
                    key = f"Bike Base {bike_bases.index(base_a)} -> Bike Base {bike_bases.index(base_b)}"
                    if key in base_distances:
                        base_a_coord = (
                            base_a["location"]["lat"],
                            base_a["location"]["lng"],
                        )
                        base_b_coord = (
                            base_b["location"]["lat"],
                            base_b["location"]["lng"],
                        )

                        distance = base_distances[key]["distance"]
                        duration = base_distances[key]["duration"]

                        graph.add_edge(
                            base_a["name"],
                            base_b["name"],
                            distance=distance,
                            duration=duration,
                            type="bike",
                            coords=(base_a_coord, base_b_coord),
                        )

                        print(f"Connecting bases: {base_a['name']} -> {base_b['name']}")

    def connect_origin_to_bases(self, origin, bike_bases, graph):
        origin_coord = f"{origin['location']['lat']},{origin['location']['lng']}"
        for base in bike_bases:
            base_coord = f"{base['location']['lat']},{base['location']['lng']}"
            response = self.google_api.directions(
                origin_coord, base_coord, mode="bicycling"
            )

            origin_tuple = (origin["location"]["lat"], origin["location"]["lng"])
            base_tuple = (base["location"]["lat"], base["location"]["lng"])

            if response["routes"]:
                distance = response["routes"][0]["legs"][0]["distance"]["value"]
                duration = response["routes"][0]["legs"][0]["duration"]["value"]

                if distance and duration:

                    graph.add_edge(
                        origin["name"],
                        base["name"],
                        distance=distance,
                        duration=duration,
                        type="origin",
                        coords=(origin_tuple, base_tuple),
                    )

                    print(
                        f"Connecting origin to base: {origin['name']} -> {base['name']}"
                    )

    def connect_origin_to_destinations(self, origin, destinations, graph):
        origin_coord = f"{origin['location']['lat']},{origin['location']['lng']}"
        for destination in destinations:
            destination_coord = (
                f"{destination['location']['lat']},{destination['location']['lng']}"
            )
            response = self.google_api.directions(
                origin_coord, destination_coord, mode="bicycling"
            )

            origin_tuple = (origin["location"]["lat"], origin["location"]["lng"])
            destination_tuple = (
                destination["location"]["lat"],
                destination["location"]["lng"],
            )

            if response["routes"]:
                distance = response["routes"][0]["legs"][0]["distance"]["value"]
                duration = response["routes"][0]["legs"][0]["duration"]["value"]

                if distance and duration:

                    graph.add_edge(
                        origin["name"],
                        destination["name"],
                        distance=distance,
                        duration=duration,
                        type="origin",
                        coords=(origin_tuple, destination_tuple),
                    )

                    print(
                        f"Connecting origin to destination: {origin['name']} -> {destination['name']}"
                    )

    def connect_destionations_between_each_other(self, destinations, graph):
        for i in range(len(destinations)):
            for j in range(i + 1, len(destinations)):
                origin_coord = f"{destinations[i]['location']['lat']},{destinations[i]['location']['lng']}"
                destination_coord = f"{destinations[j]['location']['lat']},{destinations[j]['location']['lng']}"

                response = self.google_api.directions(
                    f"{destinations[i]['location']['lat']},{destinations[i]['location']['lng']}",
                    f"{destinations[j]['location']['lat']},{destinations[j]['location']['lng']}",
                    mode="bicycling",
                )

                origin_tuple = (
                    destinations[i]["location"]["lat"],
                    destinations[i]["location"]["lng"],
                )
                destination_tuple = (
                    destinations[j]["location"]["lat"],
                    destinations[j]["location"]["lng"],
                )

                if response["routes"]:
                    distance = response["routes"][0]["legs"][0]["distance"]["value"]
                    duration = response["routes"][0]["legs"][0]["duration"]["value"]

                    if distance and duration:
                        graph.add_edge(
                            destinations[i]["name"],
                            destinations[j]["name"],
                            distance=distance,
                            duration=duration,
                            type="destination",
                            coords=(origin_tuple, destination_tuple),
                        )

                        print(
                            f"Connecting destinations: {destinations[i]['name']} -> {destinations[j]['name']}"
                        )

    def connect_destinations_to_bases(self, destinations, bike_bases, graph):
        for destination in destinations:
            destination_coord = (
                f"{destination['location']['lat']},{destination['location']['lng']}"
            )
            for base in bike_bases:
                base_coord = f"{base['location']['lat']},{base['location']['lng']}"
                response = self.google_api.directions(
                    destination_coord, base_coord, mode="bicycling"
                )

                destination_tuple = (
                    destination["location"]["lat"],
                    destination["location"]["lng"],
                )
                base_tuple = (base["location"]["lat"], base["location"]["lng"])

                if response["routes"]:
                    distance = response["routes"][0]["legs"][0]["distance"]["value"]
                    duration = response["routes"][0]["legs"][0]["duration"]["value"]

                    if distance and duration:

                        graph.add_edge(
                            destination["name"],
                            base["name"],
                            distance=distance,
                            duration=duration,
                            type="destination",
                            coords=(destination_tuple, base_tuple),
                        )

                        print(
                            f"Connecting destination to base: {destination['name']} -> {base['name']}"
                        )

    def connect_points_on_map(
        self,
        origin,
        destinations,
        bike_bases,
        base_distances,
        graph,
    ):
        self.connect_bases_between_each_other(bike_bases, base_distances, graph)
        self.connect_origin_to_bases(origin, bike_bases, graph)
        self.connect_origin_to_destinations(origin, destinations, graph)
        self.connect_destionations_between_each_other(destinations, graph)
        self.connect_destinations_to_bases(destinations, bike_bases, graph)
