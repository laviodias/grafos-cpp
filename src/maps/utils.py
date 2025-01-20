import folium


class MapUtils:
    def __init__(self, location, google_api):
        self.location = [float(coord) for coord in location.split(",")]
        self.google_api = google_api

    def initialize_map(self):
        return folium.Map(location=self.location, zoom_start=15)

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

    def draw_final_map(
        self,
        path,
        stops,
        graph,
        bike_bases,
        start_vertex,
        mandatory_vertices,
        nodes,
        node_coords,
    ):
        delivery_map = self.initialize_map()

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

            duration = graph[node1][node2]["duration"]
            duration_minutes = duration // 60

            folium.PolyLine(
                [coord1, coord2],
                color="blue",
                weight=3,
                opacity=0.7,
                popup=f"Duration: {duration_minutes} minutes",
            ).add_to(delivery_map)

        return delivery_map

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
