import streamlit as st
from core.query_fanout import generate_query_fanout
from core.query_uploader import parse_uploaded_queries


def render_step_keyword():
    st.title("Step 1: Enter Your Seed Keyword")
    st.write("Enter a keyword or topic to generate a comprehensive query fan-out.")

    keyword = st.text_input(
        "Seed Keyword",
        value=st.session_state.get("seed_keyword", ""),
        placeholder="e.g., content marketing strategy",
    )

    industry = st.selectbox(
        "Industry / Niche (optional, helps Gemini generate more relevant queries)",
        ["General", "SaaS", "eCommerce", "Health & Wellness", "Finance", "Education", "Technology", "Marketing", "Real Estate", "Travel"],
        index=0,
    )

    st.divider()

    # Query source selection
    query_source = st.radio(
        "How would you like to get your queries?",
        ["Generate with Gemini", "Upload my own queries", "Both (generate + upload & merge)"],
        index=0,
        key="query_source_radio",
    )

    # File uploader (shown for Upload and Both options)
    uploaded_file = None
    if query_source in ["Upload my own queries", "Both (generate + upload & merge)"]:
        st.markdown("**Upload your queries file:**")
        uploaded_file = st.file_uploader(
            "Supported formats: CSV, TXT, XLSX",
            type=["csv", "txt", "xlsx"],
            key="query_file_upload",
        )
        with st.expander("File format guide"):
            st.markdown("""
**TXT:** One query per line
```
best content marketing tools
how to measure content ROI
content marketing vs paid ads
```

**CSV:** Column header `query` or `query_text` (required). Optional columns: `intent`, `query_type`, `rationale`
```
query,intent,query_type
best content marketing tools,commercial_investigation,specification
how to measure content ROI,informational,follow_up
```

**XLSX:** Same columns as CSV, in an Excel spreadsheet.

If no headers are found, the tool treats the first column as query text.
            """)

    st.divider()

    # Action button
    button_label = {
        "Generate with Gemini": "Generate Query Fan-Out",
        "Upload my own queries": "Upload & Continue",
        "Both (generate + upload & merge)": "Generate & Merge with Upload",
    }[query_source]

    can_proceed = True
    if query_source == "Generate with Gemini" and not st.session_state.get("gemini_model"):
        can_proceed = False
    elif query_source == "Upload my own queries" and not uploaded_file:
        can_proceed = False
    elif query_source == "Both (generate + upload & merge)":
        if not st.session_state.get("gemini_model") or not uploaded_file:
            can_proceed = False

    if st.button(button_label, type="primary", disabled=not can_proceed):
        if query_source in ["Generate with Gemini", "Both (generate + upload & merge)"] and not keyword.strip():
            st.error("Please enter a keyword for Gemini generation.")
            return

        st.session_state["seed_keyword"] = keyword.strip()
        st.session_state["industry"] = industry

        all_queries = []

        # Generate with Gemini
        if query_source in ["Generate with Gemini", "Both (generate + upload & merge)"]:
            try:
                with st.spinner("Generating query fan-out with Gemini..."):
                    gemini_queries = generate_query_fanout(
                        st.session_state["gemini_model"],
                        f"{keyword.strip()} (industry: {industry})" if industry != "General" else keyword.strip(),
                    )
                all_queries.extend(gemini_queries)
            except Exception as e:
                st.error(f"Error generating queries: {e}")
                return

        # Upload queries
        if query_source in ["Upload my own queries", "Both (generate + upload & merge)"]:
            try:
                with st.spinner("Parsing uploaded queries..."):
                    uploaded_queries = parse_uploaded_queries(uploaded_file)
                if not uploaded_queries:
                    st.error("No queries found in the uploaded file.")
                    return
                st.success(f"Parsed {len(uploaded_queries)} queries from file.")
                all_queries.extend(uploaded_queries)
            except Exception as e:
                st.error(f"Error parsing file: {e}")
                return

        # Deduplicate by query_text (keep first occurrence)
        seen = set()
        deduped = []
        for q in all_queries:
            if q.query_text.lower() not in seen:
                seen.add(q.query_text.lower())
                deduped.append(q)

        st.session_state["generated_queries"] = deduped
        st.session_state["query_selections"] = {}  # Reset selections
        st.session_state["step"] = 2
        st.rerun()

    # Help messages
    if not st.session_state.get("gemini_model") and query_source != "Upload my own queries":
        st.info("Enter your Gemini API key in the sidebar to generate queries.")
    if query_source in ["Upload my own queries", "Both (generate + upload & merge)"] and not uploaded_file:
        st.info("Upload a file to continue.")
