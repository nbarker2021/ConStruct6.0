## 7.  Code Structure

The program is organized into the following Python files:

### 7.  1.  `construct.py`

This file contains the main logic for constructing superpermutations.

*   **`construct_superpermutation(n, config)`:**
    *   This is the main function that orchestrates the entire process. It takes the target `n` value and a configuration dictionary as input. It initializes data structures, iteratively builds up superpermutations (starting from n=1), and returns the best superpermutation found.
*   **`generate_hypothetical_superpermutation(n, strategy, ...)`:**
    *   Generates hypothetical superpermutations based on various strategies, now focusing primarily on the "n_minus_1_shell" strategy, but maintaining options for prodigal combination, De Bruijn graph guided, and a basic mutation.
* **Helper Functions:** Implements helper functions to support the n-1_shell, including selection, insertion, and connection.

### 8.  2.  `analysis.py`

This file provides functions for analyzing superpermutations and related data.

*   **`calculate_winners_losers(superpermutations, n, k=None)`:** Calculates winner/loser k-mer weights from a list of superpermutations.
*   **`identify_prodigals(superpermutation, n, ...)`:** Identifies prodigal results within a given sequence.
*   **`extend_prodigal(sequence, n, ...)`:** Extends a given sequence (presumably a prodigal) as far as possible while maintaining high overlap and other desirable properties.
*   **`analyze_prodigal(prodigal, n, ...)`:** Analyzes a prodigal sequence, identifying potential breakpoints and calculating various metrics.
*   **`identify_anti_prodigals(...)`:** Identifies sequences with low overlap, high loser density, and other undesirable properties.
*   **`identify_mega_winners(...)`:** Identifies longer sequences (MegaWinners) with consistently high winner density.
*   **`identify_mega_losers(...)`:** Identifies longer sequences (MegaLosers) with consistently low winner density.
*   **`calculate_sequence_score(...)`:** Calculates a comprehensive score for a (partial or complete) superpermutation, considering overlap, winner/loser density, layout consistency, laminate compliance, discrepancy, and other factors.
*   **`calculate_bloat(...)`:** Calculates a "bloat" metric for a superpermutation.
*   **`count_imperfect_transitions(...)`:** Counts the number of imperfect transitions (non-maximal overlaps) in a superpermutation.
*   **`analyze_imperfect_transition_distribution(...)`:** Analyzes the distribution and spacing of imperfect transitions.
*   **`analyze_breakpoint(...)`:** Performs a detailed analysis of a specific imperfect transition (breakpoint), examining its context.
*    **`insert_n_plus_1(...)`:** Inserts additional values to extend from n-1 to n.
*   **`calculate_permutation_coverage(...)`:** Calculates the percentage of permutations covered by a sequence.
    *   **`calculate_connectivity_score(...)`:** Calculates a connectivity score for a sequence.
    *   **`extract_n7_segments(...)`:** (generalized to `extract_nm1_segments(...)`): Extracts segments between imperfect transitions.
    *   **`analyze_n_minus_1_segment(...)`:** Analyzes an (n-1)-segment in the context of *n*.
    * `calculate_bridge_impact(...)`:  Evaluates the impact of a bridge sequence.
    *  `analyze_sequence_hierarchy(...)`: Performs a hierarchical analysis of a sequence.
    * `calculate_packing_fraction(...)`: Calculates a "packing fraction" for a superpermutation.
    *   `analyze_unit_cell(...)`: Analyzes the structure of repeating units (currently a placeholder).
    * `calculate_symmetry_score(...)`: Calculates a symmetry score for a superpermutation.
    *   `compare_kmer_frequencies(...)`:  Compares k-mer frequencies between datasets.
    *   `compare_prodigal_usage(...)`: Compares prodigal usage across different *n*.
    *    `calculate_cell_winners_losers(...)`: Calculates winners and losers based on a superpermutation and a cell's permutations.
    * `generate_completion_candidates_n8(...)`:  Generates candidate permutations specifically for n=8 completion.
    *  `calculate_completion_score_n8(...)`: Calculates the score for a candidate permutation during n=8 completion.
    *   `generate_permutations_on_demand(...)`:  Generates permutations on demand, with filtering.
    *   `generate_completion_candidates(...)`: Generates completion candidates.
    * `calculate_average_overlap_imperfect_transitions`: Calculates specifically the average overlap of imperfect transitions.

### 8.  3.  `utils.py`

This file provides utility functions used throughout the project.

*   `setup_logging()`: Sets up logging.
*   `compute_checksum()`: Computes SHA-256 checksums.
*   `generate_permutations(n)`: Generates all permutations of *n* symbols.
*   `is_valid_permutation(perm, n)`: Checks if a permutation is valid.
*   `calculate_overlap(s1, s2)`: Calculates the overlap between two strings.
*   `normalize_sequence(seq)`: Normalizes a superpermutation string.
*   `kmer_to_int(kmer)`: Converts a k-mer tuple to an integer.
*   `int_to_kmer(int_kmer, k)`: Converts an integer to a k-mer tuple.
*   `hash_permutation(perm)`: Hashes a permutation to an integer.
*   `unhash_permutation(perm_hash, n)`: Converts a permutation hash back to a tuple.
* `generate_n_minus_1_superpermutation(n, seed)`

### 8.  4.  `graph.py`

This file provides functions for working with De Bruijn graphs.

*   `build_de_bruijn_graph(...)`: Builds a De Bruijn graph from a set of k-mers.
*   `add_weights_to_debruijn(...)`: Adds winner/loser weights to the edges of a De Bruijn graph.
*   `find_high_weight_paths(...)`: Finds high-weight paths in a De Bruijn graph.
*   `analyze_debruijn_graph(...)`: Calculates various De Bruijn graph properties (connectivity, imbalance, cycle structure, etc.).

### 5.5. `laminate.py`

This file provides functions for creating, manipulating, and validating laminates and anti-laminates.

*   `create_laminate(...)`: Creates a laminate from a sequence.
*   `create_anti_laminate(...)`: Creates an anti-laminate from a set of anti-prodigals.
*   `is_compatible(...)`: Checks if a permutation is compatible with a laminate/anti-laminate.
*   `validate_laminate(...)`: Validates a laminate (structural and contextual checks).
*   `merge_laminates(...)`: Merges multiple laminates.
*  `update_laminate(...)` Updates a dynamic laminate.
*   `analyze_laminate_density(...)`: Calculates laminate density.
*   `analyze_laminate_connectivity(...)`: Calculates laminate connectivity.
*   `get_allowed_transitions(...)`:  Gets allowed transitions from a laminate.
*   `add_laminate_to_album(...)`, `select_laminates(...)`, `remove_laminate_from_album(...)`, `list_laminates(...)`: Functions for managing the "laminate album."
*   `create_n7_constraint_laminate(...)` (generalized to `create_constraint_laminate`).

### 5.6. `prodigal.py`

This file contains the `ProdigalManager` class for managing prodigal data.

*   `ProdigalManager` class: Methods for adding, retrieving, ranking, and extending prodigals.

### 5.7. `formulas.py`

This file stores all the formula variations considered during the project, categorized by their purpose (SP(n), C(n), I(n), segment length, action).

### 5.8. `evaluator.py`
This file contains all functions for testing and validating formulas.

### 5.9 `data_manager.py`
This file handles all loading, saving, and general organization of functions.

### 5.10 `config.py`
Contains all configuration information.