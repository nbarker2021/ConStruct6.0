construct.py - Design (v6.0)

File Purpose:  This file contains the main function, construct_superpermutation, and its supporting functions, for constructing superpermutations. It orchestrates the entire process, from initialization to final output.

Key Functions:

construct_superpermutation(n, config):

Purpose: The main entry point for superpermutation construction.
Input:
n: The target n value (integer).
config: A dictionary containing configuration parameters (loaded from config.py). This includes:
Strategy choices (e.g., weights for different generation strategies).
File paths (for saving/loading data).
Parameters for the Bouncing Batch (grid dimensions, etc.).
Formula choices (which formulas to use for SP(n), I(n), segment length).
Thresholds and weights (for scoring, prodigal selection, etc.).
Random seed.
Process:
Initialization:
Sets the random seed for reproducibility.
Initializes empty data structures: winners, losers, layout_memory, prodigal_manager, laminates, anti_laminates.
Iterative n-Building: Implements the core "bottom-up" construction:
Python

for current_n in range(1, n + 1):
    # --- Data Loading/Initialization (for current_n) ---
    # ... (Load/initialize data structures, potentially using data from current_n-1) ...

    if current_n <= 5:
        # --- Base Cases (n <= 5) ---
        superpermutation = generate_n_minus_1_superpermutation(current_n, seed) # Use existing function
        # ... (Analyze superpermutation, update data structures) ...
    else:
        # --- Main Construction Loop (n >= 6) ---
        while True: # Continue until a valid superpermutation is found or max iterations reached
            # 1. Generate Hypothetical Superpermutation
            hypothetical_sp = generate_hypothetical_superpermutation(current_n, config, ...)

            # 2. Bouncing Batch Test
            is_valid, length, winners, losers, layout_memory = bouncing_batch_test(hypothetical_sp, ...)

            # 3. Data Update
            #  - Update winners/losers, layout memory, prodigals, anti-prodigals, laminates, anti-laminates
            #  - Analyze and find new MegaWinners/MegaLosers

            # 4. Check for Completion and Validity

            # 5. Reconfiguration (periodically)

            if is_valid and length <= best_known_length: #Or other stopping condition
                break
    #Save all data.
    #Prepare all data for next n value.
Output: Returns the (hopefully minimal) superpermutation string for the target n.
Key Features:
Iterative n-Building: The core logic is the loop that iterates from n=1 up to the target n, building up the superpermutation and all associated data step-by-step.
Configuration-Driven: The behavior of the algorithm is highly configurable through the config dictionary. This allows for easy experimentation with different strategies and parameters.
Data Persistence (Simulated): The necessary information for continuing will be updated.
Integration: Calls functions from other modules (analysis.py, graph.py, laminate.py, prodigal.py, formulas.py) to perform specific tasks.
generate_hypothetical_superpermutation(n, strategy, ...):

Purpose: Generates a complete (or potentially partial, for iterative construction) hypothetical superpermutation using a specified strategy. This function is now primarily a dispatcher to other, strategy-specific functions.
Input: n, strategy (a string indicating the strategy to use), and all the usual data structures.
Strategies:
"n_minus_1_shell": (Primary Strategy)
Calls select_n_minus_1_segments to choose a set of (n-1)-segments.
Calls insert_n_plus_1 to create n-permutations from these segments.
Calls connect_segments to connect the segments, using bridge sequences.
"prodigal_combination": (Secondary) Combines existing n-prodigals.
"de_bruijn": (Secondary) Uses the De Bruijn graph to generate sequences.
"mutation": (Secondary) Mutates an existing (partial or complete) superpermutation.
"formula_based": (Secondary) Constructs a superpermutation based on segment length formulas.
Output: A superpermutation string (or None if generation fails).
Key Change: This function no longer handles the entire construction process. It focuses on generating candidates based on different strategies, which are then tested and refined within the main loop of construct_superpermutation.
Helper Functions (for "n_minus_1_shell"):

