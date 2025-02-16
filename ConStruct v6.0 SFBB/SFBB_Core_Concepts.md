## 3. Core Concepts and Data Structures

This section defines the key concepts and data structures used in the ConStruct algorithm. Understanding these is essential for comprehending the code and the overall methodology.

### 3.1. Imperfect Transitions

An *imperfect transition* is a transition between two consecutive permutations in a superpermutation where the overlap is *less than* the maximum possible overlap (n-1).  For example, in an n=7 superpermutation, a transition with an overlap of 5 or less is considered imperfect.

*   **Significance:** Imperfect transitions are *unavoidable* for n >= 6.  They are the primary reason why the theoretical lower bound (`n! + (n-1)! + ... + 1!`) is not achievable for larger *n* values.  The *number*, *positions*, and *contexts* of imperfect transitions are crucial for understanding superpermutation structure and for optimizing the construction process.
*   **`I(n)`:**  The *predicted* number of imperfect transitions in a minimal superpermutation for a given *n*.  This is a key quantity that we're trying to model with a formula.
*   **`C(n)`:** The "correction term," which represents the difference between the simple additive formula for superpermutation length (`n! + SP(n-1)`) and the actual minimal length.  `C(n)` is closely related to `I(n)`.

### 3.2. Prodigal Results

A *Prodigal Result* (or simply "prodigal") is a subsequence within a superpermutation (or a candidate superpermutation) that exhibits a *high overlap rate*.  Prodigals represent "efficient" regions of the superpermutation, where permutations are combined with near-maximal overlap.

*   **Identification:** Prodigals are identified by the `find_prodigal_results` function (in `analysis.py`), which uses a minimum length threshold and an overlap threshold.
*   **Extension:**  Prodigals are *maximally extended* using the `extend_prodigal` function. This means that the algorithm tries to add permutations to both ends of the prodigal while maintaining its high overlap rate and respecting all constraints (laminates, anti-laminates, etc.).
*   **Usage:** Prodigals are used as *building blocks* for constructing superpermutations.  The "prodigal_combination" strategy in `generate_hypothetical_superpermutation` focuses on combining and extending prodigals.
*   **`ProdigalManager`:** The `ProdigalManager` class (in `prodigal.py`) handles the storage, retrieval, ranking, and updating of prodigals.
*   **Data Stored:**  For each prodigal, the following information is stored:
    *   `sequence`: The prodigal sequence (string of digits).
    *   `length`: The length of the sequence.
    *   `overlap_rate`: The calculated overlap rate.
    *   `n_value`: The *n* value for which the prodigal was identified.
    *   `source`:  Information about how the prodigal was discovered (e.g., "n=7 minimal," "n=8 run 123," "MegaHypothetical").
    *   `breakpoints`: A list of potential "breakpoints" (imperfect transitions) within the prodigal.
    *   `winner_score`:  A score based on the winner density of the prodigal's k-mers.
    *   `loser_score`:  A score based on the loser density of the prodigal's k-mers.
    *   `extensibility_score`:  A score representing the potential for extending the prodigal to higher *n* values.
    *   `parent_prodigals`:  A list of IDs of prodigals that were used to *create* this prodigal (if applicable).
    *   `child_prodigals`:  A list of IDs of prodigals that were *derived from* this prodigal (e.g., by extension).
    * `used_count`: How many times it has been used.

### 3.3. MegaWinners and MegaLosers

MegaWinners and MegaLosers are *longer sequences* (longer than typical k-mers, but potentially shorter than prodigals) that are consistently associated with high efficiency (MegaWinners) or low efficiency (MegaLosers) in superpermutation construction.

*   **Identification:**  Identified by the `identify_mega_winners` and `identify_mega_losers` functions (in `analysis.py`), based on analyzing sequences and using winner/loser data.
*   **Lengths:** Experiment with different lengths, guided by *n* and the golden ratio (e.g., 14, 15, 21, 22 for n=8).
*   **Usage:**
    *   Used as building blocks in the "prodigal_combination" strategy (MegaWinners are treated similarly to prodigals).
    *   Used to guide the "mutation" strategy (avoiding MegaLosers, favoring MegaWinners).
    *   Used in the `insert_n_plus_1` function.
    * Used to help create, and refine, anti-prodigals.

