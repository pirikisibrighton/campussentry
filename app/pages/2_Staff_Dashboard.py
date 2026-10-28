import sys
import hmac
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from storage import init_db, get_incidents, update_status


# --------------------------------------------------
# PAGE CONFIGURATION AND SHARED STYLING
# --------------------------------------------------

st.set_page_config(
    page_title="CampusSentry | Staff Dashboard",
    page_icon="🛡️",
    layout="wide",
)

CSS_PATH = ROOT / "app" / "style.css"

if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )

init_db()

STATUSES = ["New", "Under Review", "Resolved"]


# --------------------------------------------------
# STAFF AUTHENTICATION
# --------------------------------------------------

def check_credentials(username, password):
    try:
        config = st.secrets["staff"]
        expected_username = str(config["username"])
        expected_password = str(config["password"])
    except (KeyError, FileNotFoundError):
        st.error(
            "Staff credentials are not configured. "
            "Check .streamlit/secrets.toml."
        )
        return False

    return (
        hmac.compare_digest(username, expected_username)
        and hmac.compare_digest(password, expected_password)
    )


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("🛡️ CampusSentry")
st.subheader("Staff Incident Management Dashboard")

st.caption(
    "Monitor campus incident reports, review AI predictions, "
    "and manage incident response status."
)


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

if not st.session_state.get("staff_authenticated", False):
    st.info("Staff login is required to access incident records.")

    with st.form("staff_login_form"):
        username = st.text_input("Staff username")
        password = st.text_input(
            "Staff password",
            type="password",
        )

        login_clicked = st.form_submit_button(
            "Log in",
            type="primary",
            use_container_width=True,
        )

    if login_clicked:
        if check_credentials(username, password):
            st.session_state["staff_authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🛡️ CampusSentry")
    st.caption("Staff control panel")

    st.success("Staff session active")

    if st.button("Log out", use_container_width=True):
        st.session_state["staff_authenticated"] = False
        st.rerun()

    st.divider()

    st.caption("CampusSentry NLP")
    st.caption(
        "AI predictions support triage. "
        "Verify reports before taking action."
    )


# --------------------------------------------------
# LOAD INCIDENT RECORDS
# --------------------------------------------------

incidents = get_incidents()

if not incidents:
    st.info("No incident reports have been submitted yet.")
    st.caption(
        "Incident reports will appear here after they are submitted."
    )
    st.stop()

df = pd.DataFrame(incidents)


# --------------------------------------------------
# SUMMARY METRICS
# These counts use ALL incidents, not filtered results.
# --------------------------------------------------

total = len(df)

new_count = int(
    (df["status"] == "New").sum()
)

review_count = int(
    (df["status"] == "Under Review").sum()
)

resolved_count = int(
    (df["status"] == "Resolved").sum()
)

high_count = int(
    (df["severity"].astype(str).str.casefold() == "high").sum()
)

st.markdown("### Overview")

metric_cols = st.columns(5)

metric_cols[0].metric(
    "Total incidents",
    total,
)

metric_cols[1].metric(
    "New reports",
    new_count,
)

metric_cols[2].metric(
    "Under review",
    review_count,
)

metric_cols[3].metric(
    "Resolved",
    resolved_count,
)

metric_cols[4].metric(
    "High severity",
    high_count,
)


# --------------------------------------------------
# INCIDENT SEARCH AND FILTERS
# --------------------------------------------------

st.divider()
st.subheader("Incident records")

search_text = st.text_input(
    "Search reports",
    placeholder=(
        "Search reference number, report text, or location..."
    ),
)

filter_cols = st.columns(4)

categories = sorted(
    df["category"].dropna().astype(str).unique().tolist()
)

severities = sorted(
    df["severity"].dropna().astype(str).unique().tolist()
)

languages = sorted(
    df["language"].dropna().astype(str).unique().tolist()
)

with filter_cols[0]:
    selected_categories = st.multiselect(
        "Category",
        categories,
    )

with filter_cols[1]:
    selected_severities = st.multiselect(
        "Severity",
        severities,
    )

with filter_cols[2]:
    selected_languages = st.multiselect(
        "Language",
        languages,
    )

with filter_cols[3]:
    selected_statuses = st.multiselect(
        "Status",
        STATUSES,
    )


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered = df.copy()

