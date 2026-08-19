from app.entity_resolution.resolver import EntityResolver
from app.entity_resolution.deduplication import deduplicate_entities


def test_entity_resolution_matching():
    resolver = EntityResolver()

    e1 = {
        "name": "Dr. Rahul Sharma",
        "email": "contact@rahulsharma.in",
        "website": "https://rahulsharma.in",
        "location_summary": "Mathura, Uttar Pradesh",
    }
    e2 = {
        "name": "Rahul Sharma Psychology",
        "email": "contact@rahulsharma.in",
        "website": "https://rahulsharma.in",
        "location_summary": "Mathura",
    }

    confidence, signals = resolver.compute_match_confidence(e1, e2)
    assert confidence >= 0.85
    assert len(signals) > 0


def test_deduplicate_entities_list():
    raw_list = [
        {"name": "Dr Rahul Sharma", "email": "rahul@example.com", "location_summary": "Mathura"},
        {"name": "Rahul Sharma Therapy", "email": "rahul@example.com", "location_summary": "Mathura, UP"},
        {"name": "Priya Verma", "email": "priya@example.com", "location_summary": "Mathura"},
    ]

    resolved = deduplicate_entities(raw_list)
    assert len(resolved) == 2
