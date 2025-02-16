## 6. Running the Code

This section provides instructions on how to run the ConStruct superpermutation solver.

### 6.1. Prerequisites

Before running the code, ensure you have the following:

*   **Python 3.7+:** The code is written in Python and requires a Python 3.7 or later interpreter.
*   **NetworkX:**  The `networkx` library is used for graph operations (De Bruijn graphs, laminates). Install it using:
    ```bash
    pip install networkx
    ```
*   **Pickle:** The `pickle` library is used for saving and loading the layout memory. It is usually included with Python.

### 6.2. Setup

1.  **Download/Copy the Code:** Obtain the ConStruct v6.0 code files:
    *   `construct.py`
    *   `config.py`
    *   `utils.py`
    *   `analysis.py`
    *   `graph.py`
    *   `laminate.py`
    *   `prodigal.py`
    *   `formulas.py`
    *  `data_manager.py`
    *   `evaluator.py`

2.  **Place Files in the Same Directory:**  Place all the `.py` files in the same directory. This ensures that the modules can import each other correctly.
3.  **Create a Data Directory:** It is recommended, for good practice, to create an empty directory to house the files that will be generated.

### 6.3. Execution

The ConStruct program is designed to be run from the command line, using `construct.py` as the main entry point. The behavior of the program is controlled by configuration files.

1.  **Configuration (`config.py`):**
    *   The `config.py` file contains *n*-specific configuration dictionaries (e.g., `config_n6`, `config_n7`, `config_n8`).  These dictionaries store:
        *   The target `n` value.
        *   The random seed (`seed`).
        *   Bouncing Batch parameters (`grid_dimensions`).
        *   Strategy choices and probabilities (`generation_strategies`).
        *   Formula choices (`formula_set`, `action_function`).
        *   Scoring function weights (`action_weights`).
        *   Various thresholds and parameters (e.g., `prodigal_min_length`, `anti_prodigal_threshold`, `reconfigure_frequency`, etc.).
        *   File paths for data (currently set to `None` to ensure a clean start).
    *   You *must* modify the `config.py` file to set the desired `n` value and any other parameters you want to change.  *Do not* modify the code directly to change parameters; use the configuration file.

2.  **Running the Program:**
    *   Open a terminal or command prompt.
    *   Navigate to the directory where you placed the `.py` files.
    *   Execute the `construct.py` script using Python:
        ```bash
        python construct.py
        ```
    *   The script will:
        *   Load the configuration for the specified `n` value.
        *   Initialize data structures (starting from scratch, as per the v6.0 design).
        *   Begin the iterative superpermutation construction process (starting from n=1 and building up to the target `n`).
        *   Log detailed information about its progress to the console and to the `superpermutation.log` file.
        *   Save the best superpermutation found to `best_superpermutation_n[n].txt` (where [n] is the target n value).

3.  **Monitoring Progress:**

    *   **Console Output:** The program prints summary information to the console, including the current best superpermutation length, the number of missing permutations, and the results of DTT iterations.
    *   **Log File (`superpermutation.log`):** The `superpermutation.log` file contains *much more detailed* information about the execution, including:
        *   Timestamps.
        *   Logging levels (DEBUG, INFO, WARNING, ERROR).
        *   Messages about strategy selection, candidate generation, scoring, data updates, etc.
        *   Error messages (if any).
        *   This file is crucial for understanding the algorithm's behavior and for debugging.

4.  **Interrupting and Resuming:**

    *   The algorithm is designed to be robust and to allow for interruption and resumption. Because all data is generated from scratch, there is no resuming. The program can simply be re-run.
    * To stop, simply use the standard method for your OS.

5. **Expected output:**

    * The code is set up to begin working from n=1, and build up from there. The final n value is determined in the config file, with n=8 as the default.
    * As the program runs, detailed logs are saved to "superpermutation.log", showing actions taken.
    *  Any results from analysis will be printed to the console.
    * Upon finding a valid superpermutation, the string will be saved to `best_superpermutation_n[n].txt`.

6. **Multiprocessing:**
    * The code is designed to use multi-processing, and how many processes to run at once is determined by the system you run it on.

This completes the "Running the Code" section. Next will be a summary of results.