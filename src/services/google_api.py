import requests


class GoogleMapsAPI:
    def __init__(self, api_key, language="pt-BR"):
        self.api_key = api_key
        self.language = language

    def nearby_search(self, location, radius, keyword=None, place_type=None):
        """
        Faz uma busca por locais próximos utilizando o endpoint Nearby Search da API do Google Places.
        """
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": location,
            "radius": radius,
            "key": self.api_key,
            "language": self.language,
        }
        if keyword:
            params["keyword"] = keyword
        if place_type:
            params["type"] = place_type

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Erro ao buscar locais próximos: {response.status_code} - {response.text}"
            )
            return None

    def directions(self, origin, destination, mode="bycicling"):
        """
        Obtém direções entre dois pontos utilizando o endpoint Directions da API do Google Maps.
        """
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": self.api_key,
            "language": self.language,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao buscar direções: {response.status_code} - {response.text}")
            return None
