import requests as req
from models.schemas import GeneratedQuery


def validate_queries_with_semrush(
    queries: list[GeneratedQuery],
    api_key: str,
    database: str = "us",
) -> list[GeneratedQuery]:
    for query in queries:
        try:
            params = {
                "type": "phrase_this",
                "key": api_key,
                "phrase": query.query_text,
                "database": database,
                "export_columns": "Ph,Nq,Kd",
            }
            resp = req.get(
                "https://api.semrush.com/",
                params=params,
                timeout=10,
            )
            if resp.status_code == 200 and resp.text.strip():
                lines = resp.text.strip().split("\n")
                if len(lines) >= 2:
                    values = lines[1].split(";")
                    if len(values) >= 2:
                        query.search_volume = int(values[1]) if values[1] else None
                    if len(values) >= 3:
                        query.keyword_difficulty = float(values[2]) if values[2] else None
                    query.semrush_validated = True
        except Exception:
            pass
    return queries
