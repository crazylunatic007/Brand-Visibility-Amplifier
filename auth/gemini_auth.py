import google.generativeai as genai
from config import GEMINI_MODEL_NAME


def init_gemini(api_key: str) -> genai.GenerativeModel:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    model.generate_content("test", generation_config={"max_output_tokens": 5})
    return model
