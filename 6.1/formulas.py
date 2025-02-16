# formulas.py
import math
import networkx as nx
from utils import generate_permutations, is_valid_permutation, calculate_overlap, kmer_to_int
from collections import defaultdict
from graph_utils import build_de_bruijn_graph, analyze_debruijn_graph

# Constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio
PI = math.pi
E = math.e

# --- Superpermutation Length Formulas ---

def sp_lower_bound(n):
    """Theoretical lower bound for SP(n). Status: Validated."""
    return sum(math.factorial(i) for i in range(1, n + 1))

def sp_additive(n, sp_n_minus_1):
    """Simple additive formula. Status: Deprecated (Incorrect for n>=6)."""
    return math.factorial(n) + sp_n_minus_1

def sp_v14(n, sp_n_minus_1):
    """Formula V14: SP(n-1) * (n / phi). Status: Promising (n=7)."""
    return sp_n_minus_1 * (n / PHI)

def sp_v15(n, sp_n_minus_1, c_n_minus_1):
    """Formula V15: n! + SP(n-1) + C(n-1) * (n/φ).  Status: Experimental."""
    return math.factorial(n) + sp_n_minus_1 + c_n_minus_1 * (n/PHI)

# --- Correction Term Formulas ---
def c_n_example(n):
	"""Example C(n) formula.  Status: Experimental."""
	return (n - 5) * (n-6) // 2 + (n-6) #From our discussion.

def c_n_linear(n, a, b):
    """Linear C(n) formula: a*n + b. Status: Experimental."""
    return a*n + b

def c_n_quadratic(n, a, b, c):
    """Quadratic C(n) formula: a*n^2 + b*n + c. Status: Experimental."""
    return a*n**2 + b*n + c

def c_n_exponential(n, a, b, c):
    """Exponential C(n) formula: a * exp(b*n) + c. Status: Experimental."""
    return a * math.exp(b*n) + c

def c_n_golden(n, a, b, c):
    """Golden Ratio based C(n) formula: a * φ**(n + b) + c. Status: Experimental."""
    return a * PHI**(n+b) + c

def c_n_factorial_diff(n, a, b, c):
    """Factorial difference C(n) formula. Status: Experimental."""
    return a * (math.factorial(n-1) - math.factorial(n-2)) / (n * b) + c

def c_n_debruijn(n, a, b, c):
    """De Bruijn graph based C(n) formula. Status: Experimental."""
    graph = build_de_bruijn_graph(["".join(map(str, p)) for p in generate_permutations(n - 1)], n - 1, n-2)
    imbalance = analyze_debruijn_graph(graph, n-1, n-2)['imbalance']
    return a * imbalance + b * n + c

# --- Imperfect Transitions Formulas ---
def i_n_factorial_diff(n, a=0.5, b=2, c=5, d=0, e=5.5):
    """Formula for I(n) based on factorial difference and De Bruijn imbalance. Status: Promising."""
    # Placeholder for De Bruijn graph analysis
    graph = build_de_bruijn_graph(["".join(map(str, p)) for p in generate_permutations(n - 1)], n - 1, n-2)
    imbalance = analyze_debruijn_graph(graph, n - 1, n-2)['imbalance']
    return round(((math.factorial(n-1) - math.factorial(n-2)) / (n * b)  - (n - c)) * (1.33 + 0.01 * (n-6)) + (imbalance - 2) * e)

# --- Segment Length Formulas ---

def segment_length_v5(n):
    """Segment length formula V5. Status: Deprecated."""
    return (n + (sp_lower_bound(n) / PHI)) / (n * PHI)

def segment_length_v14(n, sp_n_minus_1):
    """Segment Length, derived from best SP formula. Status: Testing."""
    return sp_n_minus_1*(n/PHI) / math.factorial(n) #Placeholder, needs more testing.

def segment_length_best(n, i_n):
    """Current best segment length formula. Status: Promising."""
    return (n / PHI) * (1 + 0.1 * i_n)

# --- Action Function Formulas ---

def action_a1(superpermutation, n):
    """Overlap-based action. Status: Baseline."""
    s_list = [int(x) for x in superpermutation]
    action = 0
    for i in range(len(s_list) - n):
        perm = tuple(s_list[i:i + n])
        if is_valid_permutation(perm, n):
            if i > 0:
                prev_perm = tuple(s_list[i-1:i-1+n])
                if is_valid_permutation(prev_perm, n):
                  overlap = calculate_overlap("".join(map(str,prev_perm)), "".join(map(str, perm)))
                  action += (n - 1) - overlap
    return action

def action_a2(superpermutation, n, winners, losers):
    """Overlap and Winner/Loser based action. Status: Testing."""
    s_list = [int(x) for x in superpermutation]
    action = 0
    for i in range(len(s_list) - n + 1):
        perm = tuple(s_list[i:i + n])
        if is_valid_permutation(perm, n):
            if i > 0:
                prev_perm = tuple(s_list[i-1:i-1+n])
                if is_valid_permutation(prev_perm, n):
                    overlap = calculate_overlap("".join(map(str,prev_perm)), "".join(map(str, perm)))
                    action += (n - 1) - overlap
            for k in [n-1, n-2]:
                for j in range(len(perm) -k + 1):
                    kmer = "".join(map(str,perm[j:j+k]))
                    action += losers.get((n,kmer), 0) - winners.get((n,kmer),0) #Losers are negative, so add.
    return action

# ... (Placeholders for A3, A4, A5 - based on previous descriptions) ...
def action_a3(superpermutation, n, layout_memory):
  return 0 #Placeholder

def action_a4(superpermutation, n, anti_laminates):
  return 0 #Placeholder

def action_a5(superpermutation, n, winners, losers, layout_memory, anti_laminates):
  return 0 #Placeholder

def action_a6(superpermutation, n, winners, losers, layout_memory, anti_laminates, segment_length):
  return 0 #Placeholder

def action_a7(superpermutation, n, winners, losers, layout_memory, anti_laminates, segment_length):
  return 0 #Placeholder

def action_a8(superpermutation, n, winners, losers, layout_memory, anti_laminates, de_bruijn_graph):
  return 0 #Placeholder

# --- Formula Combinations ---
# (Examples - Add more as we explore)

def combined_formula_1(n, sp_n_minus_1):
    """Example of combining formulas. Status: Experimental."""
    return sp_v14(n, sp_n_minus_1) + c_n_example(n)