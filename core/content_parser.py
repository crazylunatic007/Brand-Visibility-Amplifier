import re
import requests
from bs4 import BeautifulSoup
import trafilatura
from models.schemas import ContentSection, ParsedContent
from config import REQUEST_TIMEOUT


def fetch_and_parse(url: str) -> ParsedContent:
    # Strategy 1: Use trafilatura's own fetcher (handles more edge cases)
    downloaded = trafilatura.fetch_url(url)

    # Strategy 2: Fall back to requests if trafilatura fetch fails
    if not downloaded:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        response.raise_for_status()
        downloaded = response.text

    # Extract clean text with formatting preserved (markdown-style headings)
    clean_text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_formatting=True,
        include_links=True,
    ) or ""

    # Parse HTML for structured sections
    soup = BeautifulSoup(downloaded, "lxml")
    title = soup.title.string if soup.title else ""
    meta_desc = None
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        meta_desc = meta_tag.get("content", "")

    # Try BeautifulSoup section extraction first
    sections = _extract_sections(soup)

    # Fallback: If BS4 found no meaningful sections but trafilatura got text,
    # build sections from the trafilatura markdown output
    if not sections or all(s.word_count == 0 for s in sections):
        if clean_text:
            sections = _sections_from_text(clean_text)

    # Last resort: treat the entire extracted text as one section
    if not sections and clean_text:
        sections = [
            ContentSection(
                heading=title.strip() if title else "Main Content",
                heading_level=1,
                body_text=clean_text,
                word_count=len(clean_text.split()),
                section_index=0,
            )
        ]

    return ParsedContent(
        url=url,
        title=title.strip() if title else "",
        sections=sections,
        full_text=clean_text,
        meta_description=meta_desc,
    )


def _extract_sections(soup: BeautifulSoup) -> list[ContentSection]:
    """Extract sections from HTML heading tags."""
    heading_tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    sections = []
    for i, tag in enumerate(heading_tags):
        level = int(tag.name[1])
        heading_text = tag.get_text(strip=True)
        if not heading_text:
            continue
        body_parts = []
        for sibling in tag.find_next_siblings():
            if sibling.name and sibling.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                break
            text = sibling.get_text(strip=True)
            if text:
                body_parts.append(text)
        body = " ".join(body_parts)
        sections.append(
            ContentSection(
                heading=heading_text,
                heading_level=level,
                body_text=body,
                word_count=len(body.split()),
                section_index=i,
            )
        )
    return sections


def _sections_from_text(text: str) -> list[ContentSection]:
    """Build sections from trafilatura's markdown-formatted output.

    Trafilatura outputs headings as lines starting with ## or ###.
    Split on those to create structured sections.
    """
    sections = []
    # Split on markdown headings (## Heading or ### Heading etc.)
    parts = re.split(r'^(#{1,6})\s+(.+)$', text, flags=re.MULTILINE)

    # parts will be: [text_before, '#level', 'heading', text_after, '#level', 'heading', ...]
    if len(parts) < 4:
        # No markdown headings found — split on double newlines as paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 1:
            return []
        for i, para in enumerate(paragraphs):
            first_line = para.split("\n")[0][:80]
            body = para
            sections.append(
                ContentSection(
                    heading=first_line,
                    heading_level=2,
                    body_text=body,
                    word_count=len(body.split()),
                    section_index=i,
                )
            )
        return sections

    # Process markdown heading splits
    idx = 0
    # Handle text before first heading
    preamble = parts[0].strip()
    if preamble:
        sections.append(
            ContentSection(
                heading="Introduction",
                heading_level=1,
                body_text=preamble,
                word_count=len(preamble.split()),
                section_index=0,
            )
        )
        idx = 1

    # Process heading groups (level_markers, heading_text, body_text)
    i = 1
    while i < len(parts) - 2:
        level_str = parts[i]
        heading = parts[i + 1].strip()
        body = parts[i + 2].strip() if i + 2 < len(parts) else ""
        level = len(level_str)  # number of # characters

        sections.append(
            ContentSection(
                heading=heading,
                heading_level=level,
                body_text=body,
                word_count=len(body.split()) if body else 0,
                section_index=idx,
            )
        )
        idx += 1
        i += 3

    return sections
