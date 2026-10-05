import streamlit as st
from collections import Counter
from pathlib import Path

# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------

st.set_page_config(
    page_title="CircHive Biodiversity Decision Tool",
    page_icon="🌿",
    layout="centered"
)

# ------------------------------------------------------------
# CircHive branding
# ------------------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        max-width: 850px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        color: #575756;
    }

    h1 {
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    h2 {
        margin-top: 2rem;
    }

    p {
        line-height: 1.55;
    }

    .circhive-intro {
        border-left: 5px solid #ec6608;
        background: #fafafa;
        padding: 18px 22px;
        margin: 20px 0 32px 0;
        border-radius: 0 8px 8px 0;
    }

    .circhive-intro p {
        margin: 0;
        color: #575756;
    }

    .circhive-divider {
        height: 5px;
        width: 100%;
        margin: 20px 0 30px 0;
        border-radius: 4px;
        background: linear-gradient(
            90deg,
            #f9b000 0%,
            #ec6608 40%,
            #e6332a 70%,
            #e5006d 100%
        );
    }

    div.stButton > button[kind="primary"] {
        background: #ec6608;
        border: 1px solid #ec6608;
        color: white;
        font-weight: 600;
        border-radius: 7px;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #e6332a;
        border-color: #e6332a;
        color: white;
    }

    .funding-heading {
        margin-top: 35px;
        margin-bottom: 12px;
        color: #575756;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# Branding assets
# ------------------------------------------------------------

logo_path = Path("assets/circhive-logo.png")
partners_path = Path("assets/circhive-partners-funders.png")

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

if logo_path.exists():
    st.image(str(logo_path), width=300)
else:
    st.markdown("## CircHive")

st.title("Biodiversity Decision Tool")

st.write(
    "Find an assessment approach suited to your organisation, "
    "purpose and area of focus."
)

st.markdown(
    """
    <div class="circhive-intro">
        <p>
        This tool helps organisations explore biodiversity assessment
        approaches based on where they are in their biodiversity journey
        and what they want to achieve.
        </p>
    </div>

    <div class="circhive-divider"></div>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# Decision logic
# ------------------------------------------------------------

Q1_methods = {
    "Starting": {
        "Qualitative Assessment"
    },
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

# IMPORTANT:
# "Operations" now uses Life Cycle Assessment rather than
# "Life Cycle Assessment (limited)" so that it correctly overlaps
# with LCA selections from Questions 1 and 2.
#
# "Landscapes" does not use Qualitative Assessment. This prevents
# Landscapes appearing in QA-only routes such as Starting and
# Developing > Screening.

Q3_methods = {
    "Whole organization": {
        "Qualitative Assessment",
        "Input Output",
        "Life Cycle Assessment",
        "Natural Capital Accounting for Biodiversity Footprinting",
        "Natural Capital Accounting for Ecosystem Services"
    },
    "Operations": {
        "Life Cycle Assessment",
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
    options=list(Q1_methods.keys()),
    index=None,
    placeholder="Select an option"
)

# ------------------------------------------------------------
# Progressive questions
# ------------------------------------------------------------

selected_q2 = None
selected_q3 = None

if selected_q1 is not None:

    allowed_after_q1 = Q1_methods[selected_q1]

    filtered_q2 = filter_by_overlap(
        allowed_after_q1,
        Q2_methods
    )

    st.header("2. Purpose")

    selected_q2 = st.selectbox(
        "What is your overall purpose?",
        options=list(filtered_q2.keys()),
        index=None,
        placeholder="Select an option"
    )

    if selected_q2 is not None:

        allowed_after_q2 = (
            allowed_after_q1
            & Q2_methods[selected_q2]
        )

        filtered_q3 = filter_by_overlap(
            allowed_after_q2,
            Q3_methods
        )

        st.header("3. Organisational focus")

        selected_q3 = st.selectbox(
            "What aspect of your organisation do you want to focus on?",
            options=list(filtered_q3.keys()),
            index=None,
            placeholder="Select an option"
        )

        # ----------------------------------------------------
        # Recommendation
        # ----------------------------------------------------

        if selected_q3 is not None:

            if st.button(
                "Show recommendation",
                type="primary"
            ):

                strict, ranked = recommend_methods(
                    selected_q1,
                    selected_q2,
                    selected_q3
                )

                st.markdown("---")
                st.header("Your suggested approach")

                if strict:

                    st.success("Recommended method")

                    for method in sorted(strict):
                        st.subheader(method)

                    st.caption(
                        "Based on your answers to the three questions above."
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

                        st.info("Best candidate method")

                        for method in best:
                            st.subheader(method)

                        st.caption(
                            "No single method matches all three criteria "
                            "exactly. These are the closest matches based "
                            "on your answers."
                        )

                    else:
                        st.warning(
                            "No method matches the selected criteria."
                        )

                else:
                    st.warning(
                        "No recommendation could be generated."
                    )

# ------------------------------------------------------------
# About this tool
# ------------------------------------------------------------

st.markdown("---")

with st.expander("About this tool"):
    st.write(
        "This decision tool helps users explore biodiversity "
        "assessment methods based on their organisational context, "
        "purpose and area of focus."
    )

# ------------------------------------------------------------
# CircHive footer
# ------------------------------------------------------------

st.header("About CircHive")

st.write(
    "CircHive supports businesses and public sector organisations "
    "in recognising, measuring and reporting on their impacts on nature."
)

st.link_button(
    "Visit the CircHive website →",
    "https://circhive.eu/"
)

# ------------------------------------------------------------
# Partners and funders
# ------------------------------------------------------------

st.markdown(
    '<div class="funding-heading">CircHive partners and funders</div>',
    unsafe_allow_html=True
)

if partners_path.exists():
    st.image(
        str(partners_path),
        use_container_width=True
    )
else:
    st.caption(
        "CircHive partner and funder graphic will appear here."
    )
