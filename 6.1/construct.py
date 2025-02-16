# construct.py
import random
import logging
import time
import math
from collections import defaultdict
import heapq

# Local imports - assuming all files are in the same directory
import utils
import analysis
import graph
import laminate
import prodigal
from formulas import sp_v14, segment_length_best  # Import specific formulas


def construct_superpermutation(n, config):
    """Constructs a superpermutation for a given n, using the specified configuration.

    This is the main entry point for the superpermutation construction process.  It
    implements the iterative n-building approach, starting from n=1 and working up
    to the target n value.

    Args:
        n (int): The target n value.
        config (dict): A dictionary containing configuration parameters.

    Returns:
        str: The (hopefully minimal) superpermutation string, or None if construction fails.
    """
    utils.setup_logging()
    random.seed(config["seed"])

    # Initialize data structures (empty, or loaded from previous n if available)
    winners = defaultdict(float)  # Using defaultdict for easier updates
    losers = defaultdict(float)
    layout_memory = {}  # Using a standard dictionary
    prodigal_manager = prodigal.ProdigalManager(n)  # Manage prodigals
    laminates = {}  # { (n, k): [list of laminates] }
    anti_laminates = {}
    best_known_length = float('inf')  # Start with infinity
    best_known_superpermutation = ""

    for current_n in range(1, n + 1):
        logging.info(f"Constructing superpermutation for n = {current_n}")
        start_time = time.time()

        # --- Data Loading/Initialization (for current_n) ---
        # Load data from the previous n, if available.  Adapt the keys/structures as needed.
        if current_n > 1:
            prev_n = current_n - 1
            # Example of loading and adapting winners/losers:
            prev_winners, prev_losers = analysis.calculate_winners_losers([best_known_superpermutation], prev_n) # Use best from prev run
            for kmer, weight in prev_winners.items():
                winners[(prev_n, kmer)] = weight
            for kmer, weight in prev_losers.items():
                losers[(prev_n, kmer)] = weight
            # layout_memory = ...  # Adapt layout memory (if applicable) - potentially project/extend
            # prodigal_manager.load_prodigals(prev_n)  # Load prodigals from previous n
            # laminates[prev_n] = ... # Load/adapt laminates
            # anti_laminates[prev_n] = ... # Load/adapt anti-laminates

            #Get any new n-1 values to add to the prodigal list
            new_prodigals = analysis.extract_initial_prodigals([best_known_superpermutation], current_n, 50, 0.98)
            for key, value in new_prodigals.items():
                prodigal_manager.add_prodigal(value['sequence'],current_n, "Initial Prodigal")
            #Create Initial Laminate
            laminates[current_n, current_n-1] = [laminate.create_laminate(best_known_superpermutation, current_n, current_n-1)]
            laminates[current_n, current_n-2] = [laminate.create_laminate(best_known_superpermutation, current_n, current_n-2)]
            #Create Initial Anti-Laminate
            anti_prodigal_seqs = analysis.identify_anti_prodigals([best_known_superpermutation], current_n, current_n-1, 0.6, winners, losers, 2) #Get  anti-prodigals
            if anti_prodigal_seqs:
                new_anti_laminate = laminate.create_anti_laminate(anti_prodigal_seqs, current_n, current_n-1)
                if (current_n, current_n-1) not in anti_laminates:
                    anti_laminates[(current_n, current_n-1)] = []
                anti_laminates[(current_n, current_n-1)].append(new_anti_laminate)

            anti_prodigal_seqs = analysis.identify_anti_prodigals([best_known_superpermutation], current_n, current_n-2, 0.6, winners, losers, 2) #Get anti-prodigals
            if anti_prodigal_seqs:
                new_anti_laminate = laminate.create_anti_laminate(anti_prodigal_seqs, current_n, current_n-2)
                if (current_n, current_n-2) not in anti_laminates:
                    anti_laminates[(current_n, current_n-2)] = []
                anti_laminates[(current_n, current_n-2)].append(new_anti_laminate)


        if current_n <= 5:
            # --- Base Cases (n <= 5) ---  Use direct generation
            superpermutation = utils.generate_n_minus_1_superpermutation(current_n, config["seed"])
            if superpermutation:
                logging.info(f"Generated minimal superpermutation for n={current_n} (length: {len(superpermutation)})")
                best_known_length = len(superpermutation)
                best_known_superpermutation = superpermutation

                # Analyze and extract data from this example to add to our data sets.
                analysis.analyze_superpermutation(superpermutation, current_n)
                new_winners, new_losers = analysis.calculate_winners_losers([superpermutation],current_n)
                for kmer, weight in new_winners.items():
                    winners[(current_n, kmer)] = winners.get((current_n, kmer), 0) + weight
                for kmer, weight in new_losers.items():
                    losers[(current_n, kmer)] = losers.get((current_n, kmer), 0) + weight
                layout_memory = {} #Clear, and rebuild.
                layout_memory.add_sequence(superpermutation, current_n, current_n-1, "Initial")
                layout_memory.add_sequence(superpermutation, current_n, current_n-2, "Initial")
                new_prodigals = analysis.find_prodigal_results(superpermutation, current_n)
                for prodigal_seq in new_prodigals:
                    prodigal_manager.add_prodigal(prodigal_seq,current_n, "Initial")
                new_anti_prodigals = analysis.identify_anti_prodigals([superpermutation], current_n, current_n-1, 0.6, winners, losers, 2)
                anti_laminates[current_n, current_n-1] = [laminate.create_anti_laminate(new_anti_prodigals, current_n, current_n-1)]
                new_anti_prodigals = analysis.identify_anti_prodigals([superpermutation], current_n, current_n-2, 0.6, winners, losers, 2)
                anti_laminates[current_n, current_n-2] = [laminate.create_anti_laminate(new_anti_prodigals, current_n, current_n-2)]

            else:
                logging.error(f"Failed to generate superpermutation for n={current_n}")
                return None  # Exit if we can't even generate the base cases
        else:
            # --- Main Construction Loop (n >= 6) ---

            # Load any existing "best" superpermutation, and create constraint laminate
            constraint_laminates = []
            best_known_superpermutation = "" #Placeholder
            # ... (Load best_known_superpermutation from file, if it exists)
            # if best_known_superpermutation:
            #     best_known_length = len(best_known_superpermutation)
            #     constraint_laminates.append(create_constraint_laminate(best_known_superpermutation, current_n, current_n - 1))

            missing_permutations = set(utils.hash_permutation(p) for p in utils.generate_permutations(current_n))
            superpermutation = "" #Initialize empty string.

            while True:  # Continue until a valid superpermutation is found or max iterations reached
                # 1. Select a Strategy (dynamically, based on config and current state)
                strategy = select_strategy(current_n, config, laminates.get((current_n,current_n-1),[]), anti_laminates.get((current_n, current_n-1),[]))
                logging.info(f"Selected strategy: {strategy}")

                # 2. Generate Hypothetical Superpermutation
                hypothetical_sp = generate_hypothetical_superpermutation(current_n, strategy, prodigal_manager,
                                                                        winners, losers, layout_memory,
                                                                        best_known_length, config["seed"],
                                                                        laminates.get((current_n, current_n-1),[]), anti_laminates.get((current_n, current_n-1),[]),
                                                                        constraint_laminates, missing_permutations)
                #Check length.
                if hypothetical_sp:
                    if len(hypothetical_sp) > best_known_length:
                        continue #Move on if too long.

                if not hypothetical_sp:
                    logging.warning(f"Hypothetical generation failed (strategy: {strategy}).")
                    continue  # Try again with a different strategy/seed

                # 3. Bouncing Batch Test
                is_valid, length, new_winners, new_losers, _ = bouncing_batch_test(
                    hypothetical_sp, current_n, config["grid_dimensions"], prodigal_manager,
                    None, anti_laminates.get((current_n, current_n-1),[]), constraint_laminates, winners, losers, layout_memory
                )  # No layout_memory_filename for single-process

                # 4. Data Update and Analysis
                analysis.update_winners_losers(winners, losers, new_winners, new_losers) # Update winners/losers

                new_anti_prodigals = analysis.identify_anti_prodigals([hypothetical_sp], current_n, current_n-1, 0.6, winners, losers, 2) #Get  anti-prodigals
                if new_anti_prodigals:
                    new_anti_laminate = laminate.create_anti_laminate(new_anti_prodigals, current_n, current_n-1)
                    if (current_n, current_n-1) not in anti_laminates:
                        anti_laminates[(current_n, current_n-1)] = []
                    anti_laminates[(current_n, current_n-1)].append(new_anti_laminate)

                new_anti_prodigals = analysis.identify_anti_prodigals([hypothetical_sp], current_n, current_n-2, 0.6, winners, losers, 2) #Get  anti-prodigals
                if new_anti_prodigals:
                    new_anti_laminate = laminate.create_anti_laminate(new_anti_prodigals, current_n, current_n-2)
                    if (current_n, current_n-2) not in anti_laminates:
                        anti_laminates[(current_n, current_n-2)] = []
                    anti_laminates[(current_n, current_n-2)].append(new_anti_laminate)

                # Find and add new prodigal results.
                new_prodigals = analysis.find_prodigal_results(hypothetical_sp, current_n)
                for prodigal_seq in new_prodigals:
                    prodigal_manager.add_prodigal(prodigal_seq,current_n, "dynamic_generation", winners, losers, layout_memory, laminates.get((current_n, current_n-1),[]), anti_laminates.get((current_n, current_n-1),[]))
                # ... (Other analysis functions, as needed) ...

                # 5. Check for Completion and Validity
                if is_valid:
                    logging.info(f"Valid superpermutation found for n={current_n}, length={length} using strategy {strategy}")

                    if length < best_known_length:
                        best_known_length = length
                        best_known_superpermutation = hypothetical_sp
                        logging.info(f"New best superpermutation found for n={current_n}! Length: {best_known_length}")
                        # Save the new best superpermutation
                        with open(f"best_superpermutation_n{current_n}.txt", "w") as f:
                            f.write(best_known_superpermutation)

                        # Create new constraint laminate
                        constraint_laminates = []
                        constraint_laminates.append(create_constraint_laminate(best_known_superpermutation, current_n, current_n - 1))
                        constraint_laminates.append(create_constraint_laminate(best_known_superpermutation, current_n, current_n - 2))


                    # Even if it's not shorter, we might still want to keep it (for diversity)
                    # ... (Logic for saving/analyzing valid superpermutations) ...

                    break  # Exit inner loop if valid
                else:
                    logging.info(f"Generated superpermutation is not valid (length: {length}).")

                # 6. Reconfiguration (periodically)

                # --- Check for Stagnation ---

            if current_n > 5:
                logging.info (f"Best known length for n={current_n}: {best_known_length}") #Print every loop.

        # --- Prepare Data for Next n ---
        # Extract and save all relevant data to be carried over
        # to the next n value.  This includes:

    return best_known_superpermutation


