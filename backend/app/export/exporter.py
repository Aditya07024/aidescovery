import csv
import io
import json
from typing import Any, AsyncGenerator, Dict, List


async def generate_csv_stream(results: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
    """
    Generates streamed CSV data for entity export.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Write Header
    writer.writerow([
        "Entity ID",
        "Name",
        "Entity Type",
        "Website",
        "Email",
        "Phone",
        "Location",
        "Match Score",
        "Is Qualified",
        "Qualification Reasons",
    ])
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    for item in results:
        reasons_str = " | ".join(item.get("qualification_reasons", []))
        writer.writerow([
            item.get("entity_id", ""),
            item.get("name", ""),
            item.get("entity_type", ""),
            item.get("website", ""),
            item.get("email", ""),
            item.get("phone", ""),
            item.get("location_summary", ""),
            item.get("match_score", 0.0),
            item.get("is_qualified", False),
            reasons_str,
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


async def generate_json_stream(results: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
    """
    Generates streamed JSON data for entity export.
    """
    yield "[\n"
    first = True
    for item in results:
        if not first:
            yield ",\n"
        first = False
        yield json.dumps(item, indent=2)
    yield "\n]"
