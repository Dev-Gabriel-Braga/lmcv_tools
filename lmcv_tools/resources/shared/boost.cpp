#include <iostream>
#include <vector>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/cuthill_mckee_ordering.hpp>
#include <boost/graph/king_ordering.hpp>
#include <boost/graph/sloan_ordering.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

using namespace std;
using namespace boost;

// Definindo Tipos
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

// Função de Reordenação - Algoritmo Reverse Cuthill-Mckee
void reorder_rcm(map<int, set<int>> graph, py::list new_order) {
    // Variáveis Iniciais
    const int n_vertices = graph.size();
    Graph G(n_vertices);

    // Adicionando Edges
    for (auto relation : graph) {
        for (int node : relation.second) {
            add_edge(relation.first, node, G);
        }
    }

    // Criando Vetor da Ordem
    std::vector<Vertex> rcm_order(num_vertices(G));

    // Reordenando
    cuthill_mckee_ordering(
        G, 
        rcm_order.rbegin(),
        get(vertex_color, G),
        make_degree_map(G)
    );

    // Gerando Nova Ordem de de Indices
    int j = 0;
    for (int i : rcm_order) {
        new_order[i] = j;
        j++;
    }
}

// Função de Reordenação - Algoritmo de Sloan
void reorder_sloan(map<int, set<int>> graph, py::list new_order) {
    // Variáveis Iniciais
    const int n_vertices = graph.size();
    Graph G(n_vertices);

    // Adicionando Edges
    for (auto relation : graph) {
        for (int node : relation.second) {
            add_edge(relation.first, node, G);
        }
    }

    // Criando Vetor da Ordem
    std::vector<Vertex> sloan_order(num_vertices(G));

    // Reordenando
    sloan_ordering(
        G,
        sloan_order.begin(),
        get(vertex_color, G),
        make_degree_map(G),
        get(vertex_priority, G)
    );

    // Gerando Nova Ordem de de Indices
    int j = 0;
    for (int i : sloan_order) {
        new_order[i] = j;
        j++;
    }
}

PYBIND11_MODULE(boost, m) {
    m.def("reorder_rcm", &reorder_rcm);
    m.def("reorder_sloan", &reorder_sloan);
}