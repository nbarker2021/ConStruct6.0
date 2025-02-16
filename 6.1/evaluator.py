# formula_evaluator.py

import math
from utils import generate_permutations, is_valid_permutation, calculate_overlap
from analysis_scripts_final import find_prodigal_results, calculate_winners_losers, identify_anti_prodigals, count_imperfect_transitions, analyze_imperfect_transition_distribution
import formulas  # Import the formulas module
from collections import defaultdict
import logging

# Example data (replace with actual data loading)
# For now, using dictionary, will pull from files.
KNOWN_MINIMAL_LENGTHS = {
    1: 1,
    2: 3,
    3: 9,
    4: 33,
    5: 153,
    6: 872,
    7: 5906
}
#Will update as needed.

def evaluate_sp_formula(formula_name, n_values, known_values):
    """Evaluates a superpermutation length formula.

    Args:
        formula_name (str): The name of the formula function in formulas.py.
        n_values (list): A list of n values to test.
        known_values (dict): A dictionary mapping n values to known minimal lengths.

    Returns:
        dict: A dictionary containing the results: predicted lengths, actual lengths, and errors.
    """

    results = {"predicted": [], "actual": [], "errors": [], "mse": 0.0, "mae": 0.0}
    formula_func = getattr(formulas, formula_name)  # Get function from formulas.py
    total_squared_error = 0
    total_absolute_error = 0
    num_values = 0

    for n in n_values:
        if n not in known_values:
          continue #If no known value, skip.

        #Handle the different numbers of arguments for different formulas.
        if formula_name.startswith("sp_"): # Superpermutation length formula
          if formula_name in ['sp_lower_bound']:
            predicted = formula_func(n) # Lower bound takes only n
          elif formula_name in ['sp_v14', 'sp_additive', 'sp_v15']:
            if n-1 not in known_values:
              continue #Cant use it yet
            predicted = formula_func(n, known_values[n-1], 0) #Need previous value and n.
          else: #Unknown formula
            continue #Skip

        elif formula_name.startswith("c_n"):
          predicted = formula_func(n) #Should take just n
        elif formula_name.startswith("i_n"):
          predicted = formula_func(n) #Likely just uses n.
        elif formula_name.startswith("segment_length"):
          predicted = formula_func(n) #Likely just uses n.
        #Add other formula types here, like action functions.
        else:
          continue #unknown, skip

        actual = known_values[n]
        error = predicted - actual


        results["predicted"].append(predicted)
        results["actual"].append(actual)
        results["errors"].append(error)

        total_squared_error += error**2
        total_absolute_error += abs(error)
        num_values += 1

    if num_values > 0:
        results["mse"] = total_squared_error / num_values
        results["mae"] = total_absolute_error / num_values
    else:
        results["mse"] = None
        results["mae"] = None

    return results

def evaluate_segment_formula(formula_name, n_values, prodigal_data):
    """Evaluates a segment length formula.
    prodigal_data format:  {n: [list_of_prodigal_lengths]}
    """
    results = {"predicted": [], "actual_avg": [], "actual_median": [], "errors_avg": [], "errors_median": []}
    formula_func = getattr(formulas, formula_name)

    for n in n_values:
        if n not in prodigal_data:
            continue
        #Handle different arguments
        if formula_name.startswith("segment_length"):
          if formula_name in ['segment_length_best']:
            #Need to get I(n)
            predicted = formula_func(n, formulas.calculate_i_n(n))
          elif formula_name in ['segment_length_v14']:
            if n-1 not in KNOWN_MINIMAL_LENGTHS:
                continue
            predicted = formula_func(n, KNOWN_MINIMAL_LENGTHS[n-1])
          else:
            predicted = formula_func(n)  # Call the function.
        else:
          continue
        results["predicted"].append(predicted)

        actual_lengths = prodigal_data[n]
        if len(actual_lengths) > 0:
            avg_length = sum(actual_lengths) / len(actual_lengths)
            median_length = sorted(actual_lengths)[len(actual_lengths) // 2]
            results["actual_avg"].append(avg_length)
            results["actual_median"].append(median_length)
            results["errors_avg"].append(predicted - avg_length)
            results["errors_median"].append(predicted - median_length)
        else:
            results["actual_avg"].append(None)
            results["actual_median"].append(None)
            results["errors_avg"].append(None)
            results["errors_median"].append(None)

    return results

def evaluate_action_formula(formula_name, superpermutations, n, winners, losers, layout_memory, anti_laminates):
    """Evaluates an action function formula."""
    results = {"actions": []}
    formula_func = getattr(formulas, formula_name)

    # Handle the different numbers of arguments for different formulas.
    for superperm in superpermutations:
      if formula_name.startswith("action_"):
        if formula_name in ['action_a1']:
          action = formula_func(superperm, n) #Call
        elif formula_name in ['action_a2']:
          action = formula_func(superperm, n, winners, losers)
        # Add other formula types here
        else:
          continue #unknown, skip
        results["actions"].append(action)
      else:
        continue #Not an action function

    # Add more analysis as needed (average action, etc.)
    return results

def compare_formulas(formula_names, n_values, known_values, prodigal_data, superpermutations):
    """Compares multiple formulas based on different metrics."""
    results = {}
    winners = {}
    losers = {}
    if superpermutations:
        winners, losers = calculate_winners_losers(superpermutations, n_values[0]) # Get winners, losers
    for formula_name in formula_names:
        if formula_name.startswith("sp_"):
            results[formula_name] = evaluate_sp_formula(formula_name, n_values, known_values)
        elif formula_name.startswith("segment_length"):
            results[formula_name] = evaluate_segment_formula(formula_name, n_values, prodigal_data)
        elif formula_name.startswith("action_"):
            results[formula_name] = evaluate_action_formula(formula_name, superpermutations, n_values[0], winners, losers, {}, []) # Assuming n is constant for action
        # Add other formula types here
    return results

# --- I(n) and C(n) Formulas ---
def calculate_i_n(n):
    """Calculates I(n) using the current best formula."""
    # Update this whenever the best I(n) formula changes
    return formulas.i_n_factorial_diff(n)

def calculate_c_n(n, superperm_length):
    """Calculates C(n) based on predicted I(n) and best known length."""
    sp_predicted = formulas.sp_v14(n, KNOWN_MINIMAL_LENGTHS.get(n-1, 0)) # Get from dictionary if we can
    return superperm_length - sp_predicted