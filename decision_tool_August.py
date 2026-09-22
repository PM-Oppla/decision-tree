# ============================================================
# Interactive biodiversity decision engine (Q1 → Q2 → Q3)
# Numbered options to avoid typos
# Q1 imposes a hard cap on all allowed methods downstream
# Methods: QA, IO, LCA, NCA for BF, NCA for ES
# ============================================================

from typing import Dict, Set, List, Tuple
from collections import Counter


# -----------------------------
# 1. Define method sets
# -----------------------------
Q1_methods: Dict[str, Set[str]] = {
    "Starting": {"QA"},
    "First steps": {"QA", "IO"},
    "Developing": {"QA", "IO", "LCA"},
    "Maturing": {"IO", "LCA", "NCA for BF", "NCA for ES"},
    "Comprehensive": {"IO", "LCA", "NCA for BF", "NCA for ES"},
}

Q2_methods: Dict[str, Set[str]] = {
    "Screening": {"QA", "IO"},
    "Comparing options": {"LCA"},
    "Tracking change in pressures/reliance": { "IO", "LCA"},
    "Observing change in biodiversity": {"NCA for BF","NCA for ES"},
    "ES (dependency) assessment": {"NCA for ES"},
    "Reporting / Disclosure": {"QA","IO", "LCA", "NCA for BF", "NCA for ES"},
    "Target setting / Performance monitoring": {"LCA", "NCA for BF", "NCA for ES"},
}

Q3_methods: Dict[str, Set[str]] = {
    "Whole organization": {"QA","IO", "LCA", "NCA for BF", "NCA for ES"},
    "Operations": {"LCA (limited)", "NCA for BF", "NCA for ES"},
    "Value chain": {"QA", "IO", "LCA"},
    "Portfolio": {"QA","IO"},
    "Products / services": {"LCA", "NCA for BF"},
    "Landscapes": {"QA", "NCA for BF", "NCA for ES"},
}



# -----------------------------
# Hard cap setting: Q1 restricts everything after it
# -----------------------------
HARD_CAP_BY_Q1 = True


# -----------------------------
# Utility functions
# -----------------------------
def validate_method_sets(*question_maps: Dict[str, Set[str]]) -> None:
    """Ensure all method definitions have valid types."""
    for qmap in question_maps:
        if not isinstance(qmap, dict):
            raise TypeError("Each question map must be a dictionary.")
        for key, val in qmap.items():
            if not isinstance(key, str):
                raise TypeError("Keys must be strings.")
            if not isinstance(val, set):
                raise TypeError("Values must be sets.")
            for m in val:
                if not isinstance(m, str):
                    raise TypeError("Methods must be strings.")


def union_methods(selected: List[str], mapping: Dict[str, Set[str]]) -> Set[str]:
    """Union of methods for selected labels."""
    methods = set()
    for key in selected:
        methods |= mapping[key]
    return methods


def cap_with_union(current: Set[str], selected: List[str], mapping: Dict[str, Set[str]]) -> Set[str]:
    """Intersect current allowed methods with methods from new selection."""
    if not selected:
        return current
    return current & union_methods(selected, mapping)


