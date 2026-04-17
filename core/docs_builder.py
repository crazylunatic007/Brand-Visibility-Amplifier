from models.schemas import QueryPlacement, ParsedContent


def create_recommendations_doc(
    docs_service,
    drive_service,
    parsed_content: ParsedContent,
    placements: list[QueryPlacement],
    generated_content: dict[str, str] | None = None,
    folder_id: str | None = None,
) -> str:
    title = f"Content Recommendations: {parsed_content.title[:80]}"

    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    if folder_id:
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents="root",
        ).execute()

    requests_list = _build_doc_requests(parsed_content, placements, generated_content or {})

    if requests_list:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests_list},
        ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def _build_doc_requests(
    parsed_content: ParsedContent,
    placements: list[QueryPlacement],
    generated_content: dict[str, str],
) -> list[dict]:
    requests = []
    idx = 1

    header_text = "Content Enhancement Recommendations\n"
    requests.append({"insertText": {"location": {"index": idx}, "text": header_text}})
    requests.append(_style_range(idx, idx + len(header_text) - 1, "HEADING_1"))
    idx += len(header_text)

    source_line = f"\nSource: {parsed_content.url}\nArticle: {parsed_content.title}\n\n"
    requests.append({"insertText": {"location": {"index": idx}, "text": source_line}})
    idx += len(source_line)

    # Group placements by target section
    section_map: dict[int, list[QueryPlacement]] = {}
    for p in placements:
        si = p.target_section.section_index
        section_map.setdefault(si, []).append(p)

    for section_index in sorted(section_map.keys()):
        section_placements = section_map[section_index]
        section = section_placements[0].target_section

        sec_text = f"\n{section.heading}\n"
        requests.append({"insertText": {"location": {"index": idx}, "text": sec_text}})
        requests.append(_style_range(idx + 1, idx + len(sec_text) - 1, "HEADING_2"))
        idx += len(sec_text)

        for p in section_placements:
            q_text = f"\nTarget Query: {p.query.query_text}\n"
            requests.append(
                {"insertText": {"location": {"index": idx}, "text": q_text}}
            )
            requests.append(
                _style_range(idx + 1, idx + len(q_text) - 1, "HEADING_3")
            )
            idx += len(q_text)

            detail_lines = (
                f"Placement: {p.placement_type.replace('_', ' ').title()}\n"
                f"Intent: {p.query.intent.value}\n"
                f"Type: {p.query.query_type.value}\n"
            )
            if p.suggested_heading:
                detail_lines += f"Suggested Heading: {p.suggested_heading}\n"
            detail_lines += f"\nContent Brief:\n{p.content_brief}\n"
            detail_lines += f"\nReasoning:\n{p.reasoning}\n"

            requests.append(
                {"insertText": {"location": {"index": idx}, "text": detail_lines}}
            )
            idx += len(detail_lines)

            # Add generated content
            content = generated_content.get(p.query.query_text, "")
            if content:
                content_header = "\nGenerated Content:\n"
                requests.append(
                    {"insertText": {"location": {"index": idx}, "text": content_header}}
                )
                # Bold the "Generated Content:" label
                requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": idx + 1, "endIndex": idx + len(content_header) - 1},
                        "textStyle": {"bold": True},
                        "fields": "bold",
                    }
                })
                idx += len(content_header)

                content_text = f"{content}\n"
                requests.append(
                    {"insertText": {"location": {"index": idx}, "text": content_text}}
                )
                idx += len(content_text)

            separator = "\n---\n"
            requests.append(
                {"insertText": {"location": {"index": idx}, "text": separator}}
            )
            idx += len(separator)

    return requests


def _style_range(start: int, end: int, named_style: str) -> dict:
    return {
        "updateParagraphStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "paragraphStyle": {"namedStyleType": named_style},
            "fields": "namedStyleType",
        }
    }
