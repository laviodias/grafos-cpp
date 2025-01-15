import requests
import folium
import networkx as nx

API_KEY = "AIzaSyCZndMy7A8eq9aGrH-C25F0C4eoG6b0uFU"
LOCATION = "-12.9814,-38.4714"  # Salvador, Bahia
RADIUS = 5000  # 5 km

def buscar_bases_itaú():
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": LOCATION,
        "radius": RADIUS,
        "keyword": "base de bicicletas Itaú",
        "key": API_KEY,
        "language": "pt-BR"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erro na API:", response.status_code, response.text)
        return None

def calcular_distancia_tempo(origem, destino):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origem,
        "destination": destino,
        "mode": "bicycling",  # Modo bicicleta
        "key": API_KEY,
        "language": "pt-BR"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        dados = response.json()
        if dados["routes"]:
            rota = dados["routes"][0]["legs"][0]
            distancia = rota["distance"]["value"]  # Em metros
            duracao = rota["duration"]["value"]  # Em segundos
            print(f"Origem: {origem}, Destino: {destino}, Distância: {distancia} m, Duração: {duracao} s")
            return distancia, duracao
        else:
            return None, None
    else:
        print("Erro na API:", response.status_code, response.text)
        return None, None

print("Buscando bases de bicicletas Itaú em Salvador...")
dados = buscar_bases_itaú()

if dados:
    locais = [
        {
            "nome": lugar["name"],
            "localizacao": lugar["geometry"]["location"],
            "endereco": lugar["vicinity"]
        }
        for lugar in dados.get("results", [])
    ]
    
    # Exibir os locais encontrados
    for i, lugar in enumerate(locais):
        print(f"{i + 1}. Nome: {lugar['nome']}, Endereço: {lugar['endereco']}, Localização: {lugar['localizacao']}")
    
    # Criar o grafo
    G = nx.Graph()
    
    print("\nCalculando tempos e distâncias entre as bases e adicionando ao grafo...")

    success_count = 0
    failure_count = 0

    for i, origem in enumerate(locais):
        origem_coord = f"{origem['localizacao']['lat']},{origem['localizacao']['lng']}"
        for j, destino in enumerate(locais):
            if i != j:  # Não calcular distância de um ponto para ele mesmo
                destino_coord = f"{destino['localizacao']['lat']},{destino['localizacao']['lng']}"
                distancia, duracao = calcular_distancia_tempo(origem_coord, destino_coord)
                if distancia and duracao:
                    success_count += 1
                    origem_id = f"{origem['nome']} {i}"
                    destino_id = f"{destino['nome']} {j}"
                    G.add_edge(
                        origem_id,
                        destino_id,
                        weight=distancia,
                        duration=duracao,
                        coords=(origem_coord, destino_coord)
                    )
                else:
                    failure_count += 1

    print(f"Rotas adicionadas com sucesso: {success_count}")
    print(f"Falhas ao calcular rotas: {failure_count}")
    
    # Criar mapa interativo
    mapa = folium.Map(location=[-12.9814, -38.4714], zoom_start=12)
    
    # Adicionar os vértices ao mapa
    for lugar in locais:
        lat, lng = lugar["localizacao"]["lat"], lugar["localizacao"]["lng"]
        folium.Marker(
            location=[lat, lng],
            popup=f"{lugar['nome']}<br>{lugar['endereco']}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mapa)
    
    # Adicionar as arestas ao mapa
    print("Arestas no grafo:")
    for u, v, data in G.edges(data=True):
        origem = [float(coord) for coord in data["coords"][0].split(",")]
        destino = [float(coord) for coord in data["coords"][1].split(",")]
        folium.PolyLine(
            [origem, destino],
            color="blue",
            weight=2,
            opacity=0.6,
            tooltip=f"Distância: {data['weight'] / 1000:.2f} km, Tempo: {data['duration'] / 60:.1f} min"
        ).add_to(mapa)
    
    # Salvar e exibir o mapa
    mapa.save("mapa_bases_itau.html")
    print("\nMapa salvo como 'mapa_bases_itau.html'. Abra o arquivo no navegador para visualizar.")