def select_strategy(n, config, laminates, anti_laminates):
    """Selects a superpermutation generation strategy based on the configuration and current state."""
    available_strategies = list(config["generation_strategies"].keys())
    strategy_weights = list(config["generation_strategies"].values())

    # Example of dynamic strategy selection based on laminate density/connectivity:
    if laminates:  # Use the first laminate for analysis, for now
        laminate_density = analyze_laminate_density(laminates[0])
        laminate_connectivity = analyze_laminate_connectivity(laminates[0])

        # Adjust strategy weights based on laminate properties (example)
        if laminate_density < 0.1:
            # If laminate is sparse, increase weight for exploratory strategies
            strategy_weights[available_strategies.index("random_constrained")] *= 2
            strategy_weights[available_strategies.index("de_bruijn")] *= 1.5
        elif laminate_connectivity > 0.8:
            # If laminate is highly connected, increase weight for strategies that exploit structure
            strategy_weights[available_strategies.index("prodigal_combination")] *= 2
            strategy_weights[available_strategies.index("n_minus_1_shell")] *= 1.5

        # Normalize weights (important!)
        total_weight = sum(strategy_weights)
        normalized_weights = [w / total_weight for w in strategy_weights]
    else:
        total_weight = sum(strategy_weights)
        normalized_weights = [w/ total_weight for w in strategy_weights] # Default.

    strategy = random.choices(available_strategies, weights=normalized_weights)[0]
    return strategy