### 3.4. Winners and Losers (WL_PUT)

"Winners" and "losers" are k-mers (typically of length n-1 and n-2) that are statistically more or less frequent in shorter/longer superpermutations, respectively.

*   **Data Structure:** Stored in a *single* dictionary (`winners_losers`) where:
    *   Keys: Tuples of the form `(n, kmer)`, where `n` is the number of symbols and `kmer` is the k-mer string.  This allows us to store winner/loser data for different *n* values in the same dictionary.
    *   Values: Floating-point weights.  *Positive* weights indicate "winners," and *negative* weights indicate "losers."
*   **Calculation:** Calculated by the `calculate_winners_losers` function (in `analysis.py`), which compares the frequency of k-mers in shorter vs. longer superpermutations.
*   **Usage:**
    *   `calculate_score`:  Used to add a bonus/penalty to candidate permutations based on their winner/loser content.
    *   `generate_candidates`:  Used to bias candidate generation towards winners and away from losers.
    *   `identify_anti_prodigals`: Used to identify anti-prodigals.
    *   `analyze_breakpoint`: Used to analyze the context of imperfect transitions.
    *  Used in many other functions.

### 3.5. Limbo List

The Limbo List is a set of k-mers or permutations that are to be *avoided* during candidate generation. This is a simple mechanism for preventing the algorithm from repeatedly exploring unproductive regions of the search space. *Currently, it is not a focus*.

### 3.6. Layout Memory

The Layout Memory stores information about the *relative positions* of k-mer pairs in known good superpermutations.

*   **Data Structure:** An instance of the `LayoutMemory` class (in `layout_memory.py`).  Internally, it uses a dictionary where:
    *   Keys: Tuples of the form `((n, kmer1), (n, kmer2))`, representing a transition between two k-mers.
    *   Values: Dictionaries containing:
        *   `count`: The number of times this transition has been observed.
        *   `sources`:  A set of strings indicating the sources where this transition was observed (e.g., "n=7 minimal," "n=8 prodigal").
*   **Usage:**  The `calculate_score` function uses the layout memory to give a bonus to candidates that are consistent with the observed transition frequencies.

### 3.7. Laminates and Anti-Laminates

*   **Laminates (Positive Constraints):** Directed graphs (NetworkX DiGraphs) where nodes are (n-1)-mers (or (n-2)-mers) and edges represent *allowed* transitions.
*   **Anti-Laminates (Negative Constraints):** Directed graphs where edges represent *disallowed* transitions.
*   **Data Structure:** Stored as a dictionary, keyed by tuples of n and k.
*   **Constraint Laminate:** A special laminate derived from the *current best known* superpermutation, enforcing a length constraint.
*   **Usage:** Used as *hard filters* during candidate generation (`generate_candidates`, `generate_hypothetical_superpermutation`). Any candidate that violates the selected laminates or anti-laminates is *immediately rejected*.
*   **Dynamic Updates:** Laminates and anti-laminates are *dynamically updated* based on new data (new prodigals, new anti-prodigals, new superpermutations).
*   **"Laminate Album":**  The algorithm maintains a collection ("album") of laminates and anti-laminates, derived from different sources, and *selects* the most appropriate ones for each task using the `select_laminates` function.
* **Bouncing:** Laminates are "bounced" in the bouncing batch.

### 3.8. Constraint Laminate
A special laminate that is created from existing best superpermutation, to ensure that only sequences of equal or better length are created.

### 3.9. ePUT (Deprecated in v6.0)

The Enhanced Permutation Universe Tracker (ePUT) *was* used in earlier versions to track all encountered permutations. In v6.0, this functionality is largely superseded by the constraint laminate and the focus on constructive methods.

