## 4. Algorithm: ConStruct (v6.0)

### 4.1. Overview (Constructive Approach)

ConStruct v6.0 employs a *constructive* approach to building superpermutations.  Instead of starting with a large, random sequence and iteratively refining it, ConStruct builds superpermutations from the ground up, using a combination of:

*   **n-1 Shell Strategy:** Leveraging the structure of known minimal superpermutations for *n-1* as the foundation.
*   **Prodigal-Centric Construction:**  Prioritizing the use of highly efficient subsequences ("prodigals" and MegaWinners) as building blocks.
*   **Data-Driven Decisions:** Making all construction choices (segment selection, insertion of the *n*th symbol, bridging) based on accumulated data:
    *   Winners/Losers
    *   Layout Memory
    *   Laminates and Anti-Laminates
    *   De Bruijn Graph Analysis
    *   Formulas (for predicting imperfect transitions, segment lengths, and overall length)
*   **Bouncing Batch Framework:**  Using the Bouncing Batch methodology for parallel processing and information exchange.
*   **Targeted Optimization:** Focusing optimization efforts on regions around imperfect transitions ("breakpoints").
* **Iterative n-Building:** Starting with n=1, and using each result to inform the next.

This constructive approach contrasts with earlier versions of the algorithm, which relied more heavily on random generation and iterative refinement. The shift to a constructive approach is motivated by the increasing complexity of the problem as *n* grows, and the need for more precise control over the superpermutation structure.

### 4.2. Initialization

Before the main construction loop begins, the following initialization steps are performed:

1.  **Load Configuration:** The `construct_superpermutation` function receives a `config` dictionary as input. This dictionary contains all the parameters that control the algorithm's behavior, including:
    *   The target *n* value.
    *   The random seed.
    *   File paths for data (winners/losers, layout memory, etc.).
    *   Parameters for the Bouncing Batch (grid dimensions).
    *   The choice of generation strategies and their weights.
    *   The weights for the scoring function.
    *   Thresholds for prodigal identification, anti-prodigal identification, etc.
    *   The formula set to use.

2.  **Initialize Data Structures:**
    *   `winners`, `losers`: Initialized as empty dictionaries.  If data files are specified in the configuration, they are loaded.
    *   `layout_memory`: An instance of the `LayoutMemory` class is created. If a data file is specified, it's loaded.
    *   `prodigal_manager`: An instance of the `ProdigalManager` class is created.  If a prodigal data file is specified, it's loaded.
    *   `laminates`, `anti_laminates`: Initialized as empty dictionaries.
    *   `constraint_laminates`: Initialized as an empty list. If a best-known superpermutation file is specified, a constraint laminate is created from it.

3. **Iterative n-Building:** This is at the core, the program starts with n=1, and builds up, carrying over all relevant data.

### 4.3. Main Construction Loop

The core of the `construct_superpermutation` function is a loop that iteratively builds up the superpermutation. The overall structure is as follows:
for current_n in range(1, n + 1):
# --- Data Loading/Initialization (for current_n) ---
# ... (Load/initialize data structures, using data from current_n-1) ...

if current_n <= 5:
    # --- Base Cases (n <= 5) ---  Use direct generation
    superpermutation = generate_n_minus_1_superpermutation(current_n, seed)
    # ... (Analyze superpermutation, update data structures) ...
else:
    # --- Main Construction Loop (n >= 6) ---
    while True:  # Continue until a valid superpermutation is found or max iterations reached
        # 1. Select a Strategy (dynamically, based on config and current state)
        strategy = select_strategy(config, laminates, anti_laminates)  # Implemented

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
        is_valid, length, winners, losers, _ = bouncing_batch_test(
            hypothetical_sp, current_n, config["grid_dimensions"], prodigal_manager,
            config["layout_memory_filename"], anti_laminates, constraint_laminates, winners, losers
        )

        # 4. Data Update and Analysis
        #  - Update winners/losers, layout memory, prodigal_manager, anti_laminates
        #  - Analyze imperfect transitions, update formulas, etc.
        #  - Identify new prodigals and anti-prodigals
        #  - Identify new MegaWinners and MegaLosers

        # 5. Check for Completion and Validity
        if is_valid:
            if length < best_known_length:
                best_known_length = length
                logging.info(f"New best superpermutation found for n={current_n}! Length: {length}")
                # ... (Save the new best superpermutation) ...
                #Create new contraint laminate

            # ... (Save superpermutation, analyze, etc.) ...

            break # Exit inner loop, move to n+1
        else:
            logging.info(f"Generated superpermutation is not valid (length: {length}).")
            continue
        #Check if we should run reconfiguration
        #Run analysis

#Save all data.
#Prepare all data for next n value.

#### 4.3.1. n-1 Segment Selection

The `select_n_minus_1_segments(n, ...)` function is responsible for choosing the (n-1)-segments that will form the "shell" of the n-superpermutation.  It uses the following criteria:

*   **Prodigals:** Prioritizes segments that are known prodigals for n-1.
*   **Extensibility:**  Considers the `extensibility_score` of the segments (how well they can be extended to *n*).
*   **Winner/Loser Density:**  Favors segments with high winner density and low loser density (in the (n-1) context).
*   **Breakpoint Analysis:**  Avoids segments with severe internal breakpoints.
*   **Coverage:** Aims to select a set of segments that, in combination, cover a large proportion of the (n-1)! permutations.
*   **Diversity:** Avoids selecting segments that are too similar to each other.

This function uses the `ProdigalManager` to access and rank the prodigals.

#### 4.3.2. n-Symbol Insertion

The `insert_n_plus_1(segment, n, ...)` function (in `analysis.py`) takes an (n-1)-segment and inserts the *n*th symbol at various positions to create candidate *n*-permutations.  This is a *critical* step, and it's done very carefully:

*   **All Possible Positions:**  It considers *all* possible insertion positions for the new symbol.
*   **Filtering:**  It immediately filters out any resulting sequences that:
    *   Are not valid permutations.
    *   Violate the constraint laminate.
    *   Violate any anti-laminates.
*   **Scoring:** It scores the remaining candidates based on:
    *   Winner/loser density (of the resulting n-k-mers).
    *   Layout memory consistency.
    *   De Bruijn graph properties.
*   **Return Value:**  It returns a *set* of the top-scoring n-permutations (represented as hashes).

#### 4.3.3. Bridging

The `generate_bridge_candidates(...)` function (in `construct.py`) is used to find short sequences of permutations that connect two segments (either (n-1)-segments or extended (n-1)-segments). It uses:

*   **De Bruijn Graph Search:**  A modified A* search algorithm on the De Bruijn graph, prioritizing paths that:
    *   Connect the end of the first segment to the beginning of the second segment.
    *   Use high-weight "winner" edges.
    *   Avoid "loser" edges.
    *   Avoid anti-laminate violations.
    *   Minimize length.
*   **Backtracking Search:** If the De Bruijn graph search fails, a constrained backtracking search is used.
* **Formula Guidance:** The *I(n)* formula is used to estimate how many "imperfect" transitions are acceptable within the bridge.

#### 4.3.4. Bouncing Batch Testing

The Bouncing Batch methodology is used to parallelize the testing of candidate superpermutations.  The key aspects are:

*   **Grid Structure:**  The permutation space is divided into cells based on a chosen criterion (currently, the parity of digit positions). For n=8, a 2<sup>8</sup> grid is used. Other grid structures are planned.
*   **Parallel Processing:**  Multiple candidate superpermutations are tested concurrently, using `multiprocessing`.
*   **Information Exchange:**  After processing a batch of candidates, information is "bounced" between cells:
    *   Winners/losers are updated (using weighted averaging).
    *   Local laminates (within each cell) are updated.
    *   Local anti-laminates are updated
    *   These laminates are then *merged* between neighboring cells.

#### 4.3.5. Data Aggregation and Update

After each Bouncing Batch iteration (or after processing a set of candidates), the following data structures are updated:

*   **Winners/Losers:**  Combined using weighted averaging.
*   **Layout Memory:** Updated with new transitions.
*   **Prodigal Manager:** New prodigals are added (after extension and analysis).
*   **Anti-Prodigals:** New anti-prodigals are identified.
*   **Laminates/Anti-Laminates:**  New laminates and anti-laminates are created, and existing ones might be updated or merged.

#### 4.3.6. Reconfiguration (Local Optimization)

The `reconfigure_superpermutation` function is called periodically to perform local optimizations on the current (partial or complete) superpermutation. It uses techniques like:

*   Permutation swapping.
*   Permutation rotation.
*   k-mer optimization.
*   Prodigal replacement.
*   Bridge refinement.

These modifications are guided by the scoring function and simulated annealing.

#### 4.3.7. Formula Refinement

The formulas for `SP(n)`, `I(n)`, and segment length are continuously refined based on the data generated by the simulations. This is an ongoing process.

#### 4.3.8. Dynamic Strategy Selection
The algorithm dynamically selects between different strategies for generating, using laminate data.

#### 4.3.9. Termination Condition

The construction loop terminates when a valid superpermutation is found (all permutations are covered) that meets the target length (initially the best-known length, and then updated whenever a shorter solution is found). There's also a maximum iteration limit to prevent infinite loops.

**4.4 Completion (If Necessary):**

If the main construction loop terminates *without* finding a complete superpermutation (which is likely for n=8), the remaining missing permutations are identified. These are then added.

**4.5 Multi-Processing:**
Used to drastically increase efficiency.

**4.6 Dynamic Data Updates:**
All data is dynamically updated and used throughout the run.

This completes the Algorithm section. Next will be the code structure.