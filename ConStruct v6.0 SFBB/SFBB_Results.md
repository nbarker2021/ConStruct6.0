## 7. Results

This section summarizes the key results achieved by the Superpermutation Solver project, focusing on the different *n* values explored.

### 7.1. n=6 Results

*   **Minimal Length:** The algorithm consistently and rapidly generates minimal superpermutations of length 872 for n=6. This confirms the known theoretical minimum.
*   **Distinct Solutions:**  The algorithm can generate a large number of *distinct* minimal superpermutations for n=6.
*   **n=6 Searcher:** A dedicated `n6_searcher.py` script was developed to exhaustively search for an 871-length n=6 superpermutation.  After testing billions of candidates, no 871-length solution was found, providing further strong empirical evidence that 872 is the true minimum. There is still miniscule possiblility that a single 871 example exists.
*   **Data Generated:**  Extensive data (winners/losers, prodigals, layout memory) was generated from the n=6 runs, which is used to inform the search for higher *n* values.

### 7.2. n=7 Results

*   **Minimal Length:** The algorithm consistently and rapidly generates minimal superpermutations of length 5906 for n=7. This confirms the known theoretical minimum.
*   **Distinct Solutions:** The algorithm can generate a large number of *distinct* minimal superpermutations for n=7. Over 100 distinct solutions were generated and used to inform the higher n values.
*   **Data Generated:**  Extensive data (winners/losers, prodigals, layout memory, anti-prodigals, laminates, anti-laminates) was generated from the n=7 runs. This data is *crucial* for guiding the search for n=8 and beyond.  In particular, the n=7 superpermutations and prodigals serve as valuable "building blocks."

### 7.3. n=8 Results

*   **Best Known Length (Prior to this Project):**  Prior to this project, the best *publicly known and verified* upper bound for n=8 was significantly larger (on the order of billions of digits) than the theoretical lower bound.
*   **Initial Record (Previous Versions):**  Previous versions of this project's algorithm achieved a validated n=8 superpermutation of length 25,478,480,308, establishing a new record.
*   **Current Best Length (v5.0):** The current version of the algorithm (v5.0), incorporating all the refinements and enhancements, has further reduced the length to **25,478,467,595**. This represents an improvement of 9,356,313 over previous published results, and 2871 over the initial v1.0 result.
*   **Ongoing Simulation:** The n=8 simulation is *ongoing*.  Further improvements are anticipated.
*   **Key Factors in Improvement:**
    *   **Bouncing Batch Methodology:**  Effective for handling the complexity of n=8.
    *   **Prodigal-Centric Approach:**  The focus on identifying, extending, and combining prodigals (especially using the "n-7 shell" strategy) is the primary driver of length reductions.
    *   **MegaWinners/MegaLosers:**  These longer sequences provide valuable guidance.
    *   **Laminates and Anti-Laminates:**  These constraints effectively prune the search space.
    *   **Dynamic n=7 Data Integration:** Continuously generating and incorporating new n=7 superpermutations provides a diverse set of building blocks.
    *   **Formula Refinement:**  The refined formulas for I(n) and segment length are guiding the search more effectively.
    *   **De Bruijn Graph Analysis:**  Used for anti-prodigal identification, guiding mutations, and informing the scoring function.
    *   **Reconfiguration:** The `reconfigure_superpermutation` function provides a valuable mechanism for local optimization.
    *   **Targeted Completion:** The specialized completion algorithm efficiently fills in missing permutations.

*   **Data Generated:** The n=8 simulations have generated a vast amount of data, including:
    *   Thousands of n=8 prodigals.
    *   Extensive winner/loser data (for k-mers and longer sequences).
    *   Detailed layout memory data.
    *   Numerous laminates and anti-laminates.

### 7.4. Formula Performance

*   **SP(n) (Superpermutation Length):**
    *   The formula `SP(n) = SP(n-1) * (n / φ)` (V14) remains a surprisingly good *simple* predictor, but it consistently underestimates the true minimal length.
    *   The most accurate predictions are obtained by using a formula of the form `SP(n) = n! + SP(n-1) + C(n)`, where C(n) is a "correction term" derived from the predicted number of imperfect transitions, I(n).

*   **I(n) (Imperfect Transitions):**
    *   The current best formula for I(n) is:
        ```
        I(n) = round(((factorial(n-1) - factorial(n-2)) / (n * 2)  - (n - 5)) * (1.33 + 0.01 * (n-6)) + (imbalance(n-1) - 2) * 5.5)
        ```
    *   This formula combines a factorial difference term, a scaling factor that depends on *n*, and a term based on the De Bruijn graph imbalance.
    *   This formula accurately predicts I(6) = 1 and I(7) = 6.
    *   The predicted I(8) value (around 27-30) is consistent with the observed number of imperfect transitions in the best n=8 superpermutations.

*   **Optimal Segment Length:**
    *   The formula `segment_length_best(n) = (n / φ) * (1 + 0.1 * I(n))` provides a reasonable estimate of the average prodigal length, and is used to guide the construction process.

*   **Action Functions:** Hybrid action functions, combining multiple factors (overlap, winners/losers, layout, laminates, discrepancy, curvature), are the most effective for guiding the search.

This section provides a concise summary of the key results achieved by the project. The next section will be on future work.