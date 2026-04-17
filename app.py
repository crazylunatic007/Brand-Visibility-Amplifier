import streamlit as st

st.set_page_config(
    page_title="Query Fan-Out Tool",
    page_icon=":mag:",
    layout="wide",
)

# Initialize session state defaults
defaults = {
    "step": 1,
    "gemini_model": None,
    "gemini_api_key": None,
    "semrush_api_key": None,
    "seed_keyword": "",
    "industry": "General",
    "generated_queries": [],
    "selected_queries": [],
    "target_url": "",
    "parsed_content": None,
    "placements": [],
    "removed_placements": set(),
    "doc_url": None,
    "google_creds": None,
    "brand_profile": None,
    "brand_raw_text": None,
    "docs_service": None,
    "drive_service": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

from ui.sidebar import render_sidebar
from ui.step_keyword import render_step_keyword
from ui.step_fanout import render_step_fanout
from ui.step_url import render_step_url
from ui.step_analysis import render_step_analysis
from ui.step_export import render_step_export

render_sidebar()

step = st.session_state["step"]
if step == 1:
    render_step_keyword()
elif step == 2:
    render_step_fanout()
elif step == 3:
    render_step_url()
elif step == 4:
    render_step_analysis()
elif step == 5:
    render_step_export()
