import streamlit as st
from models.schemas import QueryType
from core.query_validator import validate_queries_with_semrush


QUERY_TYPE_LABELS = {
    QueryType.EQUIVALENT: "Equivalent Queries",
    QueryType.FOLLOW_UP: "Follow-Up Queries",
    QueryType.GENERALIZATION: "Generalization Queries",
    QueryType.SPECIFICATION: "Specification Queries",
    QueryType.CANONICALIZATION: "Canonicalization Queries",
    QueryType.LANGUAGE_TRANSLATION: "Language Translation Queries",
    QueryType.ENTAILMENT: "Entailment Queries",
    QueryType.CLARIFICATION: "Clarification Queries",
}


def render_step_fanout():
    st.title("Step 2: Select Queries")
    st.write(f"Generated queries for: **{st.session_state.get('seed_keyword', '')}**")

    queries = st.session_state.get("generated_queries", [])
    if not queries:
        st.warning("No queries generated. Go back to Step 1.")
        if st.button("Back to Step 1"):
            st.session_state["step"] = 1
            st.rerun()
        return

    # Optional Semrush validation
    semrush_key = st.session_state.get("semrush_api_key")
    if semrush_key and not any(q.semrush_validated for q in queries):
        if st.button("Validate with Semrush"):
            with st.spinner("Validating queries against Semrush..."):
                queries = validate_queries_with_semrush(queries, semrush_key)
                st.session_state["generated_queries"] = queries
            st.rerun()

    # Group queries by type
    grouped: dict[str, list] = {}
    for q in queries:
        label = QUERY_TYPE_LABELS.get(q.query_type, q.query_type.value)
        grouped.setdefault(label, []).append(q)

    # Initialize selection state
    if "query_selections" not in st.session_state:
        st.session_state["query_selections"] = {q.query_text: False for q in queries}

    total_selected = sum(1 for v in st.session_state["query_selections"].values() if v)
    st.metric("Selected Queries", f"{total_selected} / {len(queries)}")

    for group_name, group_queries in grouped.items():
        with st.expander(f"{group_name} ({len(group_queries)} queries)", expanded=True):
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Select All", key=f"sel_all_{group_name}"):
                    for q in group_queries:
                        st.session_state["query_selections"][q.query_text] = True
                    st.rerun()
            with col2:
                if st.button(f"Deselect All", key=f"desel_all_{group_name}"):
                    for q in group_queries:
                        st.session_state["query_selections"][q.query_text] = False
                    st.rerun()

            for q in group_queries:
                col_check, col_info = st.columns([0.05, 0.95])
                with col_check:
                    checked = st.checkbox(
                        "",
                        value=st.session_state["query_selections"].get(q.query_text, False),
                        key=f"cb_{q.query_text}",
                    )
                    st.session_state["query_selections"][q.query_text] = checked
                with col_info:
                    intent_colors = {
                        "informational": ":blue[Informational]",
                        "transactional": ":green[Transactional]",
                        "navigational": ":orange[Navigational]",
                        "commercial_investigation": ":violet[Commercial]",
                    }
                    intent_badge = intent_colors.get(q.intent.value, q.intent.value)

                    metrics_str = ""
                    if q.semrush_validated:
                        vol = q.search_volume if q.search_volume is not None else "N/A"
                        kd = f"{q.keyword_difficulty:.0f}" if q.keyword_difficulty is not None else "N/A"
                        metrics_str = f" | Vol: **{vol}** | KD: **{kd}**"
                    elif semrush_key and not q.semrush_validated:
                        metrics_str = " | :orange[No search data]"

                    st.markdown(f"**{q.query_text}** &nbsp; {intent_badge}{metrics_str}")
                    st.caption(q.rationale)

    st.divider()
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("Back to Step 1"):
            st.session_state["step"] = 1
            st.rerun()
    with col_next:
        if st.button("Continue with Selected Queries", type="primary"):
            selected = [
                q for q in queries
                if st.session_state["query_selections"].get(q.query_text, False)
            ]
            if not selected:
                st.error("Please select at least one query.")
            else:
                for q in selected:
                    q.selected = True
                st.session_state["selected_queries"] = selected
                st.session_state["step"] = 3
                st.rerun()