select_n_minus_1_segments(n, ...): Selects a set of (n-1)-segments to use as the foundation for the n-superpermutation. This function will use:
Prodigal data (from prodigal_manager).
Extensibility scores (to prioritize segments that are likely to be useful for n).
Winner/loser data.
Breakpoint analysis (to avoid weak segments).
Potentially, De Bruijn graph analysis.
A formula driven approach.
insert_n_plus_1(segment, n, ...): (Already implemented in analysis_scripts_final.py, but will be called here) Inserts the nth symbol into an (n-1)-sequence to create n-permutations. This is a highly constrained and data-driven process.
generate_bridge_candidates(segment1, segment2, ...): (Already implemented) Generates candidate "bridge" sequences to connect two segments. This heavily uses the De Bruijn graph and all available constraints.
connect_segments(segments, ...): This function takes a list of segments (already "extended" with the nth symbol) and attempts to connect them into a complete superpermutation. This will primarily use generate_bridge_candidates and calculate_bridge_score.
Other:

The file will use all other data structures, functions, and classes.

Data Flow (Simplified):

construct_superpermutation is called with a target n and a configuration.
Data for n-1 is loaded/created.
generate_hypothetical_superpermutation is called, using the "n_minus_1_shell" strategy (primarily).
select_n_minus_1_segments chooses appropriate segments.
insert_n_plus_1 extends these segments to n.
connect_segments (using generate_bridge_candidates) connects the segments.
The Bouncing Batch test is performed (using multiprocessing).
Data (winners/losers, prodigals, etc.) is updated.
Steps 3-5 are repeated until a valid superpermutation is found (or a stopping criterion is met).
The process is repeated for subsequent n values.

