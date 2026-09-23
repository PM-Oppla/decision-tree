import streamlit as st
from collections import Counter

# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------

st.set_page_config(
    page_title="Biodiversity Decision Tool",
    page_icon="🌿",
    layout="centered"
)

st.title("Biodiversity Decision Tool")

st.write(
    "Answer the questions below to identify biodiversity assessment "
    "methods that may be appropriate for your organisation."
)

# ------------------------------------------------------------
# Decision logic
# ------------------------------------------------------------

Q1_methods = {
    "Starting": {"QA"},
    "First steps": {"QA", "IO"},
    "Developing": {"QA", "IO", "LCA"},
    "Maturing": {"IO", "LCA", "NCA for BF", "NCA for ES"},
    "Comprehensive": {"IO", "LCA", "NCA for BF", "NCA for ES"},
}

Q2_methods = {
    "Screening": {"QA", "IO"},
    "Comparing options": {"LCA"},
    "Tracking change in pressures/reliance": {"IO", "LCA"},
    "Observing change in biodiversity": {"NCA for BF", "NCA for ES"},
    "ES (dependency) assessment": {"NCA for ES"},
    "Reporting / Disclosure": {
        "QA", "IO", "LCA", "NCA for BF", "NCA for ES"
    },
    "Target setting / Performance monitoring": {
        "LCA", "NCA for BF", "NCA for ES"
    },
}

Q3_methods = {
    "Whole organization": {"QA", "IO", "LCA", "NCA for BF", "NCA for ES"},
    "Operations": {"LCA (limited)", "NCA for BF", "NCA for ES"},
    "Value chain": {"QA", "IO", "LCA"},
    "Portfolio": {"QA", "IO"},
    "Products / services": {"LCA", "NCA for BF"},
    "Landscapes": {"QA", "NCA for BF", "NCA for ES"},
}


def union_methods(selected, mapping):
    methods = set()
    for key in selected:
        methods |= mapping[key]
    return methods


def filter_by_overlap(allowed, options):
    return {
        key: value
        for key, value in options.items()
        if not value.isdisjoint(allowed)
    }


def recommend_methods(selected_q1, selected_q2, selected_q3):
    all_sets = []

    for key in selected_q1:
        all_sets.append(Q1_methods[key])

    for key in selected_q2:
        all_sets.append(Q2_methods[key])

    for key in selected_q3:
        all_sets.append(Q3_methods[key])

    strict = set.intersection(*all_sets) if all_sets else set()

    freq = Counter()

    for method_set in all_sets:
        for method in method_set:
            freq[method] += 1

    ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))

    return strict, ranked


# ------------------------------------------------------------
# Question 1
# ------------------------------------------------------------

st.header("1. Biodiversity mainstreaming")

selected_q1 = st.multiselect(
    "How far are you in your biodiversity mainstreaming journey?",
    options=list(Q1_methods.keys()),
    placeholder="Select one or more options"
)

if not selected_q1:
    st.info("Select at least one option above to continue.")
    st.stop()

allowed_after_q1 = union_methods(selected_q1, Q1_methods)


# ------------------------------------------------------------
# Question 2
# ------------------------------------------------------------

st.header("2. Purpose")

filtered_q2 = filter_by_overlap(allowed_after_q1, Q2_methods)

selected_q2 = st.multiselect(
    "What is your overall purpose?",
    options=list(filtered_q2.keys()),
    placeholder="Select one or more options"
)

if selected_q2:
    allowed_after_q2 = allowed_after_q1 & union_methods(
        selected_q2, Q2_methods
    )
else:
    allowed_after_q2 = allowed_after_q1


# ------------------------------------------------------------
# Question 3
# ------------------------------------------------------------

st.header("3. Organisational focus")

filtered_q3 = filter_by_overlap(allowed_after_q2, Q3_methods)

selected_q3 = st.multiselect(
    "What aspects of your organisation do you want to focus on?",
    options=list(filtered_q3.keys()),
    placeholder="Select one or more options"
)


# ------------------------------------------------------------
# Recommendation
# ------------------------------------------------------------

if st.button("Show recommendation", type="primary"):

    strict, ranked = recommend_methods(
        selected_q1,
        selected_q2,
        selected_q3
    )

    st.divider()
    st.header("Recommendation")

    if strict:

        st.success(
            "Recommended method(s): "
            + ", ".join(sorted(strict))
        )

    elif ranked:

        best_score = ranked[0][1]

        best = [
            method
            for method, score in ranked
            if score == best_score and method in allowed_after_q1
        ]

        if best:
            st.success(
                "Best candidate method(s): "
                + ", ".join(best)
            )
        else:
            st.warning(
                "No method matches all of the selected criteria."
            )

    else:
        st.warning(
            "Please make selections before requesting a recommendation."
        )


# ------------------------------------------------------------
# About
# ------------------------------------------------------------

st.divider()

with st.expander("About this tool"):
    st.write(
        "This prototype decision tool helps users explore biodiversity "
        "assessment methods based on their organisational context, "
        "purpose and area of focus."
    )
