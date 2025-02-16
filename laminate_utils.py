# laminate_utils.py
import networkx as nx
from utils import is_valid_permutation, hash_permutation, unhash_permutation, generate_permutations

def create_laminate(sequence, n, k):
    """Creates a laminate graph from a sequence."""
    graph = nx.DiGraph()
    seq_list = [int(x) for x in sequence]
    for i in range(len(seq_list) - n + 1):
        perm = tuple(seq_list[i:i + n])
        if is_valid_permutation(perm, n):
            if i >= k:
                kmer1 = "".join(str(x) for x in seq_list[i - k:i])
                kmer2 = "".join(str(x) for x in seq_list[i - k + 1:i + 1])
                if len(kmer1) == k and len(kmer2) == k:
                    graph.add_edge(kmer1, kmer2)
    return graph

def is_compatible(permutation, laminate_graph, n, k):
    """Checks if a permutation is compatible with a laminate graph."""
    perm_str = "".join(str(x) for x in permutation)
    for i in range(len(perm_str) - k + 1):
        kmer1 = perm_str[i:i + k - 1]
        kmer2 = perm_str[i + 1:i + k]
        if len(kmer1) == k - 1 and len(kmer2) == k - 1:
            if not laminate_graph.has_edge(kmer1, kmer2):
                return False
    return True

def create_anti_laminate(anti_prodigals, n, k):
    """Creates an anti-laminate graph from a set of anti-prodigals."""

    anti_laminate = nx.DiGraph()

    # Create a complete graph with all possible (n-1)-mers as nodes and edges
    for perm in generate_permutations(n):
        perm_str = "".join(map(str, perm))
        for i in range(len(perm_str) - (k - 1) + 1):
            kmer1 = perm_str[i:i + k - 1]
            kmer2 = perm_str[i + 1:i + k]
            if len(kmer1) == k-1 and len(kmer2) == k - 1:
                anti_laminate.add_edge(kmer1, kmer2)


    # Remove edges that correspond to anti-prodigal k-mers
    for anti_prodigal in anti_prodigals:
        if len(anti_prodigal) == k:  # Ensure the anti-prodigal is a k-mer
            prefix = anti_prodigal[:-1]
            suffix = anti_prodigal[1:]
            if anti_laminate.has_edge(prefix, suffix):
                anti_laminate.remove_edge(prefix, suffix)

    return anti_laminate

def validate_laminate(laminate, n, k, laminate_type, winners, losers, layout_memory, anti_prodigals):
    """Validates a laminate graph (positive or anti-laminate).

    Now includes contextual validation against winners, losers, layout_memory,
    and anti_prodigals.
    """

    # --- (Existing Node and Edge Validity Checks - as before) ---
    # Node Validity
    for node in laminate.nodes:
        if not isinstance(node, str):
            return False, f"Invalid node type: {type(node)}"
        if len(node) != k - 1:
            return False, f"Invalid node length: {node} (should be {k-1})"
        try:  # Check if node is made of integer
            int(node)
        except:
            return False, f"Invalid node: {node}, must be made of integers."
        for digit in node:
            if not (1 <= int(digit) <= n):
                return False, f"Invalid digit in node: {node}"

    # Edge Validity
    for u, v in laminate.edges:
        if u[1:] != v[:-1]:
            return False, f"Invalid edge: ({u}, {v}) - De Bruijn property violated"

    # Laminate Type Consistency
    if laminate_type == "negative":
        if nx.number_of_nodes(laminate) > 0:
            if nx.is_strongly_connected(laminate):
                return False, "Anti-laminate cannot be strongly connected"
            try: #Check for cycles.
                nx.find_cycle(laminate, orientation="original")
                return False, "Anti-laminate cannot contain cycles"
            except nx.NetworkXNoCycle:
                pass

    # --- Contextual Validation (NEW) ---
    score = 0
    num_edges = laminate.number_of_edges()
    if num_edges > 0 :
        for u, v in laminate.edges():
            kmer = u + v[-1]  # Reconstruct the k-mer
            if laminate_type == "positive":
                # Favor winners, penalize losers
                score += winners.get((n, kmer), 0) - losers.get((n, kmer), 0)
                # Penalize transitions that are rare in the layout memory
                score -= 10 / (layout_memory.get_layout_score(((n,u),(n,v))) + 1) #Avoid division issues
            elif laminate_type == "negative":
                # Penalize winners, favor losers.
                score -= winners.get((n, kmer), 0) + losers.get((n, kmer), 0)
        score = score/num_edges #Average

    # --- Anti-Prodigal Consistency (for positive laminates) ---
    if laminate_type == "positive":
        for anti_prodigal in anti_prodigals:
            if len(anti_prodigal) == k:
                prefix = anti_prodigal[:-1]
                suffix = anti_prodigal[1:]
                if laminate.has_edge(prefix, suffix):
                    #This is bad, and should reduce the score.
                    score -= 100 # Example penalty

    return True, None, score  # Valid, plus a score