# construct.py
import random
import logging
import json
import multiprocessing
import time
import math
from utils import setup_logging, normalize_sequence, compute_checksum, generate_permutations, is_valid_permutation, calculate_overlap, hash_permutation, unhash_permutation
from layout_memory import LayoutMemory
from analysis_scripts_final import is_prodigal, generate_hypothetical_prodigals, calculate_winners_losers, identify_anti_prodigals,  identify_mega_winners, identify_mega_losers, calculate_segment_efficiency, approximate_derivative, calculate_discrepancy, analyze_breakpoint, count_imperfect_transitions, analyze_imperfect_transition_distribution, insert_n_plus_1, extract_nm1_segments, analyze_n_minus_1_segment, calculate_bridge_impact, calculate_sequence_score, calculate_permutation_coverage, calculate_connectivity_score
from laminate_utils import create_laminate, is_compatible, create_anti_laminate, analyze_laminate_density, analyze_laminate_connectivity, update_laminate, merge_laminates, create_n7_constraint_laminate
from sequence_generation import generate_n_minus_1_superpermutation
from graph_utils import build_de_bruijn_graph, find_high_weight_paths, add_weights_to_debruijn, analyze_debruijn_graph
from prodigal_manager import ProdigalManager
import formulas


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
    setup_logging()
    random.seed(config["seed"])

    # Initialize data structures (empty, or loaded from previous n if available)
    winners = {}
    losers = {}
    layout_memory = LayoutMemory()
    prodigal_manager = ProdigalManager(n)
    laminates = {}  # { (n, k): [list of laminates] }
    anti_laminates = {}
    best_known_length = float('inf')

    for current_n in range(1, n + 1):
        logging.info(f"Constructing superpermutation for n = {current_n}")

        # --- Load/Initialize Data (for current_n) ---
        #   - Load existing data (if available) from files specified in config.
        #   - If starting from scratch, initialize empty data structures.
        #   - If n > 1, use data from n-1 to initialize:
        #       -  n-1 superpermutations as seeds and for prodigal extraction
        #       -  Winners/Losers (transfer and adapt)
        #       -  Layout memory (transfer and adapt)
        #       -  Laminates and Anti-Laminates (transfer, adapt, and create constraint laminate)
        # ... (Implementation for loading/initialization) ...

        if current_n <= 5:
            # --- Base Cases (n <= 5) ---  Use direct generation
            superpermutation = generate_n_minus_1_superpermutation(current_n, config["seed"]) # Use existing function
            if superpermutation:
                logging.info(f"Generated minimal superpermutation for n={current_n} (length: {len(superpermutation)})")
                # ... (Analyze superpermutation, update data structures) ...
                # No need for Bouncing Batch or complex strategies here.

                #Save all data using data_manager.py functions
            else:
                logging.error(f"Failed to generate superpermutation for n={current_n}")
                return None # Exit if we can't even generate the base cases

        else:
            # --- Main Construction Loop (n >= 6) ---

            # Load any existing "best" superpermutation, and create constraint laminate
            constraint_laminates = []
            best_known_superpermutation = "" #Placeholder
            # ... (Load best_known_superpermutation from file, if it exists)
            # if best_known_superpermutation:
            #     best_known_length = len(best_known_superpermutation)
            #     constraint_laminates.append(create_constraint_laminate(best_known_superpermutation, current_n, current_n - 1))
            #     constraint_laminates.append(create_constraint_laminate(best_known_superpermutation, current_n, current_n - 2))

            while True:  # Continue until a valid superpermutation is found or max iterations reached
                # 1. Select a Strategy (dynamically, based on config and current state)
                #    - For v6.0, the primary strategy will be "n_minus_1_shell"
                #    - Other strategies ("prodigal_combination", "de_bruijn", "mutation") can be used,
                #      but with lower probability.
                strategy = select_strategy(config, laminates, anti_laminates)  # Placeholder for strategy selection logic

                # 2. Generate Hypothetical Superpermutation
                hypothetical_sp = generate_hypothetical_superpermutation(current_n, strategy, prodigal_manager,
                                                                        winners, losers, layout_memory,
                                                                        best_known_length, config["seed"],
                                                                        laminates, anti_laminates,
                                                                        constraint_laminates)

                if not hypothetical_sp:
                    logging.warning(f"Hypothetical generation failed (strategy: {strategy}).")
                    continue  # Try again with a different strategy/seed

                # 3. Bouncing Batch Test
                is_valid, length, new_winners, new_losers, _ = bouncing_batch_test(
                    hypothetical_sp, current_n, config["grid_dimensions"], prodigal_manager,
                    config["layout_memory_filename"], anti_laminates, constraint_laminates, winners, losers
                )

                # 4. Data Update and Analysis
                # ... (Update winners/losers, layout memory, prodigal_manager, anti_laminates) ...
                # ... (Identify new prodigals and anti-prodigals) ...
                # ... (Analyze imperfect transitions, update formulas, etc.) ...

                # 5. Check for Completion and Validity
                if is_valid:
                    if length < best_known_length:
                        best_known_length = length
                        logging.info(f"New best superpermutation found for n={current_n}! Length: {length}")
                        # ... (Save the new best superpermutation) ...
                        #Create new contraint laminate
                        constraint_laminates = []
                        with open(f"best_superpermutation_n{n}.txt", "r") as f:
                            best_n = f.read().strip()
                            constraint_laminates.append(create_constraint_laminate(best_n, n, n-1)) # Create
                            constraint_laminates.append(create_constraint_laminate(best_n, n, n-2))
                    # Even if it's not shorter, we might still want to keep it (for diversity)
                    # ... (Logic for saving/analyzing valid superpermutations) ...

                    break # Exit inner loop, move to n+1
                else:
                    logging.info(f"Generated superpermutation is not valid (length: {length}).")
                    continue
                    #Check if we should run reconfiguration
                    #Run analysis

        # --- Prepare Data for Next n ---
        # ... (Extract relevant data from current_n to use as a starting point for current_n + 1) ...

    return best_known_superpermutation # Return best.


def select_strategy(config, laminates, anti_laminates):
    """Selects a superpermutation generation strategy based on the configuration and current state.
       Dynamic Strategy Selection (based on laminate analysis - and possibly other factors)
    """
    available_strategies = ["n_minus_1_shell", "prodigal_combination", "de_bruijn", "mutation"]
    #Placeholder: For now, mostly use n_minus_1_shell
    strategy_weights = [0.7, 0.1, 0.1, 0.1]
    strategy = random.choices(available_strategies, weights=strategy_weights)[0]
    return strategy

