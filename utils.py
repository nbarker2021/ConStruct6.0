# utils.py
import itertools
import hashlib
import logging
import math

def setup_logging():
    """Sets up logging to a file."""
    logging.basicConfig(level=logging.DEBUG, filename='superpermutation.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

def compute_checksum(data: str) -> str:
    """Computes the SHA-256 checksum of a string."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def generate_permutations(n: int):
    """Generates all permutations of numbers from 1 to n."""
    return list(itertools.permutations(range(1, n + 1)))

def is_valid_permutation(perm: tuple, n: int) -> bool:
    """Checks if a tuple is a valid permutation."""
    return len(perm) == n and set(perm) == set(range(1, n + 1))

def calculate_overlap(s1: str, s2: str) -> int:
    """Calculates the maximum overlap between two strings."""
    max_len = min(len(s1), len(s2))
    for i in range(max_len, 0, -1):
        if s1[-i:] == s2[:i]:
            return i
    return 0

def normalize_sequence(seq: str) -> str:
    """Normalizes a superpermutation sequence by rotating it."""
    min_char = min(seq)
    min_indices = [i for i, c in enumerate(seq) if c == min_char]
    rotations = [seq[i:] + seq[:i] for i in min_indices]
    return min(rotations)

def kmer_to_int(kmer):
    """Converts a k-mer tuple to an integer."""
    int_kmer = 0
    for i, digit in enumerate(kmer):
        int_kmer = int_kmer * 10 + digit
    return int_kmer

def int_to_kmer(int_kmer, k):
    """Converts an integer to a k-mer tuple."""
    kmer = ()
    for _ in range(k):
        digit = int_kmer % 10
        kmer = (digit,) + kmer
        int_kmer //= 10
    return kmer

def hash_permutation(perm):
    """Hashes a permutation (tuple or int)."""
    if isinstance(perm, tuple):
        return hash(perm)
    elif isinstance(perm, int):
        return perm
    else:
        raise TypeError("Permutation must be int or tuple")

def unhash_permutation(perm_hash, n):
    """Unhashes a permutation (int to tuple)."""
    if isinstance(perm_hash, int):
        return int_to_kmer(perm_hash, n)
    else:
        raise TypeError("Permutation hash must be int")

def generate_n_minus_1_superpermutation(n, seed):
    """Generates a distinct superpermutation for n-1.
    """
    #We will use our modified n-1 code.

    # --- Constants for n-1 ---
    prodigal_overlap_threshold = 0.98
    prodigal_min_length = 6
    if n-1 > 6:
      prodigal_min_length = int(0.75 * math.factorial(n-1))
    hypothetical_prodigal_overlap_threshold = 0.90
    hypothetical_prodigal_min_length = 4
    hypothetical_prodigal_generation_count = 50  # n-1 is fast
    num_iterations = 1000 #Should be enough.
    layout_k_values = [n - 2, n - 3]

    if seed is not None:
        random.seed(seed)

    # Initialize data structures
    prodigal_manager = ProdigalManager(n-1) # Using prodigal manager

    # Load initial data, if not supplied, it starts with default values.
    winners = {}
    losers = {}

    meta_hierarchy = {}  # Track strategy effectiveness
    limbo_list = set()  # Set of permutation hashes.
    eput = {}  # The Enhanced Permutation Universe Tracker

    # Add initial n-1 prodigals, which in this case is ALWAYS the original 5906
    next_prodigal_id = 0
    

    #Create Initial Laminate, using all available n-7s
    laminates = []

    layout_memory = LayoutMemory() #Create a layout memory
    superpermutation = ""
    # --- Main Iterative Loop ---
    #for iteration in range(num_iterations): #Now stops when complete, or stuck, or iteration limit.
    iteration = 0
    while len(superpermutation) < sum(math.factorial(i) for i in range(1,n)) and iteration < num_iterations:
        iteration += 1
        #print(f"Starting iteration {iteration}...") #Removed for n=8 use.
        start_time = time.time()

        # 1. Generate Hypothetical Prodigals
        hypothetical_prodigals = generate_hypothetical_prodigals(prodigal_results, winners, losers, n-1, num_to_generate=hypothetical_prodigal_generation_count, min_length=hypothetical_prodigal_min_length, max_length=(n-1)*15) #Longer length limit, due to n=7 speed
        #print(f"  Generated {len(hypothetical_prodigals)} hypothetical prodigals.")

        #Add to the prodigals list
        for h_id, h_prodigal in hypothetical_prodigals.items():
            prodigal_manager.add_prodigal(h_prodigal['sequence'], n-1, "hypothetical") ##########Needs to add all data, not just sequence.
            next_prodigal_id += 1
            # Create and add a laminate for the new prodigal
            laminates.append(create_laminate(h_prodigal.sequence, n-1, n-2))
            laminates.append(create_laminate(h_prodigal.sequence, n-1, n-3))


        #Find best prodigals
        best_prodigals = prodigal_manager.get_best_prodigals(n=n-1, task="generation", context={})
        # 2. Construct Superpermutation (using the dynamic approach, starting from EMPTY)
        superpermutation, used_permutations = construct_superpermutation([], best_prodigals, winners, losers, layout_memory, meta_hierarchy, limbo_list, n-1, hypothetical_prodigals, laminates)
        #print(f"  Superpermutation length: {len(superpermutation)}")

        # 3. Update Data
        analysis_results = analyze_superpermutation(superpermutation, n-1)
        #print(f"  Valid: {analysis_results['validity']}")
        #print(f"  Overlap Distribution: {analysis_results['overlap_distribution']}")

        # Check for  length and distinctness
        if analysis_results['validity'] and len(superpermutation) == sum(math.factorial(i) for i in range(1,n)):
            return superpermutation

        # Find and add new prodigal results. Stricter criteria.
        new_prodigals = find_prodigal_results(superpermutation, n-1, overlap_threshold=prodigal_overlap_threshold,  min_length=prodigal_min_length)
        for prodigal_seq in new_prodigals:
            prodigal_manager.add_prodigal(prodigal_seq, n-1, "dynamic_generation")

        # Update "Winners" and "Losers" (using the new superpermutation, and k=6 and k=5)
        new_winners6, new_losers6 = calculate_winners_losers([superpermutation], n-1, k=n-2)
        new_winners5, new_losers5 = calculate_winners_losers([superpermutation], n-1, k=n-3)

        for kmer, weight in new_winners6.items():
            winners[kmer] = winners.get(kmer, 0) + weight
        for kmer, weight in new_losers6.items():
            losers[kmer] = losers.get(kmer, 0) + weight
            limbo_list.add(kmer) # Add to limbo list
        for kmer, weight in new_winners5.items():
            winners[kmer] = winners.get(kmer, 0) + weight
        for kmer, weight in new_losers5.items():
            losers[kmer] = losers.get(kmer, 0) + weight
            limbo_list.add(kmer)

        #Higher Order Winners/Losers
        new_seq_winners, new_seq_losers = calculate_sequence_winners_losers([superpermutation],n-1)
        for seq_hash, weight in new_seq_winners.items():
            if seq_hash in winners:
                winners[seq_hash] += weight
            else:
                winners[seq_hash] = weight
        for seq_hash, weight in new_seq_losers.items():
            if seq_hash in losers:
                losers[seq_hash] += weight
            else:
                losers[seq_hash] = weight

        # Update ePUT (add all *used* permutations)
        s_tuple = tuple(int(x) for x in superpermutation)
        for i in range(len(s_tuple) - (n-1) + 1):
            perm = s_tuple[i:i+(n-1)]
            if is_valid_permutation(perm, n-1):
                perm_hash = hash_permutation(perm)
                if perm_hash not in eput:
                    eput[perm_hash] = PermutationData(perm, in_sample=False, creation_method="dynamic_generation")
                eput[perm_hash].used_count += 1
                eput[perm_hash].used_in_final = True
                # Update neighbors in ePUT (using consistent k values)
                if i > 0:
                    prev_perm = s_tuple[i-1:i-1+(n-1)]
                    if is_valid_permutation(prev_perm, n-1):
                        eput[perm_hash].neighbors.add(hash_permutation(prev_perm))
                if i < len(s_tuple) - (n-1):
                    next_perm = s_tuple[i+1:i+1+(n-1)]
                    if is_valid_permutation(next_perm, n-1):
                        eput[perm_hash].neighbors.add(hash_permutation(next_perm))

        # Update Layout Memory
        layout_memory.add_sequence(superpermutation, n-1, n-2, f"run_{seed}")  # Add the new superpermutation
        layout_memory.add_sequence(superpermutation, n-1, n-3, f"run_{seed}")

        # Update "Meta-Hierarchy" (simplified for this example)
        meta_hierarchy.setdefault("run_lengths", []).append(len(superpermutation))
        meta_hierarchy.setdefault("prodigal_counts", []).append(len(prodigal_results))
        total_hypotheticals = len(hypothetical_prodigals)
        successful_hypotheticals = 0
        for h_id, h_prodigal in hypothetical_prodigals.items():
            if h_prodigal.sequence in superpermutation:
                successful_hypotheticals += 1
        success_rate = (successful_hypotheticals / total_hypotheticals) if total_hypotheticals > 0 else 0.0

        meta_hierarchy.setdefault("hypothetical_success_rate",[]).append(success_rate)
        # --- Dynamic Parameter Adjustments (Example) ---
        if len(meta_hierarchy["prodigal_counts"]) > 2 and meta_hierarchy["prodigal_counts"][-1] <= meta_hierarchy["prodigal_counts"][-2]:
            # Prodigal discovery rate is slowing down
            prodigal_overlap_threshold = max(0.90, prodigal_overlap_threshold - 0.01)  # Decrease threshold, but not below 0.90
            prodigal_min_length = max(7, prodigal_min_length - 2) # Reduce Min Length, not below 7.
            #print(f"  Adjusted Prodigal Criteria: Overlap Threshold = {prodigal_overlap_threshold}, Min Length = {prodigal_min_length}") # For Debugging

        #Stopping condition for n-1
        if len(superpermutation) == sum(math.factorial(i) for i in range(1,n)):
            return superpermutation

    return None  # Failed to find a  superpermutation within the iteration limit