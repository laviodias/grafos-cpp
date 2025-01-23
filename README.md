# 🚴‍♂️ Bike Delivery Path Optimization

Este projeto implementa um sistema para encontrar os melhores caminhos para entregadores utilizando bicicletas do Itaú, com check-ups obrigatórios em bases de apoio em tempos determinados.

O programa utiliza um grafo baseado em dados reais da cidade de Salvador, extraídos da API do Google Maps, e um algoritmo modificado de Floyd-Warshall para calcular o menor caminho entre os pontos.

---

## 🗂 Estrutura do Projeto

Os principais arquivos para

- `input/graph_input.json`: Arquivo de entrada com os dados do grafo.
- `main.py`: Arquivo principal para executar o programa com o grafo padrão.
- `tests/`: Pasta contendo casos de teste para validação.
- `run_tests.py`: Script para executar todos os testes.

---

## 📦 Instalação

1. Clone este repositório:

   ```bash
   git clone https://github.com/laviodias/grafos-cpp.git bike-delivery-path-optimization
   cd bike-delivery-path-optimization
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Como Usar

### 1. Rodar com os dados de entrada padrão

Para executar o programa com o grafo de entrada localizado em `input/graph_input.json`, rode o seguinte comando:

```bash
python main.py
```

### 2. Rodar os testes

Para executar todos os testes localizados na pasta `tests/input`, utilize:

```bash
python run_tests.py
```

O resultado da main.py estará em `output`, e os resultados dos testes estarão em `tests/output`.

---

## 🛠 Dependências

- Folium
- Requests
- Networkx
- dotenv
