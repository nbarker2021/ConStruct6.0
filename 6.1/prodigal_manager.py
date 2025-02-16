# prodigal_manager.py
import json
import logging
# Assuming analysis_scripts_final and utils are in the same directory
from analysis_scripts_final import calculate_winners_losers, identify_anti_prodigals, is_prodigal, calculate_sequence_score, find_prodigal_results,  calculate_extensibility_score, analyze_prodigal, extend_prodigal
from utils import is_valid_permutation, calculate_overlap, hash_permutation, unhash_permutation


class ProdigalManager:
    """Manages the collection, storage, analysis, and ranking of prodigal results."""

    def __init__(self, n, prodigal_file="prodigal_results.json"):
        """Initializes the ProdigalManager.

        Args:
            n (int): The value of n for this ProdigalManager.
            prodigal_file (str): The filename for storing prodigal data.
        """
        self.n = n
        self.prodigal_file = prodigal_file
        self.prodigal_results = {}  # {prodigal_id: {data}}
        self.next_prodigal_id = 0
        self.load_prodigals() # Load any saved


    def add_prodigal(self, sequence, n_value, source, winners={}, losers={}, layout_memory=None, laminates=[], anti_laminates=[]):
        """Adds a new prodigal to the database, after extending and analyzing it.

        Args:
            sequence (str): The potential prodigal sequence.
            n_value (int): The n value for which this sequence was found.
            source (str):  Information about how the prodigal was found.
            winners, losers, layout_memory, laminates, anti_laminates:  Current data.
        """

        # 1. Extend the prodigal
        extended_sequence, _ = extend_prodigal(sequence, n_value, winners, losers, layout_memory, laminates, anti_laminates)

        # 2. Analyze the prodigal
        prodigal_data = analyze_prodigal(extended_sequence, n_value, winners, losers, layout_memory, laminates, anti_laminates)

        # 3. Check if it's actually a prodigal (might not be, after extension)
        if prodigal_data["is_prodigal"]:

            # 4. Check if it's a duplicate (using sequence hash)
            is_new = True
            for existing_prodigal_id, existing_prodigal in self.prodigal_results.items():
                if extended_sequence == existing_prodigal['sequence']:
                    is_new = False
                    break

            if is_new:
                # 5. Add to the database
                prodigal_id = self.next_prodigal_id
                self.prodigal_results[prodigal_id] = {
                    "sequence": extended_sequence,
                    "length": len(extended_sequence),
                    "overlap_rate": prodigal_data["overlap_rate"],
                    "n_value": n_value,
                    "source": source,
                    "breakpoints": prodigal_data["breakpoints"],
                    "winner_score": prodigal_data["winner_score"],
                    "loser_score": prodigal_data["loser_score"],
                    "extensibility_score": prodigal_data["extensibility_score"],
                    "parent_prodigals": [],  # To be filled in if created by combining prodigals
                    "child_prodigals": [], # Or if this is used to make another.
                    "used_count": 0,
                    "id" : prodigal_id
                }
                self.next_prodigal_id += 1
                logging.info(f"Added new prodigal (ID: {prodigal_id}, Length: {len(extended_sequence)} , Source: {source})")
            else:
                logging.debug("Skipped adding duplicate prodigal.")
        else:
            logging.debug("Sequence not prodigal after extension.")


    def get_best_prodigals(self, n, task, context):
        """Retrieves the best prodigals based on the current context.

        Args:
            n (int): The target n value.
            task (str): The task for which prodigals are needed (e.g., "generation", "completion").
            context (dict):  Additional context information (e.g., current superpermutation, missing permutations).

        Returns:
            dict: A dictionary of the best prodigals, sorted by rank.
        """
        # 1. Filter prodigals based on n_value
        relevant_prodigals = {
            pid: data for pid, data in self.prodigal_results.items() if data["n_value"] == n
        }

        # 2. Rank prodigals
        ranked_prodigals = self.rank_prodigals(relevant_prodigals)

        # 3.  Return (for now, return all, sorted)
        return ranked_prodigals

    def rank_prodigals(self, prodigals):
        """Ranks prodigals based on a combined score."""
        #This is a basic ranking, and can be improved.
        scored_prodigals = []
        for p_id, p_data in prodigals.items():
            score = (
                p_data["length"] * 1 +
                p_data["overlap_rate"] * 100 +
                p_data["winner_score"] -
                p_data["loser_score"] -
                len(p_data["breakpoints"]) * 10 + # Fewer breakpoints are better.
                p_data['extensibility_score'] * 5
            )
            scored_prodigals.append((score, p_id))

        # Sort by score (highest first) and return as a dictionary
        sorted_prodigals = sorted(scored_prodigals, reverse=True)
        return {prodigals[p_id]["id"]: prodigals[p_id] for score, p_id in sorted_prodigals}

    def load_prodigals(self):
        """Loads prodigal data from the JSON file."""
        try:
            with open(self.prodigal_file, 'r') as f:
                prodigal_data = json.load(f)
                # Convert keys to integers and 'breakpoints' to list of dicts
                loaded_prodigals = {}
                for p_id_str, p_data in prodigal_data.items():
                    p_id = int(p_id_str)
                    loaded_prodigals[p_id] = {
                        'sequence': p_data['sequence'],
                        'length': p_data['length'],
                        'overlap_rate': p_data['overlap_rate'],
                        'n_value': p_data['n_value'],
                        'source': p_data['source'],
                        'breakpoints': [{'position': bp['position'], 'reason': bp['reason'], 'n_values': bp['n_values']}
                                         for bp in p_data.get('breakpoints', [])],  # Ensure 'breakpoints' exists
                        'winner_score': p_data.get('winner_score', 0), # Handle potentially missing
                        'loser_score': p_data.get('loser_score', 0),
                        'extensibility_score': p_data.get('extensibility_score', 0),
                        'parent_prodigals': p_data.get('parent_prodigals', []),
                        'child_prodigals': p_data.get('child_prodigals', []),
                        'used_count': p_data.get('used_count', 0),
                        'id': p_id
                    }
                self.prodigal_results = loaded_prodigals
                self.next_prodigal_id = max(self.prodigal_results.keys(), default=0) + 1 if self.prodigal_results else 0 #Next id
                logging.info(f"Loaded {len(self.prodigal_results)} prodigals from {self.prodigal_file}.")
        except FileNotFoundError:
            logging.info(f"No prodigal data file found: {self.prodigal_file}. Starting with an empty database.")
            self.prodigal_results = {}
            self.next_prodigal_id = 0
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from {self.prodigal_file}.  Check for file corruption.")
            self.prodigal_results = {}
            self.next_prodigal_id = 0

    def save_prodigals(self):
        """Saves the prodigal data to the JSON file."""
        with open(self.prodigal_file, 'w') as f:
            # Convert keys to strings before saving (JSON requires string keys)
            prodigal_results_str_keys = {str(k): v for k, v in self.prodigal_results.items()}
            json.dump(prodigal_results_str_keys, f, indent=4)
        logging.info(f"Saved {len(self.prodigal_results)} prodigals to {self.prodigal_file}.")

    def get_prodigal_by_id(self, prodigal_id):
        """Retrieves a prodigal by its ID."""
        return self.prodigal_results.get(prodigal_id)
    def update_prodigal(self, prodigal_id, new_data):
      """Updates and saves new data to an exisiting prodigal ID"""
      if prodigal_id in self.prodigal_results:
        self.prodigal_results[prodigal_id] = new_data
        return True
      return False