def generate_hypothetical_superpermutation(n, strategy, prodigal_manager, winners, losers, layout_memory, best_known_length, seed, laminates, anti_laminates, constraint_laminates, missing_permutations = None):
    """Generates a complete hypothetical superpermutation using a specified strategy."""

    random.seed(seed)

    if strategy == "n_minus_1_shell":
        # 1. Select n-1 Segments
        segments = select_n_minus_1_segments(n, prodigal_manager, winners, losers, layout_memory)
        # 2. Insert nth Symbol
        extended_segments = [analysis.insert_n_plus_1(seg, n, winners, losers, layout_memory, laminates, anti_laminates) for seg in segments]
        # 3. Connect Segments
        superpermutation = connect_segments(n, extended_segments, prodigal_manager, winners, losers, layout_memory, best_known_length, seed, laminates, anti_laminates, constraint_laminates, missing_permutations)
        return superpermutation

    elif strategy == "prodigal_combination":
        #Get best prodigals
        best_prodigals = prodigal_manager.get_best_prodigals(n=n, task="generation", context={})
        num_prodigals_to_combine = random.randint(2, min(4, len(best_prodigals))) # Combine 2-4 Prodigals, limit by how many exist.  Could make this dynamic
        if num_prodigals_to_combine == 0:
            return None #If there aren't any prodigals, we can't use this.

        # Select prodigals for combination.
        selected_prodigal_ids = random.sample(list(best_prodigals.keys()), num_prodigals_to_combine)
        selected_prodigals = [best_prodigals[pid]['sequence'] for pid in selected_prodigal_ids]

        # Sort by length, descending.
        selected_prodigals.sort(key=lambda p: len(p), reverse=True)

        # Use formula to estimate segment lengths
        segment_lengths = []

        for _ in range(len(selected_prodigals)-1):
            segment_length = int(formulas.segment_length_best(n, calculate_i_n(n)) * len(selected_prodigals)) #Use formula
            if segment_length <= 0: #Safety
                segment_length = n
            segment_lengths.append(segment_length)
        segment_lengths.append(max(n, best_known_length - sum(segment_lengths))) #Ensure that it is long enough to hit target on fill.

        combined_sequence = ""

        #Randomize starting location.
        start_location = random.randint(0,len(selected_prodigals)-1)
        prodigal_order = []
        for i in range(len(selected_prodigals)):
            prodigal_order.append(selected_prodigals[(start_location + i) % len(selected_prodigals)])

        for i in range(len(prodigal_order)):
            prodigal = prodigal_order[i]
            target_length = segment_lengths[i]

            # Get a  section of the prodigal.
            start_index = random.randint(0, max(0, len(prodigal) - target_length))  # Ensure valid start
            current_sequence = prodigal[start_index : start_index + target_length]

            # Connect to previous
            if combined_sequence != "":
                overlap = calculate_overlap(combined_sequence, current_sequence)
                if overlap == 0: #Need to use the combiner
                    prefix = combined_sequence[-(n-1):]
                    suffix = current_sequence[:n-1]
                    candidates = generate_candidates("".join(prefix), set(),  prodigal_manager, winners, losers, n, {}, set(), anti_laminates, constraint_laminates, end="suffix")
                    if candidates:
                        # Choose the best candidate based on winners/losers, and other data.
                        best_candidate = None
                        best_score = -float('inf')
                        for cand_hash in candidates:
                            cand_perm = unhash_permutation(cand_hash, n)
                            cand_str = "".join(str(x) for x in cand_perm)
                            score = calculate_score(combined_sequence, cand_hash, prodigal_manager, winners, losers, layout_memory, n, set(), {}, anti_laminates, constraint_laminates) #Use all data.

                            if score > best_score:
                                best_score = score
                                best_candidate = cand_str

                        overlap = calculate_overlap(combined_sequence, best_candidate)
                        combined_sequence += best_candidate[overlap:]
                    else:
                        return None #Skip if we cannot connect.

                else: #Overlap exists
                    combined_sequence += current_sequence[overlap:]
            else:
                combined_sequence = current_sequence
        return combined_sequence

    elif strategy == "de_bruijn":
        # De Bruijn graph-guided generation
        k = n - 1
        dbg = build_de_bruijn_graph(list(get_kmers("".join(str(p) for p in generate_permutations(n)),n,k)), n, k) # Build a complete graph.
        add_weights_to_debruijn(dbg, winners, losers)

        # Find a long, high-weight path (not necessarily Hamiltonian)
        start_node = random.choice(list(dbg.nodes))  # Choose a random starting node
        paths = find_high_weight_paths(dbg, start_node, best_known_length) # Use function

        best_path = None
        if paths:
            best_path = paths[0] #Best path

        if best_path:
            # Convert the path to a superpermutation string
            sequence = best_path[0] # Start with the first k-1 mer.
            for node in best_path[1:]:
                sequence += node[-1]  # Add the last character of the next node

            return sequence
        else:
            return None

    elif strategy == "mutation":
        # Mutate an existing (incomplete) superpermutation
        if not best_known_superpermutation:
          return "" # Nothing to mutate.
        working_copy = list(best_known_superpermutation)[:]  # Work on a copy
        mutation_type = random.choice(["swap", "insert", "delete", "reverse", "kmer_swap"])
        mutation_count = 0
        max_mutations = 10 #Limit

        if mutation_type == "swap":
            # Swap two permutations
            while mutation_count < max_mutations:
              idx1 = random.randint(0, len(working_copy) - n)
              idx2 = random.randint(0, len(working_copy) - n)
              perm1 = tuple(int(x) for x in working_copy[idx1:idx1+n])
              perm2 = tuple(int(x) for x in working_copy[idx2:idx2+n])
              if is_valid_permutation(perm1, n) and is_valid_permutation(perm2, n): #Must be valid to swap
                working_copy[idx1:idx1+n], working_copy[idx2:idx2+n] = working_copy[idx2:idx2+n], working_copy[idx1:idx1+n] # Do the swap
                mutation_count +=1
        elif mutation_type == "insert":
            # Insert a random permutation (respecting laminates)
            while mutation_count < max_mutations:
                insert_pos = random.randint(0, len(working_copy))
                candidates = generate_candidates("".join(working_copy), set(), prodigal_manager, winners, losers, n, {}, set(), anti_laminates, constraint_laminates)
                if candidates:
                    new_perm_hash = random.choice(list(candidates))
                    new_perm = unhash_permutation(new_perm_hash, n)
                    working_copy = working_copy[:insert_pos] + list(str(x) for x in new_perm) + working_copy[insert_pos:] #Insert
                    mutation_count+=1
                else:
                  break #Move on if no valid candidates

        elif mutation_type == "delete":
            # Delete a permutation
            while mutation_count < max_mutations:
              delete_pos = random.randint(0, len(working_copy) - n)
              perm = tuple(int(x) for x in working_copy[delete_pos:delete_pos + n])
              if is_valid_permutation(perm, n):
                working_copy = working_copy[:delete_pos] + working_copy[delete_pos + n:]
                mutation_count+=1 #Remove
        elif mutation_type == "reverse":
            # Reverse a section
            while mutation_count < max_mutations:
              start_pos = random.randint(0, len(working_copy) - n)
              end_pos = random.randint(start_pos + n, min(len(working_copy), start_pos + 5*n))  # Limit length for now
              #Make sure we are reversing valid perms
              valid = True
              for i in range(start_pos, end_pos -n + 1):
                perm = tuple(int(x) for x in working_copy[i:i+n])
                if not is_valid_permutation(perm, n):
                  valid = False
                  break
              if valid:
                working_copy[start_pos:end_pos] = working_copy[start_pos:end_pos][::-1]  # Reverse that section
                mutation_count += 1

        elif mutation_type == "kmer_swap":
          #Swap two k-mers
          pass #Removed for now

        return "".join(working_copy)

    elif strategy == "random_constrained":
        # Generate a random permutation sequence, of set length.
        superperm_list = []
        all_permutations = generate_permutations(n)
        random.shuffle(all_permutations)
        superperm_list.append(list(all_permutations[0]))
        overlap = n-1

        for perm in all_permutations[1:]:
            perm_str = "".join(map(str, perm))
            overlap = calculate_overlap("".join(map(str,superperm_list[-1])), perm_str)
            superperm_list.append(list(perm_str[overlap:]))
        ret =  "".join(map(str, superperm_list))
        if len(ret) > best_known_length:
          return None
        return ret
    else:
        logging.error(f"Unknown superpermutation generation strategy: {strategy}")
        return None
