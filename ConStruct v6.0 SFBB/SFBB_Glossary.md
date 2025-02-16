## Glossary of Terms

This glossary defines the key terms and concepts used in the Superpermutation Finder and Builder project (ConStruct v6.0).

**General Terms:**

*   **Superpermutation:** A string that contains all permutations of a given set of symbols as substrings.
*   **n:** The number of symbols used to construct the superpermutation.  For example, n=7 means the superpermutation will contain all permutations of the symbols {1, 2, 3, 4, 5, 6, 7}.
*   **k-mer:** A substring of length *k*. In this project, k-mers are typically derived from permutations or superpermutations.
*   **Overlap:** The maximum number of characters that can overlap between two consecutive strings (typically permutations or k-mers).
*   **Permutation:** An ordered arrangement of symbols.  Represented in the code as a tuple of integers (e.g., `(1, 2, 3, 4, 5, 6, 7)`).
*   **Permutation Hash:** A unique integer representation of a permutation, used for efficient storage and lookup.
*   **Theoretical Lower Bound:** The theoretical minimum length of a superpermutation for a given *n*: `n! + (n-1)! + ... + 1!`. This bound is only achievable for n <= 5.
*   **Imperfect Transition:** A transition between two consecutive permutations in a superpermutation where the overlap is *less than* the maximum possible overlap (n-1).
*   **I(n):** A function that predicts (or represents) the *number* of imperfect transitions in a minimal superpermutation of order *n*. This is a key quantity being investigated.
*   **C(n):** The "correction term" – the difference between the simple additive formula for superpermutation length (`n! + SP(n-1)`) and the actual minimal length.  `C(n)` is closely related to `I(n)`.
*   **SP(n):** The minimal superpermutation length for a given *n*.
*   **Action Function:** A function that quantifies the "inefficiency" or "cost" of a superpermutation (or a partial superpermutation).  The algorithm aims to *minimize* this action.
*   **Extensibility:**  A measure of how easily a given sequence (permutation, k-mer, prodigal, etc.) can be extended to higher *n* values while maintaining efficiency.
* **Breakpoint:** A position within a sequence (usually a prodigal) where an imperfect transition occurs or is likely to occur.
*   **Normalization:** The process of rotating a superpermutation string to start with the smallest digit, to allow for comparison of distinct solutions.
*   **Checksum:** A cryptographic hash (SHA-256) of the normalized superpermutation string, used to verify its integrity and uniqueness.
* **Bloat:** A measure of how much longer, or how many more permutations are present, that deviate from the theoretical best.

**Algorithm-Specific Terms:**

*   **Prodigal Result (Prodigal):** A subsequence within a superpermutation that exhibits a high overlap rate. Prodigals are considered "efficient" building blocks.
*   **MegaWinner:** A *longer* sequence (typically longer than a k-mer, but potentially shorter than a prodigal) that is consistently associated with high efficiency (high overlap, high winner density) in superpermutation construction.
*   **MegaLoser:** A *longer* sequence that is consistently associated with low efficiency.
*   **Winners/Losers (WL_PUT):** A system for tracking the frequency of k-mers (and potentially longer sequences) in "good" (shorter) and "bad" (longer) superpermutations.  Winners have positive weights, losers have negative weights. Stored as a dictionary with keys `(n, kmer_string)`.
*   **Limbo List:** A set of k-mers or permutations that are to be avoided during candidate generation.
*   **Layout Memory:** A data structure that stores information about the relative positions of k-mer pairs in known good superpermutations.  Used to guide the placement of permutations and to favor common transitions.
*   **Laminate:** A directed graph representing *allowed* transitions between k-mers (positive constraints).  Derived from known good sequences (minimal superpermutations, prodigals, MegaWinners).
*   **Anti-Laminate:** A directed graph representing *disallowed* transitions between k-mers (negative constraints).  Derived from anti-prodigals and other inefficient sequences.
*   **Constraint Laminate:** A laminate created from the *current best known* superpermutation, enforcing a length constraint.
*   **Bouncing Batch:** The core methodology of dividing the permutation space into cells (in a multi-dimensional grid) and iteratively testing candidate superpermutations against each cell, with information exchange ("bouncing") between neighboring cells.
*   **n-1 Shell:** The primary construction strategy for v6.0, where n-superpermutations are built by selecting segments from (n-1)-superpermutations, inserting the *n*th symbol, and connecting the resulting segments.
* **Dynamic Strategy Selection:** Choosing different construction methods based on the current status.
*  **Hypothetical Superpermutation:** Refers to any superpermutation built, even if not complete.
* **ePUT (Enhanced Permutation Universe Tracker):** *Deprecated in v6.0*.  Was used in earlier versions to track all encountered permutations.

**Conceptual Tools:**

*   **Think Tank:** A simulated multi-perspective analysis technique, used for brainstorming, problem-solving, and decision-making.
*   **Assembly Line:** A development methodology that emphasizes breaking down tasks into small, independent units and working on them concurrently.
*   **MORSR (Middle-Out, Ripple, Sub-Ripple):** A hierarchical dependency analysis technique.
*   **Wave Pool:** A metaphor for dynamic knowledge management, where new information is treated as "waves" that update the existing knowledge base.
*   **Snapshots, Movies, Songs:** Techniques for capturing and visualizing the state and evolution of the project.
*   **Whirlpool:**  A focused, intensive analysis technique for deeply understanding a specific concept or problem.
*   **DTT (Deploy to Test):**  The iterative development methodology, involving rapid prototyping, testing, and refinement.

**Code-Specific Terms:**

*   **`construct.py`:** The main Python file containing the core superpermutation construction logic.
*   **`config.py`:**  A file for storing *n*-specific configuration parameters.
*   **`utils.py`:** A file containing utility functions.
*   **`analysis.py`:** A file containing functions for analyzing superpermutations and data.
*   **`graph.py`:**  A file containing functions for working with De Bruijn graphs.
*   **`laminate.py`:** A file containing functions for creating, manipulating, and validating laminates and anti-laminates.
*   **`prodigal.py`:** A file containing the `ProdigalManager` class.
* **`formulas.py`:** Contains all formulas.
*  **`data_manager.py`:**  Handles all data loading and saving, and simulated "workbook" functionality.
* **`evaluator.py`:**  Contains functions for evaluating formulas.
* **`n6_searcher.py`:** Removed.
* **`multiprocessing_example.py`:** Removed.
*  **`sequence_generation.py`:** Removed, functions integrated.
* **`reconfigurator.py`:** Integrated.
*  **`completion_algorithm_n8.py`:** Integrated.
* **`test_utils.py`:** Removed

This glossary provides a comprehensive reference for all the key terms used in the Superpermutation Solver project. I will continue to update and refine this glossary as the project evolves. Next, I will add the requested simulation data.