def analyze_laminate_density(laminate):
    """Calculates the density of a laminate graph."""
    num_nodes = laminate.number_of_nodes()
    num_edges = laminate.number_of_edges()
    if num_nodes == 0:
        return 0
    max_possible_edges = num_nodes * (num_nodes -1) #Each node *could* connect to each other node.
    if max_possible_edges == 0:
        return 0
    return num_edges / max_possible_edges

def analyze_laminate_connectivity(laminate):
    """Analyzes the connectivity of a laminate graph."""
    if nx.number_of_nodes(laminate) == 0:
        return 0
    return nx.average_node_connectivity(laminate)

def get_allowed_transitions(laminate, kmer):
    """Gets allowed transitions from a kmer based on the laminate."""
    return list(laminate.neighbors(kmer))

def merge_laminates(laminates, method="intersection"):
    """Merges multiple laminates using different strategies."""

    if not laminates:
        return nx.DiGraph()  # Return an empty graph if the list is empty

    if method == "intersection":
        # Keep only edges present in *all* laminates
        merged_laminate = nx.DiGraph()
        # Start with the edges of the first laminate
        for u, v in laminates[0].edges():
            add_edge = True
            for laminate in laminates[1:]:
                if not laminate.has_edge(u, v):
                    add_edge = False
                    break
            if add_edge:
                merged_laminate.add_edge(u, v)
        return merged_laminate

    elif method == "union":
        # Combine all edges from all laminates
        merged_laminate = nx.DiGraph()
        for laminate in laminates:
            merged_laminate.add_edges_from(laminate.edges())
        return merged_laminate

    elif method == "weighted_average":
        # Placeholder for weighted average merging (more complex implementation)
        # Requires edge weights in the laminate graphs.
        raise NotImplementedError("Weighted average merging not yet implemented.")
    else:
        raise ValueError("Invalid merge method.")

def create_n7_constraint_laminate(sequence, n, k):
    """Creates a laminate representing a minimal superpermutation for n=7."""
    # Implementation is identical to create_laminate
    graph = nx.DiGraph()
    seq_list = [int(x) for x in sequence]
    for i in range(len(seq_list) - n + 1):
        perm = tuple(seq_list[i:i + n])
        if is_valid_permutation(perm, n):
            if i >= k:
                kmer1 = "".join(str(x) for x in seq_list[i - k:i])
                kmer2 = "".join(str(x) for x in seq_list[i - k + 1:i + 1])
                if len(kmer1) == k and len(kmer2) == k:
                    graph.add_edge(kmer1, kmer2)
    return graph

def create_constraint_laminate(sequence, n, k):
    """Generalized Constraint Laminate"""
    return create_laminate(sequence, n, k)

#Added to update for bouncing batch.
def update_laminate(laminate, sequences, n, k, type):
    """Updates a laminate with new sequences, either adding positive edges, or removing from an anti"""
    if type == "positive":
      for seq in sequences:
        new_edges = []
        seq_list = [int(x) for x in seq]
        for i in range(len(seq_list) - n + 1):
            perm = tuple(seq_list[i:i + n])
            if is_valid_permutation(perm, n):
                if i >= k:
                    kmer1 = "".join(str(x) for x in seq_list[i - k:i])
                    kmer2 = "".join(str(x) for x in seq_list[i - k + 1:i + 1])
                    if len(kmer1) == k and len(kmer2) == k:
                        new_edges.append((kmer1,kmer2))
        laminate.add_edges_from(new_edges) #Add all the edges at once.
    elif type == "negative":
        for anti_prodigal in sequences: # Assuming sequences are now anti-prodigals
            if len(anti_prodigal) == k:  # Ensure the anti-prodigal is a k-mer
                prefix = anti_prodigal[:-1]
                suffix = anti_prodigal[1:]
                if laminate.has_edge(prefix, suffix):
                    laminate.remove_edge(prefix, suffix)
    return laminate

def add_laminate_to_album(laminate, n, k, source, description, metadata=None):
    """Adds a laminate to the 'laminate album' (a dictionary)."""
    #This would be added to data_manager, to make it more organized.
    pass

def select_laminates(n, k, task, context, all_laminates):
    """Selects laminates from the album based on the current context."""
    #This would be added to data_manager, to make it more organized.
    # Placeholder implementation:  For now, just return all laminates
    # that match the given n and k.
    selected = []
    for l_key, laminate in all_laminates.items():
      if l_key[0] == n:
        selected.append(laminate)
    return selected  # Return all for now.

def remove_laminate_from_album(laminate_id):
    """Removes a laminate from the album."""
    #This would be added to data_manager, to make it more organized.
    pass

def list_laminates():
    """Lists the available laminates in the album."""
    #This would be added to data_manager, to make it more organized.
    pass