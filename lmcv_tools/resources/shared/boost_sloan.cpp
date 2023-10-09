#include <iostream>
#include <vector>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/sloan_ordering.hpp>

using namespace std;
using namespace boost;

// Definindo Tipos
typedef std::pair<std::size_t, std::size_t> Edge;
typedef adjacency_list<
    setS,
    vecS,
    undirectedS,
    property<
        vertex_color_t,
        default_color_type,
        property<
            vertex_degree_t,
            int,
            property<
                vertex_priority_t,
                double
            >
        >
    >
> Graph;
typedef graph_traits<Graph>::vertex_descriptor Vertex;

// Função Principal
int main()
{
    // Criando Edges
    int n_vertex, n_edges, n1, n2;
    cin >> n_vertex;
    cin >> n_edges;
    Edge edges[n_edges];
    for (int i = 0; i < n_edges; i++)
    {
        cin >> n1;
        cin >> n2;
        edges[i] = Edge(n1, n2);
    }

    // Criando Graph e Adicionando Edges
    Graph G(n_vertex);
    for (int i = 0; i < n_edges; i++)
    {
        add_edge(edges[i].first, edges[i].second, G);
    }

    // Criando Vetor da Ordem
    std::vector<Vertex> sloan_order(num_vertices(G));

    // sloan_ordering
    sloan_ordering(
        G,
        sloan_order.begin(),
        get(vertex_color, G),
        make_degree_map(G),
        get(vertex_priority, G)
    );

    // Gerando Lista de Indices
    int indexes_order[n_vertex];
    int j = 0;
    for (int i : sloan_order)
    {
        indexes_order[i] = j;
        j++;
    }
    for (int i : indexes_order)
    {
        cout << i << " ";
    }

    return 0;
}