### 3.10. Bouncing Batch

The Bouncing Batch methodology is a *parallel processing framework* for exploring the superpermutation search space.

*   **Grid Structure:** The permutation space is conceptually divided into a multi-dimensional grid (hypercube) with 2<sup>n</sup> cells.  Each cell corresponds to a specific combination of parities (even/odd positions) for the digits in the permutations.
*   **Parallel Processing:**  Multiple worker processes (using `multiprocessing`) test candidate superpermutations against different cells of the grid *concurrently*.
*   **Information Exchange:**  After processing a batch of candidates, the workers "bounce" information back to the main process.  This information includes:
    *   Updated winners/losers.
    *   New anti-prodigals.
    *   Updated *local* laminates and anti-laminates (in some versions).
*   **Locality:** The grid structure encourages *locality*. Permutations that are "close" to each other (in terms of their structure) are likely to be assigned to the same or neighboring cells.

### 3.11. n-1 Shell Construction

This is the *primary* superpermutation construction strategy for ConStruct v6.0. It involves:

1.  **Selecting Segments:** Choosing a set of segments from known minimal superpermutations for *n-1*.  These segments are typically:
    *   Prodigals (extended maximally).
    *   Sequences *between* imperfect transitions in the n-1 superpermutations.
    *   MegaWinners.
2.  **Inserting the *n*th Symbol:**  Using the `insert_n_plus_1` function to strategically insert the *n*th symbol into the selected segments, creating valid *n*-permutations. This insertion process is guided by *all* available data (winners/losers, layout memory, laminates, anti-laminates, De Bruijn graph).
3.  **Connecting Segments:**  Finding short, efficient "bridge" sequences to connect the extended segments, using `generate_bridge_candidates` and `calculate_bridge_score`.  The De Bruijn graph is heavily used in this step.

### 3.12. Extensibility Score

The *extensibility score* of a sequence (typically a prodigal or a segment) is a measure of how easily it can be extended to higher *n* values.  It's calculated by `calculate_extensibility_score` and is based on:

*   Overlap potential with (n+1)-permutations.
*   Winner/loser density (considering n+1 winners/losers).
*   Layout memory consistency (with the n+1 layout memory).
*   Laminate and anti-laminate compatibility (for n+1).
*   De Bruijn graph properties (for n+1)

### 3.13. Breakpoints

A *breakpoint* is a position within a sequence (typically a prodigal) where an *imperfect transition* (non-maximal overlap) occurs, or is likely to occur when the sequence is used in a larger superpermutation. Breakpoints are identified by the `analyze_prodigal` function and are used to guide the connection of prodigals and the application of mutations.

### 3.14. Action Function

The *action function* is a mathematical function that quantifies the "inefficiency" or "cost" of a superpermutation (or a partial superpermutation). It combines multiple factors, including:

*   Deviation from maximal overlap.
*   Winner/loser density.
*   Layout memory inconsistency.
*   Anti-laminate violations.
*   Discrepancy from predicted length (based on formulas).
*   "Curvature" (based on De Bruijn graph properties).
*   Extensibility.

The goal of the algorithm is to *minimize* the action. The `calculate_score` function uses the action function (or components of it) to evaluate candidate permutations and sequences.

### 3.15. Formula Definitions (I(n), C(n), Segment Length)

*   **I(n):** The *predicted* number of imperfect transitions in a minimal superpermutation for a given *n*. This is a crucial formula that's being continuously refined.
*   **C(n):** The "correction term," representing the difference between the simple additive formula for superpermutation length (`n! + SP(n-1)`) and the actual minimal length.  It's hypothesized to be closely related to `I(n)`.
*   **Optimal Segment Length:** A formula that predicts the ideal length of segments (prodigals) for constructing superpermutations.  This formula is also being refined and is likely to depend on `I(n)` and other factors.

### 3.16 De Bruijn Graph Analysis

The De Bruijn Graph is used throughout the system, for multiple tasks.