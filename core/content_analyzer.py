import json
import re
from google.generativeai import GenerativeModel
from models.schemas import GeneratedQuery, QueryPlacement, ParsedContent
from prompts.templates import CONTENT_ANALYSIS_PROMPT, CONTENT_GENERATION_PROMPT
from config import ANALYSIS_TEMPERATURE, MAX_OUTPUT_TOKENS, MAX_URL_CONTENT_LENGTH


def _repair_truncated_json(raw: str) -> list[dict]:
    """Attempt to salvage a truncated JSON array by keeping only complete objects."""
    objects = []
    for match in re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}', raw, re.DOTALL):
        try:
            obj = json.loads(match.group())
            if "query_text" in obj:
                objects.append(obj)
        except json.JSONDecodeError:
            continue
    return objects


def map_queries_to_content(
    model: GenerativeModel,
    selected_queries: list[GeneratedQuery],
    parsed_content: ParsedContent,
) -> list[QueryPlacement]:
    sections_data = []
    for s in parsed_content.sections:
        truncated_body = s.body_text[:300] if len(s.body_text) > 300 else s.body_text
        sections_data.append({
            "section_index": s.section_index,
            "heading": s.heading,
            "heading_level": s.heading_level,
            "body_text": truncated_body,
            "word_count": s.word_count,
        })

    sections_json = json.dumps(sections_data, indent=2)
    queries_json = json.dumps(
        [
            {
                "query_text": q.query_text,
                "intent": q.intent.value,
                "query_type": q.query_type.value,
            }
            for q in selected_queries
        ],
        indent=2,
    )

    # Truncate if combined content is too long
    combined = sections_json + queries_json
    if len(combined) > MAX_URL_CONTENT_LENGTH:
        sections_json = sections_json[: MAX_URL_CONTENT_LENGTH // 2]

    prompt = CONTENT_ANALYSIS_PROMPT.format(
        content_sections_json=sections_json,
        selected_queries_json=queries_json,
    )

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": ANALYSIS_TEMPERATURE,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "response_mime_type": "application/json",
        },
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    try:
        placements_data = json.loads(raw)
    except json.JSONDecodeError:
        placements_data = _repair_truncated_json(raw)
        if not placements_data:
            raise ValueError("Gemini returned invalid JSON during analysis. Please try again with fewer queries selected.")

    results = []
    for p in placements_data:
        query = next(
            (q for q in selected_queries if q.query_text == p["query_text"]),
            None,
        )
        if not query:
            continue
        section_idx = p.get("target_section_index", 0)
        if section_idx >= len(parsed_content.sections):
            section_idx = len(parsed_content.sections) - 1
        section = parsed_content.sections[section_idx]
        results.append(
            QueryPlacement(
                query=query,
                target_section=section,
                placement_type=p.get("placement_type", "new_paragraph"),
                reasoning=p.get("reasoning", ""),
                suggested_heading=p.get("suggested_heading"),
                content_brief=p.get("content_brief", ""),
            )
        )
    return results


def generate_content_for_placements(
    model: GenerativeModel,
    placements: list[QueryPlacement],
    parsed_content: ParsedContent,
    brand_profile: str | None = None,
) -> dict[str, str]:
    """Generate full written content for each placement. Returns {query_text: generated_content}."""
    if brand_profile:
        brand_section = f"\n## Brand Guidelines (MUST FOLLOW):\n{brand_profile}\n"
    else:
        brand_section = ""

    generated = {}
    for p in placements:
        prompt = CONTENT_GENERATION_PROMPT.format(
            article_title=parsed_content.title,
            article_url=parsed_content.url,
            section_heading=p.target_section.heading,
            section_body=p.target_section.body_text[:500],
            query_text=p.query.query_text,
            placement_type=p.placement_type.replace("_", " "),
            suggested_heading=p.suggested_heading or "N/A",
            content_brief=p.content_brief,
            brand_guidelines_section=brand_section,
        )
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                },
            )
            generated[p.query.query_text] = response.text.strip()
        except Exception:
            generated[p.query.query_text] = "(Content generation failed — retry later)"
    return generated
