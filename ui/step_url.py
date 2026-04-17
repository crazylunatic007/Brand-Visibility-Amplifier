import streamlit as st
from core.content_parser import fetch_and_parse


def render_step_url():
    st.title("Step 3: Enter Content URL")
    st.write(
        f"Selected **{len(st.session_state.get('selected_queries', []))}** queries. "
        "Now provide the URL of the content you want to optimize."
    )

    url = st.text_input(
        "Content URL",
        value=st.session_state.get("target_url", ""),
        placeholder="https://example.com/your-article",
    )

    if st.button("Fetch & Analyze Content", type="primary"):
        if not url.strip():
            st.error("Please enter a URL.")
            return

        st.session_state["target_url"] = url.strip()

        try:
            with st.spinner("Fetching and parsing content..."):
                parsed = fetch_and_parse(url.strip())
            st.session_state["parsed_content"] = parsed
        except Exception as e:
            st.error(f"Error fetching URL: {e}")
            return

    parsed = st.session_state.get("parsed_content")
    if parsed:
        st.success(f"Content parsed successfully!")
        st.subheader(parsed.title)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sections", len(parsed.sections))
        with col2:
            total_words = sum(s.word_count for s in parsed.sections)
            st.metric("Total Words", total_words)

        with st.expander("Content Structure", expanded=True):
            for section in parsed.sections:
                indent = "&nbsp;" * (section.heading_level - 1) * 4
                st.markdown(
                    f"{indent}**H{section.heading_level}:** {section.heading} "
                    f"*({section.word_count} words)*"
                )

        st.divider()
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("Back to Query Selection"):
                st.session_state["step"] = 2
                st.rerun()
        with col_next:
            if st.button("Proceed to Analysis", type="primary"):
                st.session_state["step"] = 4
                st.rerun()

    else:
        st.divider()
        if st.button("Back to Query Selection"):
            st.session_state["step"] = 2
            st.rerun()
