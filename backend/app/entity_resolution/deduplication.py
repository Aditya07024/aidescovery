import logging
from typing import Any, Dict, List
from app.entity_resolution.resolver import EntityResolver

logger = logging.getLogger(__name__)


def deduplicate_entities(
    entities: List[Dict[str, Any]],
    confidence_threshold: float = 0.70
) -> List[Dict[str, Any]]:
    """
    Deduplicates a list of normalized raw entities.
    Combines duplicate records exceeding the confidence threshold into a single resolved entity.
    """
    resolver = EntityResolver()
    resolved: List[Dict[str, Any]] = []

    for item in entities:
        merged_flag = False
        for i, existing in enumerate(resolved):
            confidence, signals = resolver.compute_match_confidence(item, existing)
            if confidence >= confidence_threshold:
                logger.info(f"Deduplicating entity '{item.get('name')}' into '{existing.get('name')}' with score {confidence}: {signals}")
                resolved[i] = resolver.merge_entities(existing, item)
                merged_flag = True
                break
        if not merged_flag:
            resolved.append(item)

    return resolved