def complete_from_partial(partial_superpermutation, n, missing_permutations, prodigal_manager, winners, losers, layout_memory, limbo_list, eput, best_known_length, anti_laminates, constraint_laminates):
    """
    Attempts to complete a partial superpermutation to the target length, using all tools to find best fit.
    Returns None if it cannot complete to the target length. Now uses constraint laminates
    """
    working_superpermutation = list(partial_superpermutation)
    attempts = 0
    max_attempts = 1000  # Limit attempts to avoid infinite loops

    while missing_permutations and len("".join(working_superpermutation)) < best_known_length and attempts < max_attempts:
        attempts += 1
        candidates = generate_candidates("".join(working_superpermutation), missing_permutations, prodigal_manager, winners, losers, n, eput, limbo_list, anti_laminates, constraint_laminates)
        best_candidate = None
        best_score = -float('inf')

        for candidate_hash in candidates:
            score = calculate_score("".join(working_superpermutation), candidate_hash, prodigal_manager, winners, losers, layout_memory, n, missing_permutations, eput, anti_laminates)
            if score > best_score:
                best_score = score
                best_candidate = unhash_permutation(candidate_hash, n)

        if best_candidate:
            overlap = calculate_overlap("".join(working_superpermutation), "".join(map(str, best_candidate)))
            working_superpermutation.extend(list(str(x) for x in best_candidate[overlap:]))
            missing_permutations.discard(hash_permutation(best_candidate))
            #  Basic eput update
            eput[hash_permutation(best_candidate)] = True
        else:
            # If no candidate found. We are returning none.
            return None

    if len("".join(working_superpermutation)) > best_known_length:
        return None #Too long.
    if missing_permutations:
        return None #Couldn't fill it.

    return "".join(working_superpermutation)

