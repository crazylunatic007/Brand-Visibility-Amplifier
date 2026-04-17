import streamlit as st
from core.docs_builder import create_recommendations_doc


def render_step_export():
    st.title("Step 5: Export to Google Docs")

    if not st.session_state.get("google_creds"):
        st.warning("Please connect your Google account in the sidebar first.")
        return

    placements = st.session_state.get("placements", [])
    removed = st.session_state.get("removed_placements", set())
    active_placements = [p for i, p in enumerate(placements) if i not in removed]
    parsed = st.session_state.get("parsed_content")

    if not active_placements or not parsed:
        st.error("No placements to export. Go back to the analysis step.")
        if st.button("Back to Analysis"):
            st.session_state["step"] = 4
            st.rerun()
        return

    st.write(f"Ready to export **{len(active_placements)}** query placement recommendations.")

    if st.session_state.get("doc_url"):
        st.success("Google Doc created successfully!")
        st.markdown(f"[Open Google Doc]({st.session_state['doc_url']})")
        st.balloons()
    else:
        if st.button("Create Google Doc", type="primary"):
            try:
                with st.spinner("Creating Google Doc..."):
                    doc_url = create_recommendations_doc(
                        docs_service=st.session_state["docs_service"],
                        drive_service=st.session_state["drive_service"],
                        parsed_content=parsed,
                        placements=active_placements,
                        generated_content=st.session_state.get("generated_content", {}),
                    )
                st.session_state["doc_url"] = doc_url
                st.rerun()
            except Exception as e:
                st.error(f"Error creating document: {e}")

    st.divider()
    if st.button("Start Over"):
        for key in [
            "step", "seed_keyword", "generated_queries", "selected_queries",
            "query_selections", "target_url", "parsed_content", "placements",
            "removed_placements", "doc_url", "generated_content",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state["step"] = 1
        st.rerun()
