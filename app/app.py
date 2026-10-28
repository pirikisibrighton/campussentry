import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from pipeline import analyze
from storage import init_db, save_incident

st.set_page_config(
    page_title="CampusSentry | Report an Incident",
    page_icon="🛡️",
    layout="centered",
)

init_db()

st.title("🛡️ CampusSentry")
st.subheader("Campus Incident Reporting")
st.write(
    "Report a campus incident in English, Shona, or mixed language. "
    "Your report will be analysed to help authorised campus staff review it."
)

st.info("You do not need to log in to submit an incident report.")

with st.form("incident_report_form", clear_on_submit=True):
    report_text = st.text_area(
        "Describe the incident",
        placeholder=(
            "Example: There is a burst pipe near the library server room.\n"
            "Example: Moto uri kubuda pa library."
        ),
        height=180,
        max_chars=5000,
    )

    submitted = st.form_submit_button(
        "Analyse and Submit Report",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not report_text.strip():
        st.error("Please describe the incident before submitting.")
    else:
        try:
            with st.spinner("Analysing and saving your report..."):
                analysis = analyze(report_text.strip())
                incident_id = save_incident(report_text.strip(), analysis)

            st.success(
                f"Your report was submitted successfully. "
                f"Reference number: CS-{incident_id:05d}"
            )
            st.write(
                "Authorised campus staff can review your report "
                "on the incident management dashboard."
            )

        except Exception:
            st.error(
                "We could not process your report. Please try again later."
            )
            st.exception(Exception("Check the terminal for the underlying error."))

st.divider()
st.caption(
    "CampusSentry NLP supports incident triage. "
    "AI predictions may be incorrect and must be verified by authorised staff. "
    "For an immediate emergency, contact campus security directly."
)
