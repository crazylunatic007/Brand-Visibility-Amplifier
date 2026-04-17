import streamlit as st
from core.content_analyzer import map_queries_to_content, generate_content_for_placements


def render_step_analysis():
    st.title("Step 4: Review Query Placements")

    parsed = st.session_state.get("parsed_content")
    selected = st.session_state.get("selected_queries", [])
    model = st.session_state.get("gemini_model")

    if not parsed or not selected or not model:
        st.error("Missing data. Please go back to previous steps.")
        if st.button("Start Over"):
            st.session_state["step"] = 1
            st.rerun()
        return

    # Generate placements if not already done
    if not st.session_state.get("placements"):
        try:
            with st.spinner("Analyzing content and mapping queries..."):
                placements = map_queries_to_content(model, selected, parsed)
            st.session_state["placements"] = placements
        except Exception as e:
            st.error(f"Error analyzing content: {e}")
            return

    placements = st.session_state["placements"]

    if not placements:
        st.warning("No placements could be determined.")
        if st.button("Back to URL Input"):
            st.session_state["step"] = 3
            st.rerun()
        return

    # Generate full content for placements if not already done
    if not st.session_state.get("generated_content"):
        try:
            with st.spinner("Generating full content for each placement... This may take a minute."):
                generated = generate_content_for_placements(
                    model, placements, parsed,
                    brand_profile=st.session_state.get("brand_profile"),
                )
            st.session_state["generated_content"] = generated
        except Exception as e:
            st.error(f"Error generating content: {e}")
            return

    generated_content = st.session_state.get("generated_content", {})

    st.write(f"Found **{len(placements)}** query placements across **{parsed.title}**")

    # Two-column layout
    col_outline, col_placements = st.columns([1, 2])

    with col_outline:
        st.subheader("Content Outline")
        for section in parsed.sections:
            indent = "&nbsp;" * (section.heading_level - 1) * 4
            count = sum(1 for p in placements if p.target_section.section_index == section.section_index)
            badge = f" :red[+{count}]" if count > 0 else ""
            st.markdown(
                f"{indent}**H{section.heading_level}:** {section.heading}{badge}"
            )

    with col_placements:
        st.subheader("Placement Recommendations")

        if "removed_placements" not in st.session_state:
            st.session_state["removed_placements"] = set()

        for i, p in enumerate(placements):
            if i in st.session_state["removed_placements"]:
                continue

            placement_label = p.placement_type.replace("_", " ").title()

            with st.container(border=True):
                header_col, remove_col = st.columns([0.85, 0.15])
                with header_col:
                    st.markdown(f"**{p.query.query_text}**")
                with remove_col:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state["removed_placements"].add(i)
                        st.rerun()

                st.markdown(
                    f":dart: **Section:** {p.target_section.heading} &nbsp; | &nbsp; "
                    f":wrench: **Type:** {placement_label}"
                )
                if p.suggested_heading:
                    st.markdown(f":bookmark: **Suggested Heading:** {p.suggested_heading}")
                st.markdown(f"**Content Brief:** {p.content_brief}")

                # Show generated content
                content = generated_content.get(p.query.query_text, "")
                if content:
                    with st.expander("Generated Content", expanded=False):
                        st.markdown(content)

                with st.expander("Reasoning"):
                    st.write(p.reasoning)

    active_count = len(placements) - len(st.session_state.get("removed_placements", set()))
    st.divider()
    st.write(f"**{active_count}** placements will be exported.")

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("Back to URL Input"):
            st.session_state["placements"] = []
            st.session_state["removed_placements"] = set()
            st.session_state["generated_content"] = {}
            st.session_state["step"] = 3
            st.rerun()
    with col_next:
        if st.button("Export to Google Docs", type="primary"):
            st.session_state["step"] = 5
            st.rerun()
