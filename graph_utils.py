# graph_utils.py
import networkx as nx
import logging
from utils import calculate_overlap, is_valid_permutation, kmer_to_int, int_to_kmer
import heapq

def build_de_bruijn_graph(kmers, n, k):
    """Builds a De Bruijn graph from a list of k-mers."""
    graph = nx.DiGraph()
    for kmer in kmers:
        prefix = kmer[:-1]
        suffix = kmer[1:]
        graph.add_edge(prefix, suffix)
    logging.debug(f"De Bruijn graph constructed with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")
    return graph

def add_weights_to_debruijn(graph: nx.DiGraph, winners: dict, losers: dict):
    """Adds 'winner_weight' and 'loser_weight' attributes to the edges of a De Bruijn graph."""

    for u, v, data in graph.edges(data=True):
        kmer = u[1:] + v[-1]  # Reconstruct the k-mer from the edge
        # Lookup the kmer in the winners and losers dictionaries, using the (n, kmer) tuple as key
        n = len(u) + 1  # Infer n from the node length.  +1 because nodes are k-1 mers
        data['winner_weight'] = winners.get((n, kmer), 0)
        data['loser_weight'] = losers.get((n, kmer), 0)

def find_high_weight_paths(graph: nx.DiGraph, start_node: str, length_limit: int, num_paths=10) -> list[list[str]]:
    """
    Finds high-weight paths in the De Bruijn graph starting from a given node.
    Prioritizes longer paths, and higher weights.

    Returns a *list* of paths, where a path is a list of *strings*.
    """
    best_paths = []

    def dfs(current_node, current_path, current_weight):
        nonlocal best_paths
        if len(current_path) > length_limit:
            return

        # Calculate a score that prioritizes length and then weight.  Simple sum for now.
        score = len(current_path) + current_weight

        if len(best_paths) < num_paths:
            heapq.heappush(best_paths, (score, current_path.copy()))  # Use heappush
        elif score > best_paths[0][0]:  # Compare to the lowest score in the heap
            heapq.heapreplace(best_paths, (score, current_path.copy())) # Use heapreplace

        for neighbor in graph.neighbors(current_node):
            edge_data = graph.get_edge_data(current_node, neighbor)
            new_weight = current_weight + edge_data.get('winner_weight', 0) + edge_data.get('loser_weight', 0) #Using the weights.
            dfs(neighbor, current_path + [neighbor], new_weight)

    dfs(start_node, [start_node], 0)
    return [path for score, path in sorted(best_paths, reverse=True)] #Return just the paths

def analyze_debruijn_graph(graph, n, k):
    """
    Performs various analyses on a De Bruijn graph.

    Returns a dictionary containing analysis results.
    """
    analysis = {}

    # Basic Graph Properties
    analysis['num_nodes'] = graph.number_ofnodes()
    analysis['num_edges'] = graph.number_of_edges()
    analysis['density'] = nx.density(graph)

    # Node Degree Distribution
    in_degrees = [d for n, d in graph.in_degree()]
    out_degrees = [d for n, d in graph.out_degree()]
    analysis['avg_in_degree'] = sum(in_degrees) / len(in_degrees) if in_degrees else 0
    analysis['min_in_degree'] = min(in_degrees, default=0)
    analysis['max_in_degree'] = max(in_degrees, default=0)
    analysis['avg_out_degree'] = sum(out_degrees) / len(out_degrees) if out_degrees else 0
    analysis['min_out_degree'] = min(out_degrees, default=0)
    analysis['max_out_degree'] = max(out_degrees, default=0)

    # --- Imbalance Calculation ---
    total_imbalance = 0
    for node in graph.nodes:
        in_degree = graph.in_degree(node)
        out_degree = graph.out_degree(node)
        total_imbalance += abs(in_degree - out_degree)
    analysis['imbalance'] = total_imbalance / (2.0 * graph.number_of_edges()) if graph.number_of_edges() > 0 else 0 #Normalized

    # Connectivity
    try:
        analysis['is_strongly_connected'] = nx.is_strongly_connected(graph)
        analysis['num_strongly_connected_components'] = nx.number_strongly_connected_components(graph)
        analysis['average_node_connectivity'] = nx.average_node_connectivity(graph)
    except nx.NetworkXError:
        analysis['is_strongly_connected'] = False
        analysis['num_strongly_connected_components'] = 0
        analysis['average_node_connectivity'] = 0

    # Cycles (Simplified - just checks for presence/absence)
    try:
        nx.find_cycle(graph, orientation="original")
        analysis['has_cycles'] = True
    except nx.NetworkXNoCycle:
        analysis['has_cycles'] = False

    # Diameter (Computationally Expensive - use with caution!)
    # try:
    #     analysis['diameter'] = nx.diameter(graph) # This can be VERY slow
    # except nx.NetworkXError:
    #     analysis['diameter'] = -1 # Indicate that diameter couldn't be calculated

    # Spectral Analysis (Example - could add more)
    try:
        laplacian_spectrum = nx.laplacian_spectrum(graph)
        analysis['laplacian_spectrum'] = laplacian_spectrum.tolist()  # Convert numpy array to list
        analysis['algebraic_connectivity'] = nx.algebraic_connectivity(graph) # Second smallest eigenvalue of the Laplacian
    except Exception as e:
        logging.warning(f"Spectral analysis failed: {e}")
        analysis['laplacian_spectrum'] = []
        analysis['algebraic_connectivity'] = -1
    #Minimum Cut
    try:
        analysis['min_cut'] = nx.minimum_edge_cut(graph) #Gets the set of edges
        analysis['min_cut_value'] = len(analysis['min_cut']) #Gets the number of edges.
    except:
        analysis['min_cut'] = -1
        analysis['min_cut_value'] = -1

    return analysis