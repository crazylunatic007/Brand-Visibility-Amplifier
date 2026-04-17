import requests
from bs4 import BeautifulSoup
import trafilatura
from models.schemas import ContentSection, ParsedContent
from config import REQUEST_TIMEOUT


def fetch_and_parse(url: str) -> ParsedContent:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    html = response.text

    clean_text = trafilatura.extract(html, include_comments=False) or ""

    soup = BeautifulSoup(html, "lxml")
    title = soup.title.string if soup.title else ""
    meta_desc = None
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        meta_desc = meta_tag.get("content", "")

    sections = _extract_sections(soup)

    return ParsedContent(
        url=url,
        title=title.strip() if title else "",
        sections=sections,
        full_text=clean_text,
        meta_description=meta_desc,
    )


def _extract_sections(soup: BeautifulSoup) -> list[ContentSection]:
    heading_tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    sections = []
    for i, tag in enumerate(heading_tags):
        level = int(tag.name[1])
        heading_text = tag.get_text(strip=True)
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
