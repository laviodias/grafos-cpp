#include <iostream>
#include <vector>
#include <queue>
#include <climits>

using namespace std;

/**
 * Modifies the adjacency matrix by removing edges with weights
 * greater than the specified weight limit. Sets those edge weights
 * to zero in the matrix.
 *
 * @param adjMatrix A reference to the adjacency matrix represented
 *                  as a vector of vectors of integers.
 * @param weightLimit The weight limit above which edges should be
 *                    removed (set to zero) in the adjacency matrix.
 */
void removeEdgesAboveLimit(vector<vector<int>>& adjMatrix, int weightLimit) {
    int n = adjMatrix.size();
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (adjMatrix[i][j] > weightLimit) {
                adjMatrix[i][j] = 0;
            }
        }
    }
}

/**
 * Implements Dijkstra's algorithm to find the shortest paths from
 * a starting vertex to all other vertices in a graph represented
 * by an adjacency matrix. The function prints the shortest distance
 * from the start vertex to each vertex. If a vertex is unreachable,
 * it prints "Inacessível".
 *
 * @param adjMatrix The adjacency matrix representing the graph,
 *                  where adjMatrix[i][j] is the weight of the edge
 *                  from vertex i to vertex j, or 0 if there is no edge.
 * @param startVertex The index of the starting vertex from which to
 *                    calculate the shortest paths.
 */

void dijkstra(const vector<vector<int>>& adjMatrix, int startVertex) {
    int n = adjMatrix.size();
    vector<int> dist(n, INT_MAX);
    vector<bool> visited(n, false);

    dist[startVertex] = 0;

    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<>> pq;
    pq.push({0, startVertex});

    while (!pq.empty()) {
        int currentDist = pq.top().first;
        int currentVertex = pq.top().second;
        pq.pop();

        if (visited[currentVertex]) continue;
        visited[currentVertex] = true;

        for (int neighbor = 0; neighbor < n; ++neighbor) {
            int weight = adjMatrix[currentVertex][neighbor];
            if (weight > 0 && !visited[neighbor]) {
                int newDist = currentDist + weight;
                if (newDist < dist[neighbor]) {
                    dist[neighbor] = newDist;
                    pq.push({newDist, neighbor});
                }
            }
        }
    }

    cout << "Distâncias do vértice " << startVertex << ":\n";
    for (int i = 0; i < n; ++i) {
        if (dist[i] == INT_MAX) {
            cout << "Vértice " << i << ": Inacessível\n";
        } else {
            cout << "Vértice " << i << ": " << dist[i] << "\n";
        }
    }
}

int main() {
    // Initial values
    vector<vector<int>> adjMatrix = {
        {0, 10, 15, 0, 0, 0},
        {10, 0, 0, 12, 0, 0},
        {15, 0, 0, 0, 10, 0},
        {0, 12, 0, 0, 2, 1},
        {0, 0, 10, 2, 0, 5},
        {0, 0, 0, 1, 5, 0}
    };
    int weightLimit = 13;
    int startVertex = 0;

    removeEdgesAboveLimit(adjMatrix, weightLimit);
    dijkstra(adjMatrix, startVertex);

    return 0;
}
