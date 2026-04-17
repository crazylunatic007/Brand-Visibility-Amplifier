import json
import re
from google.generativeai import GenerativeModel
from models.schemas import GeneratedQuery
from prompts.templates import QUERY_FANOUT_PROMPT
from config import FANOUT_TEMPERATURE, MAX_OUTPUT_TOKENS


def _repair_truncated_json(raw: str) -> list[dict]:
    """Attempt to salvage a truncated JSON array by keeping only complete objects."""
    # Find all complete JSON objects in the array
    objects = []
    for match in re.finditer(r'\{[^{}]*\}', raw):
        try:
            obj = json.loads(match.group())
            if "query_text" in obj:
                objects.append(obj)
        except json.JSONDecodeError:
            continue
    return objects


def generate_query_fanout(
    model: GenerativeModel,
    seed_keyword: str,
) -> list[GeneratedQuery]:
    prompt = QUERY_FANOUT_PROMPT.format(seed_keyword=seed_keyword)
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": FANOUT_TEMPERATURE,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "response_mime_type": "application/json",
        },
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    try:
        queries_data = json.loads(raw)
    except json.JSONDecodeError:
        queries_data = _repair_truncated_json(raw)
        if not queries_data:
            raise ValueError("Gemini returned invalid JSON. Please try again.")

    results = []
    for q in queries_data:
        try:
            results.append(GeneratedQuery(**q))
        except Exception:
            continue
    if not results:
        raise ValueError("No valid queries could be parsed. Please try again.")
    return results