def generate_hypothetical_superpermutation(n, strategy, prodigal_manager, winners, losers, layout_memory, best_known_length, seed, laminates, anti_laminates, constraint_laminates):
    """Generates a complete hypothetical superpermutation using a specified strategy."""

    random.seed(seed)

    if strategy == "n_minus_1_shell":
        # 1. Select n-1 Segments
        segments = select_n_minus_1_segments(n, prodigal_manager, winners, losers, layout_memory)
        # 2. Insert nth Symbol
        extended_segments = [insert_n_plus_1(seg, n, winners, losers, layout_memory, laminates, anti_laminates) for seg in segments]
        # 3. Connect Segments
        superpermutation = connect_segments(n, extended_segments, prodigal_manager, winners, losers, layout_memory, best_known_length, seed, laminates, anti_laminates, constraint_laminates) # TODO: Implement this
        return superpermutation

    elif strategy == "prodigal_combination":
        # ... (Implementation - as in previous versions, but refined) ...
        pass
    elif strategy == "de_bruijn":
        # ... (Implementation - as in previous versions, but refined) ...
        pass
    elif strategy == "mutation":
        # ... (Implementation - as in previous versions, but refined) ...
        pass
    elif strategy == "random_constrained":
        # ... (Implementation - as in previous versions, but refined) ...
        pass
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

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
    #For now, select all.  In the future, we may limit this.
    selected_segments = [seg for score, seg in scored_segments]
    #We can sort, and only use a subset if needed.

    return selected_segments

def connect_segments(n, segments, prodigal_manager, winners, losers, layout_memory, best_known_length, seed, laminates, anti_laminates, constraint_laminates):
    """Connects the extended n-1 segments using bridge sequences.
       This is where we would call functions to generate and score.
    """
    # Placeholder implementation:  Just concatenate the segments for now.
    # In a real implementation, this would involve:
    # 1. Identifying missing permutations between segments.
    # 2. Generating candidate bridge sequences using generate_bridge_candidates.
    # 3. Scoring bridge sequences using calculate_bridge_score.
    # 4. Selecting and inserting the best bridge sequence.
    # 5. Potentially using backtracking or local optimization.
    combined = "".join(segments)
    # Attempt to complete:
    all_permutations = generate_permutations(n)
    missing_permutations = set(hash_permutation(p) for p in all_permutations if not "".join(map(str,p)) in combined)
    eput = {hash_permutation(p):True for p in all_permutations if "".join(map(str,p)) in combined}
    return complete_from_partial(combined, n, missing_permutations, prodigal_manager, winners, losers, layout_memory, set(), eput, best_known_length, anti_laminates, constraint_laminates)
    #pass

# The existing functions (generate_candidates, calculate_score, complete_from_partial, etc.)
# will be used *within* these new functions.

# The key is to adapt them to the specific context of n-1 segment extension and bridging.

Explanation of Changes and Key Functions:

construct_superpermutation(n, config): This is the main entry point. It now implements the iterative n-building process, starting from n=1 and going up to the target n. It handles data loading/initialization, strategy selection, and the main construction loop.
generate_hypothetical_superpermutation(...): This function now primarily implements the "n_minus_1_shell" strategy. It calls:
select_n_minus_1_segments(...): To choose the (n-1)-segments.
insert_n_plus_1(...): To insert the nth symbol.
connect_segments(...): To join the extended segments.
select_n_minus_1_segments(...): This new function selects the (n-1)-segments to use as the "shell." It prioritizes segments based on their "extensibility" to n and their overall quality (winner/loser density, etc.).
insert_n_plus_1(...): This crucial function (moved to analysis_scripts_final.py) takes an (n-1)-segment and inserts the nth symbol in all valid positions, creating n-permutations. It uses all available data (winners/losers, layout memory, laminates, anti-laminates) to filter and prioritize the insertions.
connect_segments(...): This function takes multiple segments and finds the best way to combine them.
This design emphasizes a constructive, data-driven, and hierarchical approach to superpermutation generation, leveraging the strengths of the previous versions while addressing their limitations. The next message will have more files.