if selected_categories:
    filtered = filtered[
        filtered["category"].isin(selected_categories)
    ]

if selected_severities:
    filtered = filtered[
        filtered["severity"].isin(selected_severities)
    ]

if selected_languages:
    filtered = filtered[
        filtered["language"].isin(selected_languages)
    ]

if selected_statuses:
    filtered = filtered[
        filtered["status"].isin(selected_statuses)
    ]

if search_text.strip():
    query = search_text.strip().casefold()

    def matches_search(row):
        locations = row.get("location", []) or []

        if not isinstance(locations, (list, tuple)):
            locations = [str(locations)]

        searchable = [
            f"CS-{int(row['id']):05d}",
            str(row.get("report_text", "")),
            str(row.get("category", "")),
            str(row.get("severity", "")),
            str(row.get("language", "")),
            ", ".join(str(item) for item in locations),
        ]

        return any(
            query in value.casefold()
            for value in searchable
        )

    filtered = filtered[
        filtered.apply(matches_search, axis=1)
    ]


# --------------------------------------------------
# INCIDENT TABLE
# --------------------------------------------------

st.caption(
    f"Showing {len(filtered)} of {total} incidents."
)

if filtered.empty:
    st.warning("No incidents match the selected filters.")

else:
    table_rows = []

    for _, row in filtered.iterrows():
        locations = row.get("location", []) or []

        if not isinstance(locations, (list, tuple)):
            locations = [str(locations)]

        table_rows.append(
            {
                "Reference": f"CS-{int(row['id']):05d}",
                "Submitted (UTC)": str(row["created_at"]),
                "Category": row["category"],
                "Severity": row["severity"],
                "Language": row["language"],
                "Location": (
                    ", ".join(str(item) for item in locations)
                    if locations
                    else "Not identified"
                ),
                "Status": row["status"],
            }
        )

    table_df = pd.DataFrame(table_rows)

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=min(450, 100 + len(table_df) * 40),
    )

    # --------------------------------------------------
    # REVIEW AND UPDATE INCIDENTS
    # --------------------------------------------------

    st.divider()
    st.subheader("Review and update incidents")

    for _, row in filtered.iterrows():
        incident_id = int(row["id"])
        reference = f"CS-{incident_id:05d}"

        with st.expander(
            f"{reference} | {row['category']} | "
            f"{row['severity']} severity | {row['status']}"
        ):
            st.markdown("**Original report**")
            st.write(row["report_text"])

            detail_cols = st.columns(3)

            detail_cols[0].write(
                f"**Category:** {row['category']}"
            )

            detail_cols[1].write(
                f"**Severity:** {row['severity']}"
            )

            detail_cols[2].write(
                f"**Language:** {row['language']}"
            )

            locations = row.get("location", []) or []

            if not isinstance(locations, (list, tuple)):
                locations = [str(locations)]

            st.write(
                "**Identified locations:** "
                + (
                    ", ".join(str(item) for item in locations)
                    if locations
                    else "None identified"
                )
            )

            entities = row.get("entities", []) or []

            if entities:
                st.markdown("**Extracted entities**")

                st.dataframe(
                    pd.DataFrame(entities),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.caption(
                    "No entities were extracted for this report."
                )

            st.caption(
                f"Submitted at: {row['created_at']} (UTC)"
            )

            current_status = row["status"]

            status_index = (
                STATUSES.index(current_status)
                if current_status in STATUSES
                else 0
            )

            with st.form(f"status_form_{incident_id}"):
                new_status = st.selectbox(
                    "Incident status",
                    STATUSES,
                    index=status_index,
                    key=f"status_select_{incident_id}",
                )

                save_clicked = st.form_submit_button(
                    "Save status",
                    type="primary",
                )

            if save_clicked:
                try:
                    update_status(incident_id, new_status)

                    st.success(
                        f"{reference} status updated to {new_status}."
                    )

                    st.rerun()

                except Exception:
                    st.error(
                        "Could not update the incident status. "
                        "Try again."
                    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI predictions support incident triage and may be incorrect. "
    "Staff must verify the report and determine the appropriate "
    "response. For immediate emergencies, follow campus "
    "emergency procedures."
)