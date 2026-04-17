import io
from google.generativeai import GenerativeModel
from prompts.templates import BRAND_EXTRACTION_PROMPT


def extract_text_from_file(uploaded_file) -> str:
    """Extract plain text from an uploaded PDF, DOCX, or TXT file."""
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return _extract_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return _extract_docx(uploaded_file)
    elif filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {filename}. Use PDF, DOCX, or TXT.")


def _extract_pdf(uploaded_file) -> str:
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n".join(text_parts)


def _extract_docx(uploaded_file) -> str:
    from docx import Document

    doc = Document(io.BytesIO(uploaded_file.read()))
    text_parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)
    return "\n".join(text_parts)


def generate_brand_profile(
    model: GenerativeModel,
    raw_guidelines_text: str,
) -> str:
    """Use Gemini to extract a structured brand voice profile from raw guidelines text."""
    # Truncate if very long to stay within context limits
    truncated = raw_guidelines_text[:30000]

    prompt = BRAND_EXTRACTION_PROMPT.format(guidelines_text=truncated)
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 2048,
        },
    )
    return response.text.strip()
