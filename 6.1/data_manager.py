# data_manager.py
import csv
import json
import pickle
import os
from layout_memory import LayoutMemory
import networkx as nx

# All of these functions will be very similar to before, but will work with internal data

# In-memory storage for simulating file I/O
_data = {
    "winners_losers": {},       # { (n, kmer): weight }
    "layout_memory": {},        # { (n, (kmer1, kmer2)): {count: int, sources: set} }
    "prodigals": {},         # Managed by ProdigalManager, loaded/saved via to/from dict.
    "laminates": {},   # { (n, k): [list of laminate dictionaries] }
    "anti_laminates": {},
    "best_superpermutation": {}, # { n: "superpermutation_string" }
}

def _save_data(data_key, data, filename):
    """Simulates saving data to a file (actually stores in _data)."""
    _data[data_key] = data
    print(f"Simulated saving {data_key} to {filename}")


def _load_data(data_key, filename, default_value):
    """Simulates loading data from a file (actually retrieves from _data)."""
    print(f"Simulated loading {data_key} from {filename}")
    return _data.get(data_key, default_value)

# --- Superpermutation ---
def save_superpermutation(superpermutation, n, filename_prefix="best_superpermutation"):
  _save_data(f"best_superpermutation_n{n}", superpermutation, f"{filename_prefix}_n{n}.txt")

def load_superpermutation(n, filename_prefix="best_superpermutation"):
    return _load_data(f"best_superpermutation_n{n}", f"{filename_prefix}_n{n}.txt", "")

# --- Winners and Losers ---
def save_winner_loser_data(winners_losers, n, filename_prefix="winners_losers_data"):
  _save_data(f"winners_losers_n{n}", winners_losers,  f"{filename_prefix}_n{n}.txt")

def load_winner_loser_data(n, filename_prefix="winners_losers_data"):
    return _load_data(f"winners_losers_n{n}", f"{filename_prefix}_n{n}.txt", {})

# --- Layout Memory ---
def save_layout_memory_data(layout_memory, n, filename_prefix="layout_memory"):
  #Need to save as dict
    _save_data(f"layout_memory_n{n}", layout_memory.memory, f"{filename_prefix}_n{n}.pkl") # Save the memory *directly*

def load_layout_memory_data(n, filename_prefix="layout_memory"):
    memory_dict = _load_data(f"layout_memory_n{n}", f"{filename_prefix}_n{n}.pkl", {})
    layout_memory = LayoutMemory()  # Create a new instance
    layout_memory.memory = memory_dict # Load
    return layout_memory

# --- Prodigals ---
def save_prodigal_data(prodigal_manager, n, filename_prefix="prodigal_results"):
    _save_data(f"prodigals_n{n}", prodigal_manager.prodigal_results, f"{filename_prefix}_n{n}.json") # Save all.

def load_prodigal_data(n, filename_prefix="prodigal_results"):
    # We don't actually *load* into the ProdigalManager here; we just simulate it.
    return _load_data(f"prodigals_n{n}", f"{filename_prefix}_n{n}.json", {})

# --- Laminates and Anti-Laminates ---
# Since these are dictionaries of NetworkX graphs, we'll simulate saving/loading
# with a simplified representation (just storing the number of graphs for each type).

def save_laminates(laminates, n, filename_prefix="laminates"):
    # In a real implementation, you might use pickle or a graph serialization format.
    laminate_data = {key: [g.edges() for g in graph_list] for key, graph_list in laminates.items()}
    _save_data(f"laminates_n{n}", laminate_data, f"{filename_prefix}_n{n}.pkl")

def load_laminates(n, filename_prefix="laminates"):
    laminate_data = _load_data(f"laminates_n{n}", f"{filename_prefix}_n{n}.pkl", {})
    laminates = {}
    for key, edge_list in laminate_data.items():
      laminates[key] = []
      for edges in edge_list:
        graph = nx.DiGraph()
        graph.add_edges_from(edges)
        laminates[key].append(graph)
    return laminates

def save_anti_laminates(anti_laminates, n, filename_prefix="anti_laminates"):
    anti_laminate_data = {key: [g.edges() for g in graph_list] for key, graph_list in anti_laminates.items()}
    _save_data(f"anti_laminates_n{n}", anti_laminate_data, f"{filename_prefix}_n{n}.pkl")

def load_anti_laminates(n, filename_prefix="anti_laminates"):
    anti_laminate_data = _load_data(f"anti_laminates_n{n}", f"{filename_prefix}_n{n}.pkl", {})
    anti_laminates = {}
    for key, edge_list in anti_laminate_data.items():
      anti_laminates[key] = []
      for edges in edge_list:
        graph = nx.DiGraph()
        graph.add_edges_from(edges)
        anti_laminates[key].append(graph)
    return anti_laminates

# --- Workbooks (Conceptual - for internal use) ---

def create_workbook(workbook_name):
    _data[f"workbook_{workbook_name}"] = {} #Initialize empty

def add_entry_to_workbook(workbook_name, section, entry_data):
    if f"workbook_{workbook_name}" not in _data:
        create_workbook(workbook_name)
    if section not in _data[f"workbook_{workbook_name}"]:
        _data[f"workbook_{workbook_name}"][section] = []
    _data[f"workbook_{workbook_name}"][section].append(entry_data) #Add the entry

def get_section_from_workbook(workbook_name, section):
    return _data.get(f"workbook_{workbook_name}", {}).get(section, []) # Get sections

def query_workbook(workbook_name, section, criteria):
    # Placeholder for query functionality (would need specific implementation based on data structure)
    return []

def save_workbook(workbook_name, filename):
  pass #Not needed as it is all internal.

def load_workbook(workbook_name, filename):
    return _data.get(f"workbook_{workbook_name}", {})