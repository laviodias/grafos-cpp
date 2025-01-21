import numpy as np


def graph_to_adjacency_matrix(graph):
    nodes = list(graph.nodes)
    num_nodes = len(nodes)
    node_index = {node: i for i, node in enumerate(nodes)}
    adjacency_matrix = np.zeros((num_nodes, num_nodes))

    node_coords = {node: graph.nodes[node]["coords"] for node in nodes}

    for node1, node2, data in graph.edges(data=True):
        i, j = node_index[node1], node_index[node2]
        adjacency_matrix[i, j] = data.get("duration", 0)
        adjacency_matrix[j, i] = data.get("duration", 0)

    adjacency_matrix = adjacency_matrix.astype(int)

    return adjacency_matrix, nodes, node_coords
