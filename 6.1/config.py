# config.py

# This file contains configuration dictionaries for different n values.
# These dictionaries will be loaded by construct.py to control the
# algorithm's behavior.

config_n6 = {
    "n": 6,
    "seed": 42,
    "grid_dimensions": (2, 2, 2, 2, 2, 2),  # 2^6 = 64 cells
    "generation_strategies": {  # Probabilities for different strategies
        "n_minus_1_shell": 0.8,  # Primary strategy
        "prodigal_combination": 0.1,
        "de_bruijn": 0.05,
        "mutation": 0.05,
        "random_constrained": 0.0,  # Not used in construction phase.
    },
    "formula_set": "set_1",  # Which set of formulas to use
    "action_function": "action_a6",  # Use action function A6
    "action_weights": {  # Weights for the action function components
        "overlap": 5.0,
        "missing_bonus": 1000.0,
        "layout_score": 2.0,
        "prodigal_bonus": 500.0,
        "winner_bonus": 2.0,
        "loser_penalty": 2.0,
        "lookahead_bonus": 0.5,
        "anti_laminate_penalty": 5000.0,
        "discrepancy_penalty": 1.0,
        "symmetry_bonus": 1.0,
        "connectivity_bonus": 5.0,
    },
    "mutation_rate": 0.1,  # Probability of applying a mutation
    "mutation_types": {  # Probabilities for different mutation types
        "swap": 0.4,
        "insert": 0.2,
        "delete": 0.2,
        "reverse": 0.1,
        "kmer_swap": 0.1,
    },
    "reconfigure_frequency": 0,  #  Don't reconfigure during n=6 build
    "prodigal_min_length": 10,
    "prodigal_overlap_threshold": 0.98,
    "anti_prodigal_threshold": 2.0,
    "max_bridge_length": 100,  # Maximum length for bridge sequences
    "de_bruijn_k": 5,  # k value for De Bruijn graph
    "megawinner_lengths": [10, 11],  # Lengths for MegaWinners/MegaLosers
    "megawinner_loser_threshold": 2.0, # Threshold multiplier for MegaWinner/MegaLoser identification
    "num_laminates_to_select": 5,  # Number of laminates to select from the album
    "laminate_merge_method": "intersection", # How to merge laminates
    #Data files set to none, because all data will be generated.
    "data_filepaths": {
        "winners_losers": None,
        "layout_memory": None,
        "prodigals": None,
        "laminates": None,
        "anti_laminates": None,
        "best_superpermutation": None,
    },
}

config_n7 = {
    "n": 7,
    "seed": 42,
    "grid_dimensions": (2, 2, 2, 2, 2, 2, 2),  # 2^7 = 128 cells
     "generation_strategies": {  # Probabilities for different strategies
        "n_minus_1_shell": 0.8,
        "prodigal_combination": 0.1,
        "de_bruijn": 0.05,
        "mutation": 0.05,
        "random_constrained": 0.0,
    },
    "formula_set": "set_1", # Which set of formulas to use
    "action_function": "action_a6",
    "action_weights": {
        "overlap": 5.0,
        "missing_bonus": 1000.0,
        "layout_score": 3.0,
        "prodigal_bonus": 750.0,
        "winner_bonus": 2.0,
        "loser_penalty": 2.0,
        "lookahead_bonus": 0.5,
        "anti_laminate_penalty": 5000.0,
        "discrepancy_penalty": 1.0,
        "symmetry_bonus": 1.0,
        "connectivity_bonus": 5.0
    },
    "mutation_rate": 0.1,
    "mutation_types": {
        "swap": 0.4,
        "insert": 0.2,
        "delete": 0.2,
        "reverse": 0.1,
        "kmer_swap": 0.1,
    },
    "reconfigure_frequency": 0,  #  Don't reconfigure during n=7 build
    "prodigal_min_length": 20,
    "prodigal_overlap_threshold": 0.98,
    "anti_prodigal_threshold": 2.0,
    "max_bridge_length": 150,
    "de_bruijn_k": 6,
    "megawinner_lengths": [12, 13, 19, 20],
    "megawinner_loser_threshold": 2.0,
    "num_laminates_to_select": 5,
    "laminate_merge_method": "intersection",
    #Data files set to none, because all data will be generated.
    "data_filepaths": {
        "winners_losers": None,
        "layout_memory": None,
        "prodigals": None,
        "laminates": None,
        "anti_laminates": None,
        "best_superpermutation": None,
    },
}

config_n8 = {
    "n": 8,
    "seed": 42,
    "grid_dimensions": (2, 2, 2, 2, 2, 2, 2, 2),  # 2^8 = 256 cells
    "generation_strategies": { # Probabilities for different strategies
        "n_minus_1_shell": 0.8,  # Increased reliance on n-1 shell
        "prodigal_combination": 0.1, # Reduced direct prodigal combination
        "de_bruijn": 0.05, # Reduced
        "mutation": 0.05, # Increased mutation
        "random_constrained": 0.0, # Only for testing
    },
    "formula_set": "set_1", # Which set of formulas to use
    "action_function": "action_a6", # Still using a hybrid, refined action function
    "action_weights": {  # Tuned weights, higher emphasis on layout, connectivity and lookahead
        "overlap": 5.0,
        "missing_bonus": 1000.0,
        "layout_score": 5.0,
        "prodigal_bonus": 500.0,
        "winner_bonus": 2.0,
        "loser_penalty": 2.0,
        "lookahead_bonus": 2.0,
        "anti_laminate_penalty": 5000.0,
        "discrepancy_penalty": 1.0,  # Tuned weight
        "symmetry_bonus": 1.0,
        "connectivity_bonus": 5.0
    },
    "mutation_rate": 0.2,  # Higher mutation rate for exploration
    "mutation_types": {
        "swap": 0.3,
        "insert": 0.2,
        "delete": 0.2,
        "reverse": 0.15,
        "kmer_swap": 0.15,
    },
    "reconfigure_frequency": 500,  # Reconfigure every 500 permutations added
    "prodigal_min_length": 50,  # Increased prodigal length for n=8
    "prodigal_overlap_threshold": 0.98,  # High overlap threshold
    "anti_prodigal_threshold": 1.5,  # Tuned threshold
    "max_bridge_length": 250, # Maximum length for bridge sequences
    "de_bruijn_k": 7,  # k value for De Bruijn graph
    "megawinner_lengths": [14, 15, 21, 22, 30, 40, 50],  # Lengths for MegaWinners/MegaLosers
    "megawinner_loser_threshold": 2.5, # Increased threshold
    "num_laminates_to_select": 10,
    "laminate_merge_method": "intersection", # Using intersection for merging
    #Data files set to none, because all data will be generated.
    "data_filepaths": {
        "winners_losers": None,
        "layout_memory": None,
        "prodigals": None,
        "laminates": None,
        "anti_laminates": None,
        "best_superpermutation": None,
    },
}