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
        "random_constrained": 0.0, # Not used in construction phase.
    },
    "formula_set": "set_1", # Which set of formulas to use
    "action_function": "action_a6", # Use action function A6
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
    "prodigal_min_length": 10, #This is used for finding prodigals
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
     "generation_strategies": {
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
        "layout_score": 5.0,  # Increased layout weight
        "prodigal_bonus": 500.0,
        "winner_bonus": 2.0,
        "loser_penalty": 2.0,
        "lookahead_bonus": 1.0, # Increased lookahead
        "anti_laminate_penalty": 5000.0,
        "discrepancy_penalty": 0.2, # Tuned
        "symmetry_bonus": 1.0,
        "connectivity_bonus": 5.0
    },
    "mutation_rate": 0.2,  # Increased mutation rate
    "mutation_types": {
        "swap": 0.3,
        "insert": 0.2,
        "delete": 0.2,
        "reverse": 0.15,
        "kmer_swap": 0.15,
    },
    "reconfigure_frequency": 500,  # Call reconfigure every 500 permutations added
    "prodigal_min_length": 50,
    "prodigal_overlap_threshold": 0.98,
    "anti_prodigal_threshold": 1.5, # Tuned
    "max_bridge_length": 250,  # Maximum length for bridge sequences
    "de_bruijn_k": 7,  # k value for De Bruijn graph
    "megawinner_lengths": [14, 15, 21, 22, 30, 40, 50],  # Lengths for MegaWinners/MegaLosers
    "megawinner_loser_threshold": 2.5, # Tuned
    "num_laminates_to_select": 10,  # Select top 10 laminates
    "laminate_merge_method": "intersection", # Merge method for laminates.
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


# You can add more configurations for other n values as needed.

Explanation:

n-Specific Dictionaries: The file contains separate configuration dictionaries for n=6, n=7, and n=8 (config_n6, config_n7, config_n8).  This allows us to tailor the parameters and strategies for each n value.

Key Parameters:  Each dictionary includes settings for:

n: The number of symbols.
seed: The random seed.
grid_dimensions: The dimensions of the Bouncing Batch grid.
generation_strategies: The probabilities for different generation strategies within generate_hypothetical_superpermutation.
formula_set: Which set of formulas to use (from formulas.py – this allows for easy switching between different formula variations).
action_function: Which action function to use (from formulas.py).
action_weights: The weights for the different components of the action function (used in calculate_score).
mutation_rate: The probability of applying a mutation in the "mutation" strategy.
mutation_types: The probabilities for different types of mutations.
reconfigure_frequency: How often to call the reconfigure_superpermutation function during construction.
prodigal_min_length, prodigal_overlap_threshold: Parameters for prodigal identification.
anti_prodigal_threshold: Parameter for anti-prodigal identification.
max_bridge_length: The maximum length of bridge sequences.
de_bruijn_k: The k value for De Bruijn graph construction.
megawinner_lengths: The lengths to consider for MegaWinners/MegaLosers.
megawinner_loser_threshold: The threshold for identifying MegaWinners/MegaLosers.
num_laminates_to_select: How many laminates to select from the album.
laminate_merge_method: How to merge laminates ("intersection," "union," "weighted_average").
data_filepaths: Initially set to None. This enforces the "clean slate" approach. The program will create new data files.
Flexibility: This configuration-driven approach makes it very easy to experiment with different settings and strategies without modifying the core code.  You can simply create a new configuration dictionary or modify an existing one.

Reproducibility:  By storing the configuration in a separate file, we ensure that each run is fully reproducible (given the same seed).

Integration with construct.py:

The construct_superpermutation function will now take the config dictionary as an argument and use it to access all the necessary parameters.  Example:

Python

# Inside construct_superpermutation
config = config_n8 #Example
n = config['n']
seed = config['seed']
# ...

# Accessing parameters:
overlap_weight = config["action_weights"]["overlap"]
prodigal_min_length = config["prodigal_min_length"]

# Selecting a generation strategy:
strategy = random.choices(list(config["generation_strategies"].keys()), weights=list(config["generation_strategies"].values()))[0]
This config.py file is a crucial part of the v6.0 design. It centralizes all the parameters and settings, making the algorithm much more flexible and easier to experiment with.  It also enforces the "clean slate" approach by ensuring that no data from previous runs is accidentally used.