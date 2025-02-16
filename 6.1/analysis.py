# analysis.py
import itertools
import logging
import networkx as nx
import math
from collections import defaultdict
import heapq
from utils import is_valid_permutation, generate_permutations, calculate_overlap, hash_permutation, unhash_permutation, kmer_to_int, int_to_kmer
from graph_utils import build_de_bruijn_graph, add_weights_to_debruijn, analyze_debruijn_graph

def is_prodigal(sequence, all_permutations, n, min_length=20, overlap_threshold=0.95):
    """Checks if a sequence is a 'Prodigal Result'."""
    sequence_str = "".join(map(str, sequence))  # Ensure sequence is a string
    if len(sequence_str) < min_length * (n -1):
        return False

    total_length = 0
    overlap_length = 0
    num_permutations = 0

    for i in range(len(sequence_str) - n + 1):
        perm = tuple(int(x) for x in sequence_str[i:i + n])
        if is_valid_permutation(perm, n):
            total_length += n
            num_permutations += 1
            if i > 0:
                prev_perm = tuple(int(x) for x in sequence_str[i-1:i-1+n])
                if is_valid_permutation(prev_perm, n):
                  overlap_length += calculate_overlap("".join(map(str,prev_perm)), "".join(map(str, perm)))

    if num_permutations < min_length:
        return False

    if num_permutations == 0:
      return False

    max_possible_overlap = (num_permutations - 1) * (n - 1)
    overlap_rate = overlap_length / max_possible_overlap if max_possible_overlap > 0 else 0

    return overlap_rate >= overlap_threshold


def generate_hypothetical_prodigals(prodigal_results, winners, losers, n, num_to_generate=50, min_length=7, max_length=None):
    """Placeholder: Generates hypothetical prodigal results."""
    return {}

