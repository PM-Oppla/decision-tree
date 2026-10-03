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
    "Starting": {"Qualitative Assessment"},
    "First steps": {
        "Qualitative Assessment",
        "Input Output"
    },
    "Developing": {
        "Qualitative Assessment",
        "Input Output",
        "Life Cycle Assessment"
    },
    "Maturing": {
        "Input Output",
        "Life Cycle Assessment",
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
    "Comprehensive": {
        "Input Output",
        "Life Cycle Assessment",
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
}

Q2_methods = {
    "Screening": {
        "Qualitative Assessment",
        "Input Output"
    },
    "Comparing options": {
        "Life Cycle Assessment"
    },
    "Tracking change in pressures/reliance": {
        "Input Output",
        "Life Cycle Assessment"
    },
    "Observing change in biodiversity": {
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
    "Ecosystem Services (dependency) assessment": {
        "Natural Capital Accounting for Ecosystem Services"
    },
    "Reporting / Disclosure": {
        "Qualitative Assessment",
        "Input Output",
        "Life Cycle Assessment",
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
    "Target setting / Performance monitoring": {
        "Life Cycle Assessment",
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
}

Q3_methods = {
    "Whole organization": {
        "Qualitative Assessment",
        "Input Output",
        "Life Cycle Assessment",
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
    "Operations": {
        "Life Cycle Assessment (limited)",
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
    "Value chain": {
        "Qualitative Assessment",
        "Input Output",
        "Life Cycle Assessment"
    },
    "Portfolio": {
        "Qualitative Assessment",
        "Input Output"
    },
    "Products / services": {
        "Life Cycle Assessment",
        "Natural Capital Accounting for Biodiversity Footprinting"
    },
    "Landscapes": {
        "Qualitative Assessment",
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
}


def filter_by_overlap(allowed, options):
    return {
        key: value
        for key, value in options.items()
        if not value.isdisjoint(allowed)
    }


def recommend_methods(selected_q1, selected_q2, selected_q3):
    all_sets = [
        Q1_methods[selected_q1],
        Q2_methods[selected_q2],
        Q3_methods[selected_q3]
    ]

    strict = set.intersection(*all_sets)

    freq = Counter()

    for method_set in all_sets:
        for method in method_set:
            freq[method] += 1

    ranked = sorted(
        freq.items(),
        key=lambda x: (-x[1], x[0])
    )

    return strict, ranked


# ------------------------------------------------------------
# Question 1
# ------------------------------------------------------------

st.header("1. Biodiversity mainstreaming")

selected_q1 = st.selectbox(
    "How far are you in your biodiversity mainstreaming journey?",
    options=[None] + list(Q1_methods.keys()),
    index=0,
    placeholder="Select one option"
)

if selected_q1 is None:
    st.info("Select an option above to continue.")
    st.stop()

allowed_after_q1 = Q1_methods[selected_q1]


# ------------------------------------------------------------
# Question 2
# ------------------------------------------------------------

st.header("2. Purpose")

filtered_q2 = filter_by_overlap(
    allowed_after_q1,
    Q2_methods
)

selected_q2 = st.selectbox(
    "What is your overall purpose?",
    options=[None] + list(filtered_q2.keys()),
    index=0,
    placeholder="Select one option"
)

if selected_q2 is None:
    st.info("Select an option above to continue.")
    st.stop()

allowed_after_q2 = (
    allowed_after_q1 & Q2_methods[selected_q2]
)


# ------------------------------------------------------------
# Question 3
# ------------------------------------------------------------

st.header("3. Organisational focus")

filtered_q3 = filter_by_overlap(
    allowed_after_q2,
    Q3_methods
)

selected_q3 = st.selectbox(
    "What aspect of your organisation do you want to focus on?",
    options=[None] + list(filtered_q3.keys()),
    index=0,
    placeholder="Select one option"
)

if selected_q3 is None:
    st.info("Select an option above to continue.")
    st.stop()


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
            if score == best_score
            and method in allowed_after_q1
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
            "No method matches the selected criteria."
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