def select_n_minus_1_segments(n, prodigal_manager, winners, losers, layout_memory):
    """Selects a set of (n-1)-segments to use as the foundation for the n-superpermutation.

    This function embodies the "n-1 shell" strategy. It selects segments from
    known n-1 superpermutations and prodigals, prioritizing those that are
    likely to be useful for constructing a minimal n-superpermutation.

    Args:
        n (int): The target n value.
        prodigal_manager (ProdigalManager): The ProdigalManager instance.
        winners (dict): Dictionary of winner k-mers and their weights.
        losers (dict): Dictionary of loser k-mers and their weights.
        layout_memory (LayoutMemory): The LayoutMemory instance.

    Returns:
        list: A list of (n-1)-segment strings.
    """
    # 1. Load n-1 Superpermutations:
    n_minus_1_superpermutations = []
    try:
        with open(f"distinct_superpermutations_n{n-1}.txt", "r") as f:
          n_minus_1_superpermutations = [line.strip() for line in f]
    except:
        logging.warning(f"Could not find n={n-1} file, using default method.")
        n_minus_1_superpermutations = [generate_n_minus_1_superpermutation(n-1, INITIAL_SEED)]
        if not n_minus_1_superpermutations[0]:
            logging.critical("Cannot continue without n-1 data.")
            exit()

    # 2. Extract Segments (between imperfect transitions):
    segments = extract_nm1_segments(n_minus_1_superpermutations, n-1)

    # 3. Add "Best" Prodigals (if any are better than current segments)
    # Get best prodigals, filtering by n-1
    best_prodigals = prodigal_manager.get_best_prodigals(n=n-1, task="generation", context={})
    best_prodigals_list = [best_prodigals[p]['sequence'] for p in best_prodigals]
    segments.extend(best_prodigals_list)

    # 4. Score Segments:
    scored_segments = []
    for seg in segments:
      score = calculate_sequence_score(seg, n-1, winners, losers, layout_memory, None, None, level=7) #Use level 7, as that scores based on many factors.
      scored_segments.append((score, seg))
    
    # 5. Select Top Segments:
    # For now, select all.  In the future, we may limit this.
    selected_segments = [seg for score, seg in scored_segments]

    return selected_segments