def calculate_winners_losers(superpermutations, n, k=None):
    """Calculates "Winner" and "Loser" k-mer weights, and stores by n value.
    Combines winners and losers into a single dictionary with positive/negative weights
    """
    if k is None:
      k = n -1
    all_kmers = {}  # {kmer: total_count}
    for superpermutation in superpermutations:
        s_tuple = tuple(int(x) for x in superpermutation)
        for i in range(len(s_tuple) - n + 1):
            perm = s_tuple[i:i + n]
            if is_valid_permutation(perm, n):  # Valid
                if i > 0:
                    kmer = "".join(str(x) for x in s_tuple[i - k:i])
                    all_kmers[kmer] = all_kmers.get(kmer, 0) + 1

    # Divide into "shorter" and "longer" groups based on median length
    lengths = [len(s) for s in superpermutations]
    lengths.sort()
    median_length = lengths[len(lengths) // 2]
    shorter_superpermutations = [s for s in superpermutations if len(s) <= median_length]
    longer_superpermutations = [s for s in superpermutations if len(s) > median_length]

    winners_losers = {} # Combine

    shorter_counts = {}  # {kmer: count_in_shorter}
    for superpermutation in shorter_superpermutations:
        s_tuple = tuple(int(x) for x in superpermutation)
        for i in range(len(s_tuple) - n + 1):
            perm = s_tuple[i:i + n]
            if is_valid_permutation(perm, n):
                if i > 0:
                    kmer = "".join(str(x) for x in s_tuple[i - k:i])
                    shorter_counts[kmer] = shorter_counts.get(kmer, 0) + 1

    longer_counts = {}  # {kmer: count_in_longer}
    for superpermutation in longer_superpermutations:
        s_tuple = tuple(int(x) for x in superpermutation)
        for i in range(len(s_tuple) - n + 1):
            perm = s_tuple[i:i + n]
            if is_valid_permutation(perm, n):
                if i > 0:
                    kmer = "".join(str(x) for x in s_tuple[i - k:i])
                    longer_counts[kmer] = longer_counts.get(kmer, 0) + 1

    # Calculate weights based on the difference in counts
    for kmer in all_kmers:
        score = shorter_counts.get(kmer, 0) - longer_counts.get(kmer, 0)
        winners_losers[(n, kmer)] = score # Store with n value

    return winners_losers


def identify_anti_prodigals(superpermutations, n, k, overlap_threshold, winners, losers, anti_prodigal_threshold):
    """Identifies 'anti-prodigal' k-mers within a set of superpermutations.

    Args:
        superpermutations (list): A list of superpermutation strings.
        n (int): The value of n.
        k (int): The length of k-mers to consider.
        overlap_threshold (float): Sequences with average overlap *below* this are considered for anti-prodigals.
        winners (dict):  Dictionary of winner k-mers and their weights.
        losers (dict): Dictionary of loser k-mers and their weights.
        anti_prodigal_threshold (float): Threshold for the anti-prodigal score.

    Returns:
        set: A set of 'anti-prodigal' k-mer strings.
    """
    anti_prodigals = set()

    for superpermutation in superpermutations:
        s_list = [int(x) for x in superpermutation]
        sequence_length = len(superpermutation)
        total_overlap = 0
        num_permutations = 0
        anti_prodigal_score = 0

        for i in range(len(s_list) - n + 1):
            perm = tuple(s_list[i:i + n])
            if is_valid_permutation(perm, n):
                num_permutations += 1
                if i > 0:
                    prev_perm = tuple(s_list[i-1:i-1+n])
                    if is_valid_permutation(prev_perm, n):
                        total_overlap += calculate_overlap("".join(map(str,prev_perm)), "".join(map(str, perm)))

        if num_permutations > 0:
            average_overlap = total_overlap / (num_permutations - 1) if (num_permutations - 1) > 0 else 0
            #Low Average Overlap
            if average_overlap < (n - 1) * overlap_threshold:
                anti_prodigal_score += ( (n-1) * overlap_threshold) - average_overlap

            #Iterate through for winner/loser score
            for i in range(len(s_list) - k + 1):
                kmer = "".join(map(str,s_list[i:i+k]))
                anti_prodigal_score -= winners.get((n,kmer), 0) # Subtract winner score
                anti_prodigal_score += losers.get((n,kmer), 0) # Add Loser Score

            if anti_prodigal_score > anti_prodigal_threshold:
                #Add all kmers to set.
                for i in range(len(s_list) - k + 1):
                    anti_prodigals.add("".join(map(str,s_list[i:i+k])))
    return anti_prodigals

def analyze_candidate_pool(candidate_file, n):
    """Analyzes a pool of candidate superpermutations."""
    candidates = []
    try:
        with open(candidate_file, 'r') as f:
            for line in f:
                length, is_valid, seed, sequence = line.strip().split(",", maxsplit=3)
                candidates.append({"length": int(length), "is_valid": is_valid.lower() == "true", "seed": int(seed), "sequence": sequence})
    except FileNotFoundError:
        logging.error(f"Candidate file not found: {candidate_file}")
        return {}

    logging.info(f"Analyzing candidate pool from {candidate_file}...")

    # 1. Length Distribution
    length_distribution = defaultdict(int)
    for candidate in candidates:
        length_distribution[candidate["length"]] += 1
    logging.info(f"Length Distribution: {dict(length_distribution)}")

    # 2. New Prodigal Identification
    new_prodigals = find_prodigal_results("".join(c["sequence"] for c in candidates), n) # Combine all, as one long string.
    logging.info(f"New prodigals found in candidate pool: {len(new_prodigals)}")

    # 3. Winner/Loser Frequencies (within the candidate pool)
    winners, losers = calculate_winners_losers(["".join(c["sequence"]) for c in candidates], n)

    # 4. Anti-Prodigal Identification (within the candidate pool)
    anti_prodigals = identify_anti_prodigals(["".join(c["sequence"]) for c in candidates], n, n-1, 0.8, winners, losers, 2) # Example thresholds
    logging.info(f"Anti-prodigals found in candidate pool: {len(anti_prodigals)}")

    return {
        "length_distribution": dict(length_distribution),
        "new_prodigals": new_prodigals,
        "winners": winners,
        "losers": losers,
        "anti_prodigals": anti_prodigals,
    }

def extract_useful_segments(candidate_file, n, criteria):
    """Extracts useful segments from a pool of candidates based on given criteria."""
    segments = []
    try:
      with open(candidate_file, 'r') as f:
          for line in f:
              length, is_valid, seed, sequence = line.strip().split(",", maxsplit=3)
              if criteria.get("min_length") and len(sequence) < criteria.get("min_length"):
                continue
              #Add other checks here, like presence in prodigals, winner score.
              segments.append(sequence)
    except:
      logging.error("Error extracting useful segments.")
      return []
    return segments


def calculate_sequence_winners_losers(superpermutations: list[str], n: int, sequence_length: int = 2) -> tuple[dict, dict]:
    """Calculates 'Winner' and 'Loser' weights for sequences of permutations.

    Args:
        superpermutations (list[str]): List of superpermutation strings.
        n (int): The value of n.
        sequence_length (int): The length of the permutation sequences to analyze (default: 2).

    Returns:
        tuple: (winners, losers), where winners and losers are dictionaries
               mapping sequence hashes (integers) to weights.
    """
    all_sequences = {} # {seq_hash : count}

    for superperm in superpermutations:
        s_tuple = tuple(int(x) for x in superperm)
        perms = []
        for i in range(len(s_tuple) - n + 1):
            perm = s_tuple[i:i+n]
            if is_valid_permutation(perm, n):
                perms.append(hash_permutation(perm))  # Append hash

        for i in range(len(perms) - (sequence_length -1)):
            seq = tuple(perms[i:i+sequence_length])
            seq_hash = hash(seq) #Hash the sequence of hashes.
            all_sequences[seq_hash] = all_sequences.get(seq_hash, 0) + 1

    #Divide into "shorter" and "longer"
    lengths = [len(s) for s in superpermutations]
    lengths.sort()
    median_length = lengths[len(lengths)//2]
    shorter_superpermutations = [s for s in superpermutations if len(s) <= median_length]
    longer_superpermutations = [s for s in superpermutations if len(s) > median_length]

    winners = {}
    losers = {}
    shorter_counts = {}
    for superperm in shorter_superpermutations:
        s_tuple = tuple(int(x) for x in superperm)
        perms = []
        for i in range(len(s_tuple) - n + 1):
            perm = s_tuple[i:i+n]
            if is_valid_permutation(perm, n):
                perms.append(hash_permutation(perm)) #Append hash
        for i in range(len(perms) - (sequence_length - 1)):
            seq = tuple(perms[i:i+sequence_length])
            seq_hash = hash(seq)
            shorter_counts[seq_hash] = shorter_counts.get(seq_hash, 0) + 1

    longer_counts = {}
    for superperm in longer_superpermutations:
        s_tuple = tuple(int(x) for x in superperm)
        perms = []
        for i in range(len(s_tuple) - n + 1):
            perm = s_tuple[i:i+n]
            if is_valid_permutation(perm, n):
                perms.append(hash_permutation(perm))
        for i in range(len(perms) - (sequence_length - 1)):
            seq = tuple(perms[i:i+sequence_length])
            seq_hash = hash(seq)
            longer_counts[seq_hash] = longer_counts.get(seq_hash, 0) + 1

    for seq_hash in all_sequences:
        score = shorter_counts.get(seq_hash, 0) - longer_counts.get(seq_hash, 0)
        if score > 0:
            winners[seq_hash] = score
        if score < 0:
            losers[seq_hash] = -score

    return winners, losers

def calculate_segment_efficiency(n, length, winners, losers, layout_memory, anti_laminates):
    """Calculates the efficiency of using segments of a given length."""
    pass #Placeholder.

def approximate_derivative(func, x, delta=0.001):
    """Approximates the derivative of a function at a point."""
    return (func(x + delta) - func(x)) / delta

def calculate_discrepancy(n, superpermutation_length, formula="additive"):
    if formula == "additive":
        predicted_length = math.factorial(n) + {1:1, 2:3, 3:9, 4:33, 5:153, 6:872, 7:5906}.get(n-1, 0)  # Use known values, not recursion
        if n > 7: # If greater than 7, use best known.
          try:
            with open(f"best_superpermutation_n{n-1}.txt", 'r') as f:
              best_known = len(f.read().strip())
          except:
            best_known = 0 #Placeholder
          predicted_length = best_known
    # ... (Other formula options) ...
    else:
      return 0

    return predicted_length - superpermutation_length #Can return negative

def count_imperfect_transitions(superpermutation, n):
    """Counts the number of imperfect transitions (less than maximal overlap) in a superpermutation."""
    s_list = [int(x) for x in superpermutation]
    count = 0
    for i in range(len(s_list) - n):
        perm1 = tuple(s_list[i:i + n])
        perm2 = tuple(s_list[i + 1:i + 1 + n])
        if is_valid_permutation(perm1, n) and is_valid_permutation(perm2, n):
            if calculate_overlap("".join(map(str,perm1)), "".join(map(str, perm2))) < n - 1:
                count += 1
    return count

def analyze_imperfect_transition_distribution(superpermutation, n):
    """Analyzes the distribution of imperfect transitions in a superpermutation."""
    s_list = [int(x) for x in superpermutation]
    imperfect_positions = []
    for i in range(len(s_list) - n):
        perm1 = tuple(s_list[i:i + n])
        perm2 = tuple(s_list[i + 1:i + 1 + n])
        if is_valid_permutation(perm1, n) and is_valid_permutation(perm2, n):
            if calculate_overlap("".join(map(str,perm1)), "".join(map(str, perm2))) < n - 1:
                imperfect_positions.append(i)

    # Calculate distances between imperfect transitions
    distances = [imperfect_positions[i+1] - imperfect_positions[i] for i in range(len(imperfect_positions) - 1)]

    # Calculate statistics
    if distances:
        avg_distance = sum(distances) / len(distances)
        min_distance = min(distances)
        max_distance = max(distances)
        std_dev = math.sqrt(sum((x - avg_distance) ** 2 for x in distances) / len(distances))
    else:
        avg_distance = min_distance = max_distance = std_dev = 0

    return {
        "imperfect_transition_count": len(imperfect_positions),
        "imperfect_transition_positions": imperfect_positions,
        "distances_between_imperfect_transitions": distances,
        "average_distance": avg_distance,
        "min_distance": min_distance,
        "max_distance": max_distance,
        "standard_deviation_distance": std_dev,
    }

def analyze_breakpoint(superpermutation, n, position, winners, losers, layout_memory, laminates, anti_laminates):
    """Analyzes the context of an imperfect transition (breakpoint).

    Args:
        superpermutation (str): The superpermutation string.
        n (int): The value of n.
        position (int): The index of the *start* of the first permutation in the imperfect transition.
        winners (dict): Dictionary of winner k-mers.
        losers (dict): Dictionary of loser k-mers.
        layout_memory (LayoutMemory): Layout memory object.
        laminates (list): List of positive laminates
        anti_laminates (list): List of anti-laminates

    Returns:
        dict: A dictionary containing the analysis results.
    """

    s_list = [int(x) for x in superpermutation]
    perm1 = tuple(s_list[position : position + n])
    perm2 = tuple(s_list[position + 1 : position + 1 + n])
    # Check if valid, in case of bad input
    if not (is_valid_permutation(perm1, n) and is_valid_permutation(perm2, n)):
      return {}
    overlap = calculate_overlap("".join(map(str, perm1)), "".join(map(str, perm2)))

    analysis = {
        "position": position,
        "permutations": (perm1, perm2),
        "overlap": overlap,
        "kmer_analysis": {},
        "layout_analysis": {},
        "de_bruijn_local": {},
        "laminate_analysis":{},
        "surrounding_permutations": {} #New - store context.
    }

    # --- k-mer Analysis (n-1 and n-2) ---
    for k in [n - 1, n - 2]:
        kmer1 = "".join(map(str,perm1[-(k):]))
        kmer2 = "".join(map(str,perm2[:k]))
        analysis["kmer_analysis"][f"k={k}"] = {
            "kmer1": kmer1,
            "kmer2": kmer2,
            "winner_score_kmer1": winners.get((n,kmer1), 0),
            "loser_score_kmer1": losers.get((n,kmer1), 0),
            "winner_score_kmer2": winners.get((n,kmer2), 0),
            "loser_score_kmer2": losers.get((n,kmer2), 0),
        }

    # --- Layout Memory Analysis ---
    k = n-1
    last_k_minus_1 = tuple(int(digit) for digit in superpermutation[position:position+k])
    kmer2 = tuple(int(digit) for digit in "".join(map(str, perm2))[:k])

    analysis["layout_analysis"] = layout_memory.get( ((n, last_k_minus_1),(n,kmer2)), {})


    # --- Local De Bruijn Graph ---
    local_kmers = set()
    # Capture all kmers from a surrounding area
    for i in range(position - 3 * n, position + 3 * n + 1):  #  3n on each side
        if 0 <= i < len(s_list) - n + 1:
            perm = tuple(s_list[i:i + n])
            if is_valid_permutation(perm, n):
                local_kmers.update(get_kmers("".join(map(str,perm)), n, n - 1))

    local_dbg = build_de_bruijn_graph(list(local_kmers), n, n-1) # Build the graph
    add_weights_to_debruijn(local_dbg, winners, losers) # Add weights
    analysis["de_bruijn_local"] = analyze_debruijn_graph(local_dbg, n, n-1) # Analyze

    # --- Laminate Analysis ---
    analysis["laminate_analysis"] = {"compatible_laminates": [], "incompatible_anti_laminates": []}
    for lam in laminates:
      if is_compatible(perm1, lam, n, n-1) and is_compatible(perm2, lam, n, n-1):
        analysis["laminate_analysis"]["compatible_laminates"].append(True) #Correct
      else:
        analysis["laminate_analysis"]["compatible_laminates"].append(False)
    for anti_lam in anti_laminates:
      if not is_compatible(perm1, anti_lam, n, n-1) and not is_compatible(perm2, anti_lam, n, n-1):
        analysis["laminate_analysis"]["incompatible_anti_laminates"].append(True)
      else:
        analysis["laminate_analysis"]["incompatible_anti_laminates"].append(False)

    # --- Surrounding Permutations (Context) ---
    analysis["surrounding_permutations"]["prefix"] = [tuple(s_list[i:i+n]) for i in range(max(0, position - 5*n), position) if is_valid_permutation(tuple(s_list[i:i+n]),n)] # 5 perms before
    analysis["surrounding_permutations"]["suffix"] = [tuple(s_list[i:i+n]) for i in range(position + 1, min(len(s_list) - n + 1, position + 1 + 5*n)) if is_valid_permutation(tuple(s_list[i:i+n]),n)] # 5 perms after

    return analysis

def calculate_permutation_coverage(sequence, n):
    """Calculates the percentage of n-permutations covered by a sequence."""
    all_permutations = set(generate_permutations(n))
    found_permutations = set()
    s_list = [int(x) for x in sequence]
    for i in range(len(s_list) - n + 1):
        perm = tuple(s_list[i:i + n])
        if is_valid_permutation(perm, n):
            found_permutations.add(perm)
    return len(found_permutations) / len(all_permutations) * 100

def calculate_connectivity_score(sequence, n, winners, losers, layout_memory, laminates, anti_laminates):
    """Calculates a connectivity score for a sequence."""
    # Placeholder implementation:  For now, just use a combination of
    # winner/loser density and layout memory consistency.
    # In a more complete implementation, this would also consider
    # De Bruijn graph properties.

    score = 0

    # Winner/loser density
    winner_score = 0
    loser_score = 0
    s_list = [int(x) for x in sequence]
    for i in range(len(s_list) - (n-1) + 1):
        kmer = "".join(map(str, s_list[i:i + (n-1)]))
        winner_score += winners.get((n,kmer), 0)
        loser_score  += losers.get((n,kmer), 0)
    for i in range(len(s_list) - (n-2) + 1):
        kmer = "".join(map(str, s_list[i:i + (n-2)]))
        winner_score += winners.get((n,kmer), 0)
        loser_score  += losers.get((n,kmer), 0)
    score += winner_score - loser_score

    # Layout memory consistency (simplified)
    layout_score = 0
    for i in range(len(s_list) - n):
        perm1 = tuple(s_list[i:i + n])
        perm2 = tuple(s_list[i + 1:i + 1 + n])
        if is_valid_permutation(perm1, n) and is_valid_permutation(perm2, n):
            kmer1 = tuple(s_list[i:i + n -1])
            kmer2 = tuple(s_list[i+1:i+n])
            layout_score += layout_memory.get(((n, kmer1),(n,kmer2)), {}).get('count', 0)
    score += layout_score
    return score

def insert_n_plus_1(n7_sequence, n, winners, losers, layout_memory, laminates, anti_laminates):
    """Inserts '8's into an n=7 sequence to create candidate n=8 permutations.

    Args:
        n7_sequence (str): The n=7 sequence (string of digits).
        n (int): The target n value (should be 8).
        winners (dict): Dictionary of winner k-mers and weights (for n=8).
        losers (dict): Dictionary of loser k-mers and weights (for n=8).
        layout_memory (LayoutMemory): Layout memory (for n=8).
        laminates (list): List of positive laminates (for n=8).
        anti_laminates (list): List of anti-laminates (for n=8).

    Returns:
        set: A set of n=8 permutation *hashes*.
    """
    if n != 8:
        raise ValueError("insert_n_plus_1 is designed for n=8, with n-1=7")

    candidates = set()
    n7_list = [int(x) for x in n7_sequence]

    # --- Early Laminate Filtering ---
    def is_fully_compatible(perm):
    # Check against ALL laminates and anti-laminates
        for laminate in laminates:
            if not is_compatible(perm, laminate, n, n-1): #Check n-1
                return False
            if not is_compatible(perm, laminate, n, n-2): #Check n-2
                return False
        for anti_laminate in anti_laminates:
            if not is_compatible(perm, anti_laminate, n, n-1):
                return False
            if not is_compatible(perm, anti_laminate, n, n-2):
                return False
        return True

    # Iterate through all possible insertion positions
    for i in range(len(n7_list) + 1):
        new_perm = n7_list[:i] + [8] + n7_list[i:]  # Insert '8'
        # Check if valid permutation
        if is_valid_permutation(tuple(new_perm), n):
            perm_hash = hash_permutation(tuple(new_perm))
            perm_str = "".join(map(str,new_perm))
            # Basic filtering:
            valid = True
            #Anti-Laminate Check (n-1 and n-2)
            if not is_fully_compatible(tuple(new_perm), "anti"):
                valid = False

            #Loser check (n-1 and n-2)
            for k in [n - 1, n - 2]:
                for j in range(len(perm_str) - k + 1):
                    kmer = perm_str[j:j+k]
                    if losers.get((n, kmer), 0) > 20: #Check against losers, using a threshold to determine strength.
                        valid = False
                        break
                if not valid:
                    break
            if valid:
                candidates.add(perm_hash)
    return candidates

def extract_n7_segments(n7_superpermutations, n=7):
    """Extracts segments between imperfect transitions from n=7 superpermutations.
       Now takes n value, but defaults to 7.
    """
    segments = []
    for sp in n7_superpermutations:
        imperfect_transitions = find_imperfect_transitions(sp, n)
        # Extract segments between imperfect transitions
        start = 0
        for pos, p1, p2, overlap in imperfect_transitions:
            segment = sp[start : pos + n]  # Extract segment up to *end* of first permutation
            segments.append(segment)
            start = pos + n #Start at the end of the perm.
        segments.append(sp[start:])  # Add the last segment
    return segments

def extract_nm1_segments(n_minus_1_superpermutations, n):
  """Extracts segments from n-1 superpermutations.
  """
  return extract_n7_segments(n_minus_1_superpermutations, n) # Use existing function, just named more generically

def calculate_average_overlap_imperfect_transitions(superpermutation, n):
    """Calculates the average overlap *specifically at imperfect transitions*."""
    s_list = [int(x) for x in superpermutation]
    total_overlap = 0
    num_imperfect_transitions = 0

    for i in range(len(s_list) - n):
        perm1 = tuple(s_list[i:i + n])
        perm2 = tuple(s_list[i + 1:i + 1 + n])
        if is_valid_permutation(perm1, n) and is_valid_permutation(perm2, n):
            overlap = calculate_overlap("".join(map(str, perm1)), "".join(map(str, perm2)))
            if overlap < n - 1:
                total_overlap += overlap
                num_imperfect_transitions += 1

    if num_imperfect_transitions > 0:
        return total_overlap / num_imperfect_transitions
    else:
        return n - 1  # Return maximal overlap if no imperfect transitions found

def calculate_sequence_score(sequence, n, winners, losers, layout_memory, laminates, anti_laminates, level=7):
    """Calculates an overall score for a superpermutation sequence, not just permutations

    """
    score = 0

    # 1. Overlap Score (Total)
    total_overlap = 0
    s_list = [int(x) for x in sequence]
    for i in range(len(s_list) - n):
        perm1 = tuple(s_list[i:i + n])
        perm2 = tuple(s_list[i + 1:i + 1 + n])
        if is_valid_permutation(perm1, n) and is_valid_permutation(perm2, n):
          total_overlap += calculate_overlap("".join(map(str,perm1)), "".join(map(str, perm2)))
    score += total_overlap * 5

    # 2. Winner/Loser Density
    winner_score = 0
    loser_score = 0
    for i in range(len(s_list) - (n-1) + 1):
        kmer = "".join(map(str, s_list[i:i + (n-1)]))
        winner_score += winners.get((n, kmer), 0)
        loser_score  += losers.get((n, kmer), 0)
    for i in range(len(s_list) - (n-2) + 1):
        kmer = "".join(map(str, s_list[i:i + (n-2)]))
        winner_score += winners.get((n, kmer), 0)
        loser_score  += losers.get((n, kmer), 0)
    score += winner_score * 2 score -= loser_score * 2

    # 3. Layout Memory Consistency
    layout_score = 0
    for i in range(len(s_list) - n):
        perm1 = tuple(s_list[i:i + n])
        perm2 = tuple(s_list[i + 1:i + 1 + n])
        if is_valid_permutation(perm1, n) and is_valid_permutation(perm2, n):
            kmer1 = tuple(s_list[i:i + n -1])
            kmer2 = tuple(s_list[i+1:i+n])
            layout_score += layout_memory.get(((n, kmer1),(n,kmer2)), {}).get('count', 0)
    score += layout_score * 3

    # 4. Anti-Laminate Compliance (Hard Constraint - Already Checked)

    # 5. Prodigal Bonus
    prodigal_bonus = 0
    best_prodigals = prodigal_manager.get_best_prodigals(n=n, task="generation", context={})
    for p_id, p_data in best_prodigals.items():
        if p_data['sequence'] in sequence:
            prodigal_bonus += 500
    score += prodigal_bonus

    # 6. Imperfect Transition Penalty
    num_imperfect = count_imperfect_transitions(sequence, n)
    score -= num_imperfect * 100  # Adjust weight as needed

    # 7. "Curvature" Penalty (De Bruijn-based - Example)
    # Placeholder:  Replace this with a more sophisticated curvature measure
    #              based on the De Bruijn graph.
    if level==7:
      curvature_penalty = 0
      k = n -1
      try: # May not be possible to make
        dbg = build_de_bruijn_graph(list(get_kmers(sequence, n, k)), n, k)
        curvature_penalty = analyze_debruijn_graph(dbg, n, k)['imbalance'] * 50 # Example weight
      except:
        pass #No penalty if failure

      score -= curvature_penalty

      # 8. Extensibility Bonus (if applicable, use level above)
      score += calculate_extensibility_score(sequence, n, winners, losers, layout_memory, laminates, anti_laminates) * 5
    #Further, higher level checks
    if level == 8:
      score += calculate_extensibility_score(sequence, n, winners, losers, layout_memory, laminates, anti_laminates) * 10 # Higher weight

    return score