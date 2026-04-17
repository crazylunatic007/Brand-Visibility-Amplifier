import streamlit as st
from auth.gemini_auth import init_gemini
from auth.google_oauth import get_google_credentials, get_docs_service, get_drive_service
from core.brand_parser import extract_text_from_file, generate_brand_profile


def render_sidebar():
    with st.sidebar:
        st.header("Settings")

        # Progress indicator
        step = st.session_state.get("step", 1)
        steps = ["Keyword", "Select Queries", "URL", "Analysis", "Export"]
        for i, name in enumerate(steps, 1):
            if i < step:
                st.markdown(f"~~:white_check_mark: Step {i}: {name}~~")
            elif i == step:
                st.markdown(f"**:arrow_right: Step {i}: {name}**")
            else:
                st.markdown(f":white_circle: Step {i}: {name}")

        st.divider()

        # Gemini API Key
        st.subheader("Gemini API Key")
        api_key = st.text_input("Enter your Gemini API key", type="password", key="gemini_key_input")
        if st.button("Validate Gemini Key"):
            if not api_key:
                st.error("Please enter an API key.")
            else:
                try:
                    with st.spinner("Validating..."):
                        model = init_gemini(api_key)
                    st.session_state["gemini_model"] = model
                    st.session_state["gemini_api_key"] = api_key
                    st.success("Gemini API key validated!")
                except Exception as e:
                    st.error(f"Invalid API key: {e}")

        if st.session_state.get("gemini_model"):
            st.markdown(":white_check_mark: Gemini connected")

        st.divider()

        # Semrush (optional)
        st.subheader("Semrush API Key (Optional)")
        semrush_key = st.text_input("Enter Semrush API key", type="password", key="semrush_key_input")
        if semrush_key:
            st.session_state["semrush_api_key"] = semrush_key
            st.markdown(":white_check_mark: Semrush key provided")
        else:
            st.session_state["semrush_api_key"] = None

        st.divider()

        # Brand Guidelines
        st.subheader("Brand Guidelines (Optional)")
        if st.session_state.get("brand_profile"):
            st.markdown(":white_check_mark: Brand guidelines loaded")
            with st.expander("View Brand Profile"):
                st.markdown(st.session_state["brand_profile"])
            if st.button("Clear Brand Guidelines"):
                st.session_state["brand_profile"] = None
                st.session_state["brand_raw_text"] = None
                st.rerun()
        else:
            uploaded_file = st.file_uploader(
                "Upload brand guidelines",
                type=["pdf", "docx", "txt"],
                key="brand_file_upload",
            )
            if uploaded_file and st.button("Process Guidelines"):
                if not st.session_state.get("gemini_model"):
                    st.error("Validate your Gemini API key first.")
                else:
                    try:
                        with st.spinner("Extracting and analyzing brand guidelines..."):
                            raw_text = extract_text_from_file(uploaded_file)
                            st.session_state["brand_raw_text"] = raw_text
                            profile = generate_brand_profile(
                                st.session_state["gemini_model"],
                                raw_text,
                            )
                            st.session_state["brand_profile"] = profile
                        st.success("Brand guidelines processed!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing guidelines: {e}")

        st.divider()

        # Google OAuth
        st.subheader("Google Drive")
        if st.session_state.get("google_creds"):
            st.markdown(":white_check_mark: Google account connected")
        else:
            if st.button("Connect Google Account"):
                try:
                    with st.spinner("Opening browser for Google sign-in..."):
                        creds = get_google_credentials()
                    st.session_state["google_creds"] = creds
                    st.session_state["docs_service"] = get_docs_service(creds)
                    st.session_state["drive_service"] = get_drive_service(creds)
                    st.success("Google account connected!")
                    st.rerun()
                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Google auth failed: {e}")