def connect_segments(n, segments, prodigal_manager, winners, losers, layout_memory, best_known_length, seed, laminates, anti_laminates, constraint_laminates, missing_permutations):
    """Connects the extended n-1 segments using bridge sequences."""
    combined = ""
    for seg in segments:
      if combined == "":
        combined = seg
        continue
      overlap = calculate_overlap(combined, seg)
      if overlap == 0: #Need to use the combiner
          prefix = combined[-(n-1):]
          suffix = seg[:n-1]
          candidates = generate_bridge_candidates("".join(prefix), "".join(suffix), missing_permutations, n, winners, losers, layout_memory, laminates, anti_laminates)
          if candidates:
              # Choose the best candidate based on winners/losers, and other data
              best_candidate = None
              best_score = -float('inf')
              for cand_hash in candidates:
                  cand_perm = unhash_permutation(cand_hash, n)
                  cand_str = "".join(str(x) for x in cand_perm)
                  score = calculate_score(combined, cand_hash, prodigal_manager, winners, losers, layout_memory, n, missing_permutations, {}, anti_laminates)

                  if score > best_score:
                      best_score = score
                      best_candidate = cand_str

              overlap = calculate_overlap(combined, best_candidate)
              combined += best_candidate[overlap:]
          else:
              return None #Skip if we cannot connect.

      else: #Overlap exists
          combined += seg[overlap:]

    # Now, try to complete the combined_sequence to a full superpermutation

    return combined
    #pass

