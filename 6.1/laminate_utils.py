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

    Includes contextual validation against winners, losers, layout_memory,
    and anti_prodigals.
    """

    # --- (Existing Node and Edge Validity Checks - as before) ---
    # Node Validity
    for node in laminate.nodes:
        if not isinstance(node, str):
            return False, f"Invalid node type: {type(node)}", 0
        if len(node) != k - 1:
            return False, f"Invalid node length: {node} (should be {k-1})", 0
        try:  # Check if node is made of integer
            int(node)
        except:
            return False, f"Invalid node: {node}, must be made of integers.", 0
        for digit in node:
            if not (1 <= int(digit) <= n):
                return False, f"Invalid digit in node: {node}", 0

    # Edge Validity
    for u, v in laminate.edges:
        if u[1:] != v[:-1]:
            return False, f"Invalid edge: ({u}, {v}) - De Bruijn property violated", 0

    # Laminate Type Consistency
    if laminate_type == "negative":
        if nx.number_of_nodes(laminate) > 0:
            if nx.is_strongly_connected(laminate):
                return False, "Anti-laminate cannot be strongly connected", 0
            try: #Check for cycles.
                nx.find_cycle(laminate, orientation="original")
                return False, "Anti-laminate cannot contain cycles", 0
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
                score -= 10 / (layout_memory.get(((n,u),(n,v)), {'count':0})['count'] + 1) #Avoid division issues
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

    return True, None, score

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

_next_laminate_id = 1

def add_laminate_to_album(laminate, n, k, source, description, metadata=None):
    """Adds a laminate to the 'laminate album' (a dictionary)."""
    global _next_laminate_id
    laminate_id = _next_laminate_id
    _next_laminate_id += 1

    if (n, k) not in laminate_album:
        laminate_album[(n, k)] = []  # Initialize if needed

    laminate_entry = {
        "id": laminate_id,
        "graph": laminate,  # Store the actual graph object
        "source": source,
        "description": description,
        "metadata": metadata if metadata is not None else {}, #Avoid errors
        "score": 0, #Initialize to zero
    }
    # Calculate the score using validate_laminate
    is_valid, error_message, score = validate_laminate(laminate, n, k, "positive", winners, losers, layout_memory, {})
    if is_valid:
        laminate_entry["score"] = score
    else:
        logging.error(f"Failed to add laminate to album: {error_message}") #Log if not valid
        return None  # Don't add invalid laminates

    laminate_album[(n, k)].append(laminate_entry)
    logging.info(f"Added laminate to album: ID={laminate_id}, Source={source}, n={n}, k={k}")
    return laminate_id

def select_laminates(n, k, task, context, all_laminates):
    """Selects laminates from the album based on the current context."""
    # Placeholder implementation:  Select a few "good" laminates based on source
    # and score.  In a real implementation, this would be much more sophisticated.

    relevant_laminates = []
    high_score_laminates = []

    # Filter by n and k
    if (n,k) in all_laminates:
        for laminate_entry in all_laminates[(n, k)]:
            if laminate_entry['score'] > 0: #Only use laminates that have passed validation.
                relevant_laminates.append(laminate_entry)

    # Sort by score (descending)
    relevant_laminates = sorted(relevant_laminates, key=lambda x: x['score'], reverse = True)

    # Select top scoring.
    selected_laminates = relevant_laminates[:5] #Get 5 for now.

    # Return the *graphs* themselves, not the entire entry
    return [lam["graph"] for lam in selected_laminates]

def remove_laminate_from_album(laminate_id):
    """Removes a laminate from the album by ID."""
    global laminate_album
    for key in list(laminate_album.keys()):  # Iterate over a copy of keys
        laminates_list = laminate_album[key]
        for laminate in laminates_list:
            if laminate["id"] == laminate_id:
                laminates_list.remove(laminate)
                logging.info(f"Removed laminate with ID {laminate_id} from album.")
                return
        if not laminates_list:  # If the list is empty after removal, delete the key
          del laminate_album[key]

def list_laminates():
    """Lists the available laminates in the album, with their metadata."""
    #This would be added to data_manager, to make it more organized.
    print("Current Laminates in Album:")
    for key, lam_list in laminate_album.items(): #Iterate through dict
        print(f"  n={key[0]}, k={key[1]}:")
        for laminate in lam_list: #Iterate through list
            print(f"    ID: {laminate['id']}")
            print(f"    Source: {laminate['source']}")
            print(f"    Description: {laminate['description']}")
            print(f"    Score: {laminate['score']}")
            if laminate['metadata']:
                print(f"    Metadata: {laminate['metadata']}")
            print("-" * 20)