def filter_by_overlap(allowed: Set[str], options: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """Return only options where allowed ∩ option_methods ≠ ∅."""
    return {k: v for k, v in options.items() if not v.isdisjoint(allowed)}


def explain_filtering(allowed: Set[str], options: Dict[str, Set[str]], title: str) -> None:
    """Print keep/drop for transparency."""
    print(f"\n--- {title} ---")
    print("Allowed methods:", sorted(allowed))
    for k, v in options.items():
        overlap = sorted(v & allowed)
        if overlap:
            print(f" ✔ KEEP: {k:45s} {sorted(v)} (overlap={overlap})")
        else:
            print(f" ✘ DROP: {k:45s} {sorted(v)} (no overlap)")


# -----------------------------
# Numbered selection system
# -----------------------------
def prompt_select(question: str, mapping: Dict[str, Set[str]], allowed_keys=None) -> List[str]:
    """
    Displays numbered options and returns list of labels (strings).
    Prevents typos by having users type numbers only.
    """
    print(f"\n{question}")
    print("-" * len(question))

    # Determine selectable keys
    keys = allowed_keys if allowed_keys is not None else list(mapping.keys())
    keys = list(keys)

    if not keys:
        print("No available options.")
        return []

    # Number the options
    index_to_label = {}
    print("Options:")
    for i, label in enumerate(keys, start=1):
        index_to_label[i] = label
        print(f"  {i}. {label}  -> methods: {sorted(mapping[label])}")

    # Ask user for input
    while True:
        raw = input("Select options by number (comma-separated) or Enter to skip: ").strip()
        if not raw:
            return []

        try:
            chosen_numbers = [int(x.strip()) for x in raw.split(",") if x.strip()]
        except ValueError:
            print("Invalid input — please enter numbers like: 1,2")
            continue

        invalid = [n for n in chosen_numbers if n not in index_to_label]
        if invalid:
            print(f"Invalid numbers: {invalid}. Please choose from 1–{len(keys)}.")
            continue

        # Convert numbers → labels
        seen = set()
        selected_labels = []
        for n in chosen_numbers:
            lab = index_to_label[n]
            if lab not in seen:
                seen.add(lab)
                selected_labels.append(lab)

        return selected_labels


# -----------------------------
# Final recommendation logic
# -----------------------------
def recommend_methods(selected_Q1, selected_Q2, selected_Q3):
    """Strict intersection; fallback frequency ranking."""
    all_sets = []
    for k in selected_Q1: all_sets.append(Q1_methods[k])
    for k in selected_Q2: all_sets.append(Q2_methods[k])
    for k in selected_Q3: all_sets.append(Q3_methods[k])
    

    strict = set.intersection(*all_sets) if all_sets else set()

    freq = Counter()
    for s in all_sets:
        for m in s:
            freq[m] += 1

    ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))

    return strict, ranked


# -----------------------------
# Interactive Engine
# -----------------------------
if __name__ == "__main__":
    validate_method_sets(Q1_methods, Q2_methods, Q3_methods)

    # === Q1 ===
    selected_Q1 = []
    while not selected_Q1:
        selected_Q1 = prompt_select(
            "How far are you in your biodiversity mainstreaming journey?",
            Q1_methods
        )
        if not selected_Q1:
            print("You must select at least one option in Q1.")

    allowed_after_Q1 = union_methods(selected_Q1, Q1_methods)
    cap_Q1 = set(allowed_after_Q1)

    # === Q2 ===
    filtered_Q2 = filter_by_overlap(cap_Q1, Q2_methods)
    explain_filtering(cap_Q1, Q2_methods, "Filtering Q2 based on Q1")

    selected_Q2 = prompt_select(
        "What is your overall purpose?",
        Q2_methods,
        allowed_keys=list(filtered_Q2.keys())
    )

    allowed_after_Q2 = cap_with_union(allowed_after_Q1, selected_Q2, Q2_methods)

    # === Q3 ===
    filtered_Q3 = filter_by_overlap(allowed_after_Q2, Q3_methods)
    explain_filtering(allowed_after_Q2, Q3_methods, "Filtering Q3 based on Q1 + Q2")

    selected_Q3 = prompt_select(
        "What aspects of your organization do you want to focus on?",
        Q3_methods,
        allowed_keys=list(filtered_Q3.keys())
    )

    allowed_after_Q3 = cap_with_union(allowed_after_Q2, selected_Q3, Q3_methods)

   

    # === Final Recommendation ===
    strict, ranked = recommend_methods(selected_Q1, selected_Q2, selected_Q3)

    print("\n===== FINAL RECOMMENDATION =====")
    if strict:
        print("Strict method recommendation:", sorted(strict))
    else:
        best_score = ranked[0][1]
        best = [m for m, s in ranked if s == best_score and m in cap_Q1]
        print("No strict match. Best candidates:", best)
        print("Ranking:", ranked)

    print("\n===== END =====")