#Placeholder, as this is handled in analysis.
def generate_bridge_candidates(segment1, segment2, missing_permutations, n, winners, losers, layout_memory, laminates, anti_laminates, max_length):
  pass
	
File: construct.py (v6.0 - Design Document)

Purpose: This file contains the main logic for constructing superpermutations. It implements the iterative n-building approach, starting from n=1 and working up to the target n value. The primary construction strategy is the "n_minus_1_shell" approach, which leverages data and structures from n-1 superpermutations.

Key Design Principles:

Constructive Approach: The algorithm primarily builds superpermutations by adding permutations and segments, guided by data and formulas, rather than relying on random generation and filtering.
n-1 Shell: Uses segments from n-1 superpermutations as the foundation for constructing n-superpermutations.
Data-Driven: All decisions (segment selection, insertion points, bridging) are based on accumulated data (winners/losers, layout memory, laminates, anti-laminates, prodigals, De Bruijn graph analysis, formulas).
Deterministic: Minimizes randomness as much as possible, relying on deterministic algorithms and fixed random seeds for reproducibility.
Iterative n-Building: Starts from n=1 and builds up to the target n, carrying over data between levels.
Modularity: The code is organized into well-defined functions with clear responsibilities.
Configurability: The algorithm's behavior is controlled by a configuration dictionary (loaded from config.py).
Think Tank: Used in design.
DTT: Used in design.
Functions:

construct_superpermutation(n, config):

Purpose: The main entry point for constructing a superpermutation of order n.
Input:
n (int): The target number of symbols.
config (dict): A dictionary containing configuration parameters (loaded from config.py).
Output:
str: The constructed superpermutation string (or None if construction fails).
Algorithm:
1.  Initialization:
    - Set random seed (from config).
    - Initialize empty data structures: winners, losers, layout_memory, prodigal_manager, laminates, anti_laminates.
    - best_known_length = infinity

2.  Iterative n-Building:
    - for current_n in range(1, n + 1):
        - Load/Initialize Data (for current_n):
            - If current_n > 1:
                - Load/adapt data (winners, losers, layout, prodigals, laminates, anti-laminates) from current_n-1.  Adapt means:
                  -Winners/Losers: Carry over, but adjust weights based on any formulas, and combine with any of that n value already present.
                  -Layout Memory: Carry over, but adjust for new n value
                  -Prodigals: Carry over, run extend and analyze prodigal
                  -Laminates/Anti-Laminates: Carry over, adjusting for new n value.
                  -best_known_length: Carry over, or use formula to determine.
            - Else (current_n <= 5):  # Base Cases
                - Generate minimal superpermutation directly (using generate_n_minus_1_superpermutation).
                - Analyze the superpermutation and populate the data structures.
                - Skip to the next n value.

        - Load/Create Constraint Laminate (based on current best known length for current_n).

        - Main Construction Loop:
          while True:  # Until a valid superpermutation is found or max iterations reached.
              - Select a strategy (using select_strategy, based on config and laminate analysis).
              - Generate a hypothetical superpermutation (using generate_hypothetical_superpermutation).

              - IF hypothetical generation fails:
                  - Log a warning.
                  - Continue to the next iteration (try a different strategy or seed).

              - Bouncing Batch Test:
                  - Run the bouncing_batch_test (simplified – potentially without multiprocessing initially).  This updates:
                      - Local winners/losers (within each cell).
                      - Local laminates and anti-laminates (within each cell).
                  - Return: is_valid, length, updated_winners, updated_losers, new_anti_prodigals

              - Data Aggregation and Update:
                  - Update global winners/losers (using weighted averaging, incorporating cell-specific data).
                  - Add new anti-prodigals and update anti-laminates.
                  - Merge local laminates (using appropriate merging strategy).
                  - Update the prodigal_manager (add new prodigals, extend existing ones, update scores).

              - Check for Completion and Validity:
                  - If is_valid:
                      - If length < best_known_length:
                          - Update best_known_length and best_known_superpermutation.
                          - Save the new best superpermutation to a file.
                          - Recreate the constraint laminate.
                      - Break out of the inner loop (move to the next n).
                  - Else:
                        - Log a warning (valid but not shorter).

              - Periodic Reconfiguration:
                  - Call reconfigure_superpermutation on the current (potentially incomplete) superpermutation.

