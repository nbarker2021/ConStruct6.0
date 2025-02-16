## Appendix: Formula Variations

This appendix provides a comprehensive list of all formula variations considered during the development of the Superpermutation Solver, categorized by their purpose. Each formula is given a unique ID, a brief description, its mathematical expression, and notes on its status (e.g., "Deprecated," "Experimental," "Promising," "Best Current") and performance.

### A. Superpermutation Length Formulas (SP(n))

These formulas attempt to predict the minimal superpermutation length for a given *n*.

*   **SP_1: Theoretical Lower Bound**
    *   **Formula:** `SP(n) >= n! + (n-1)! + ... + 1!`
    *   **Status:** Validated (for n <= 5), Incorrect (for n >= 6)
    *   **Notes:** Provides a theoretical minimum, but not achievable for n >= 6.

*   **SP_2: Simple Additive**
    *   **Formula:** `SP(n) = n! + SP(n-1)`
    *   **Status:** Deprecated (Incorrect for n >= 6)
    *   **Notes:**  Assumes maximal overlap between all permutations, which is not possible for n >= 6.

*   **SP_3: V14 (Golden Ratio Scaling)**
    *   **Formula:** `SP(n) ≈ SP(n-1) * (n / φ)`  (where φ is the golden ratio, ≈ 1.618)
    *   **Status:** Promising (but underestimates)
    *   **Notes:**  Provides a significantly better estimate than the simple additive formula, but consistently underestimates the true minimal length for n >= 6.  Captures the scaling behavior well.

*   **SP_4: V15 (with Correction Term)**
    *   **Formula:** `SP(n) = n! + SP(n-1) + C(n)`
    *   **Status:**  Conceptually Correct (tautology), but depends on C(n)
    *   **Notes:**  The accuracy depends entirely on the accuracy of the `C(n)` formula.

*   **SP_5: V14 with Correction**
    *   **Formula:** `SP(n) = SP(n-1) * (n / φ) + C(n)`
    *   **Status:** Experimental (depends on C(n))
    *   **Notes:** Combines the scaling of V14 with a correction term.

*   **SP_6: De Bruijn Based**
    *   **Formula:**  (Various formulas incorporating De Bruijn graph properties)
    *   **Status:** Experimental
    *   **Notes:**  Attempts to link superpermutation length to the structure of the De Bruijn graph.

*(Many other variations of the above were tested internally, with different constants, scaling factors, and combinations of terms. These are not listed individually here for brevity, but they are tracked in the internal workbooks.)*

### B. Correction Term Formulas (C(n))

These formulas attempt to model the "correction term" C(n), which represents the difference between a simple prediction of superpermutation length and the actual minimal length.

*   **C_1: Example (Linear)**
    *   **Formula:** `C(n) = a*n + b`
    *   **Status:** Deprecated (not accurate)
    *   **Notes:**  A simple linear model; doesn't capture the complexity.

*   **C_2: Quadratic**
    *   **Formula:** `C(n) = a*n^2 + b*n + c`
    *   **Status:** Deprecated (not accurate)
    *   **Notes:**  A quadratic model; still doesn't capture the rapid growth.

*   **C_3: Exponential**
    *   **Formula:** `C(n) = a * exp(b*n) + c`
    *   **Status:** Deprecated (not accurate)

*   **C_4: Golden Ratio Based**
    *   **Formula:** `C(n) = a * φ**(n + b) + c`
    *   **Status:** Deprecated (not accurate)

*   **C_5: Factorial Difference (Initial)**
    *   **Formula:** `C(n) = (n - 5) * (n - 6) / 2 + (n-6)`
    *   **Status:** Deprecated ( superseded by better formulas)
    *  **Notes:** Based on early observation of imperfect transition counts.

*   **C_6: Factorial Difference (Refined):**
    *  **Formula:**  Variations of  `C(n) = a * (factorial(n-1) - factorial(n-2)) / (n * b) + c`
    *   **Status:** Promising (used within I(n) formulas)
    *   **Notes:**  Captures the rapid growth in complexity, but needs scaling and potentially additional terms.

*   **C_7: De Bruijn Based:**
    *   **Formula:** Variations incorporating De Bruijn graph properties (imbalance, connectivity).  Example: `C(n) = a * imbalance(n-1) + b`
    *   **Status:** Experimental, integrated into I(n)
    *   **Notes:**  Attempts to link the correction term to the structure of the De Bruijn graph.

*(Many other variations were tested internally.)*

### C. Imperfect Transitions (I(n))

These formulas attempt to predict the number of imperfect transitions in a minimal superpermutation.

*   **I_1: Factorial Difference (Initial):**
    * **Formula:** `I(n) = (factorial(n-1) - factorial(n-2)) / (n * 2)  - (n - 5)`
    * **Status:** Promising, but needs refinement.

* **I_2: Current Best (v4.9):**
    ```
    I(n) = round(((factorial(n-1) - factorial(n-2)) / (n * 2)  - (n - 5)) * (1.33 + 0.01 * (n-6)) + (imbalance(n-1) - 2) * 5.5)
    ```
    *   **Status:** Best performing so far. Accurately predicts I(6) and I(7).
    *   **Notes:** Incorporates the factorial difference, a scaling factor, an offset, and the De Bruijn graph imbalance.

*   **(Other variations - numerous, based on De Bruijn graph properties, combinations of terms, etc. - were tested internally.)**

### D. Optimal Segment Length Formulas

These formulas attempt to predict the optimal length of segments (prodigals, MegaWinners) for superpermutation construction.

*   **segment_length_v5(n):**  `(n + (Limit / φ)) / (n * φ)`  (Deprecated)
*   **segment_length_v14(n, sp_n_minus_1):** `sp_n_minus_1 * (n/φ) / n!` (Deprecated)
*   **segment_length_best(n):** `(n / φ) * (1 + 0.1 * I(n))` (Current Best)
    *   **Status:** Promising.  Uses the golden ratio and the predicted number of imperfect transitions.
    *   **Notes:**  Needs further refinement and testing, especially for n=8.

*(Many other variations were tested internally.)*

### E. Action Function Formulas

These formulas quantify the "inefficiency" of a superpermutation.

*   **A1: Overlap-Based:**  (Simple sum of overlap deficiencies) - Baseline.
*   **A2: Overlap + Winner/Loser:** (Adds winner/loser density)
*   **A3: Layout-Constrained:** (Adds layout memory penalty)
*   **A4: Anti-Laminate Constrained:** (Adds anti-laminate violation penalty)
*   **A5: Hybrid:** (Weighted combination of A1-A4) - Best performing in early versions.
*   **A6: Hybrid + Discrepancy:** (A5 + penalty for deviation from predicted length)
* **A7 (Hybrid + Segment Length):** A5 + a term related to segment length.
* **A8 (Hybrid + Curvature):**  A5 + a term based on De Bruijn graph properties (e.g., imbalance).
* Many variations with changed weights.

This appendix provides a comprehensive overview of the formulas considered during the project.  The "Status" column indicates the current state of each formula. The most promising formulas are actively used in the ConStruct v6.0 code, while others are retained for potential future use or as points of comparison. The best performing formulas are the current focus, and are being actively used.