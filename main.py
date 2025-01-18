import os
from dotenv import load_dotenv
from src.maps.manager import MapManager

load_dotenv()

LOCATION = "-12.9814,-38.4714"  # Salvador, Bahia
RADIUS = 10000  # 10 km
API_KEY = os.getenv("API_KEY")
BASES_FILE = "storage/bases_itau_distances.json"
NUM_DESTINATIONS = 5

maps = MapManager(API_KEY, LOCATION, RADIUS, BASES_FILE, NUM_DESTINATIONS)

if __name__ == "__main__":
    if not os.path.exists(BASES_FILE):
        maps.save_base_distances()

    maps.create_delivery_map()