3.  Return the best superpermutation found.
select_strategy(n, config, laminates, anti_laminates):

Purpose: Selects a superpermutation generation strategy based on the configuration and the current state (represented by laminates).
Input: n, config, laminates, anti_laminates
Process:
Gets the available strategies and their initial weights from the config dictionary.
Analyzes the laminates (density, connectivity) to adjust the strategy weights (as in previous versions). Denser, more connected laminates favor "prodigal_combination"; sparser laminates favor "random_constrained" or "de_bruijn".
Selects a strategy using random.choices with the adjusted weights.
Output: The name of the selected strategy (string).
generate_hypothetical_superpermutation(n, strategy, ...):

Purpose: Generates a complete (or potentially partial, for iterative construction) hypothetical superpermutation using a specified strategy.
Input: n, strategy (string), and all the usual data structures.
Strategies:
"n_minus_1_shell": (Primary Strategy)
Call select_n_minus_1_segments to choose a set of (n-1)-segments.
Call insert_n_plus_1 on each segment to create n-permutations.
Call connect_segments to join the segments using bridge sequences.
"prodigal_combination": (Secondary)
Select "best" prodigals using prodigal_manager.get_best_prodigals.
Combine prodigals, using best connection method
Call complete_from_partial
"de_bruijn": (Secondary)
Construct a weighted De Bruijn graph.
Find high-weight paths in the graph.
Convert paths to superpermutation strings.
Call complete_from_partial
"mutation": (Secondary)
Start with a (partial or complete) superpermutation.
Apply mutations (swap, insert, delete, reverse).
Use all data to make mutations.
"formula_based": (Secondary)
Use best formulas to determine segments.
Build based on that.
"random_constrained": (Secondary)
Generate random, filtered by all data.
Output: A superpermutation string (or None if generation fails).
select_n_minus_1_segments(n, ...):

Purpose: Selects a set of (n-1)-segments to be used in the "n_minus_1_shell" strategy.
Input: n and all the usual data structures.
Process:
Loads the available (n-1)-superpermutations (from the "workbook" or file).
Extracts segments from these superpermutations using extract_nm1_segments (which identifies segments between imperfect transitions).
Adds high-quality n-1 prodigals from the prodigal_manager to the set of candidate segments.
Scores each segment based on:
Length.
Overlap rate.
Winner/loser density.
Extensibility score (to n).
Number of breakpoints.
Consistency with layout memory and laminates/anti-laminates.
Selects a subset of segments based on these scores, aiming for:
High overall quality.
Diversity (avoid selecting very similar segments).
Coverage of a significant portion of the (n-1)! permutations.
Output: A list of (n-1)-segment strings.
connect_segments(n, segments, ...):

Purpose: Connects a set of (potentially already extended) segments into a complete superpermutation.
Input: n, a list of segments (strings), and all the usual data structures.
Process:
Iteratively connects the segments, using generate_bridge_candidates to find short, efficient "bridge" sequences between them.
Prioritizes direct overlap (if possible).
Uses calculate_bridge_score to evaluate candidate bridge sequences.
Uses the De Bruijn graph to guide the search for bridges.
Enforces laminate and anti-laminate constraints.
Uses a limited backtracking search if direct connection fails.
Calls complete_from_partial if needed.
Output: A complete superpermutation string (or None if connection fails).
generate_candidates(...): (Used for extending segments and building bridges)

Purpose: Generates candidate permutations, heavily constrained by laminates and other data.
Will work at multiple n values.
Input: The current (partial) superpermutation, missing permutations, all usual data structures, and an end parameter ("prefix" or "suffix" or "bridge").
Process: As described in previous updates, but now even more constrained.
calculate_score(...): (Used for evaluating candidates)

Purpose: Calculates a score for a candidate permutation, considering multiple factors.
Input: The current (partial) superpermutation, the candidate permutation, all the usual data structures.
Process: Calculates a weighted sum of factors (overlap, missing permutation bonus, layout score, prodigal bonus, winner/loser bonus, anti-laminate penalty, lookahead bonus, connectivity bonus, discrepancy penalty, symmetry bonus). The weights are defined in the configuration.
Output: A single score (float).
bouncing_batch_test(...):

Performs the bouncing batch test.
No changes.
This detailed design document for construct.py outlines the core logic of ConStruct v6.0.
