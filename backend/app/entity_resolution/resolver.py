import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def normalize_string(text: Optional[str]) -> str:
    if not text:
        return ""
    # Lowercase, strip punctuation and honorific titles
    text = text.lower()
    text = re.sub(r"\b(dr|mr|mrs|ms|prof|doctor|clinic|psychologist|therapist)\b", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def extract_domain(url: Optional[str]) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(url if "://" in url else f"http://{url}")
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


class EntityResolver:
    """
    Multi-signal Entity Resolution Engine.
    Evaluates candidate normalized entities against existing records using:
    1. Exact Email Match (Weight 0.95)
    2. Exact Phone Match (Weight 0.90)
    3. Canonical Website Domain Match (Weight 0.85)
    4. Canonical Social Profile URL Match (Weight 0.85)
    5. Name + Location Match (Weight 0.75)
    6. Name + Company Match (Weight 0.70)
    """

    def compute_match_confidence(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> Tuple[float, List[str]]:
        signals = []
        confidence = 0.0

        # Signal 1: Email Match
        e1_email = (entity1.get("email") or "").strip().lower()
        e2_email = (entity2.get("email") or "").strip().lower()
        if e1_email and e2_email and e1_email == e2_email:
            confidence = max(confidence, 0.95)
            signals.append(f"Exact email match ({e1_email})")

        # Signal 2: Phone Match
        e1_phone = re.sub(r"\D", "", entity1.get("phone") or "")
        e2_phone = re.sub(r"\D", "", entity2.get("phone") or "")
        if e1_phone and e2_phone and len(e1_phone) >= 7 and e1_phone == e2_phone:
            confidence = max(confidence, 0.90)
            signals.append("Exact phone number match")

        # Signal 3: Website Domain Match
        dom1 = extract_domain(entity1.get("website"))
        dom2 = extract_domain(entity2.get("website"))
        if dom1 and dom2 and dom1 == dom2 and dom1 not in ("facebook.com", "instagram.com", "youtube.com", "linkedin.com"):
            confidence = max(confidence, 0.85)
            signals.append(f"Domain match ({dom1})")

        # Signal 4: Social Profile URL Match
        soc1 = set(entity1.get("social_profiles", []))
        soc2 = set(entity2.get("social_profiles", []))
        common_socials = soc1.intersection(soc2)
        if common_socials:
            confidence = max(confidence, 0.85)
            signals.append(f"Social profile match ({list(common_socials)[0]})")

        # Signal 5: Name Similarity + Location/Company Match
        name1 = normalize_string(entity1.get("name"))
        name2 = normalize_string(entity2.get("name"))
        
        if name1 and name2 and (name1 in name2 or name2 in name1):
            loc1 = normalize_string(entity1.get("location_summary"))
            loc2 = normalize_string(entity2.get("location_summary"))
            if loc1 and loc2 and (loc1 in loc2 or loc2 in loc1):
                confidence = max(confidence, 0.75)
                signals.append("Name and Location match")

            comp1 = normalize_string(entity1.get("company_name"))
            comp2 = normalize_string(entity2.get("company_name"))
            if comp1 and comp2 and (comp1 in comp2 or comp2 in comp1):
                confidence = max(confidence, 0.70)
                signals.append("Name and Company match")

        return confidence, signals

    def merge_entities(self, target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges source entity into target entity while preserving raw provenance records.
        """
        merged = dict(target)

        # Update missing fields
        for field in ["email", "phone", "website", "description", "location_summary"]:
            if not merged.get(field) and source.get(field):
                merged[field] = source[field]

        # Combine social profiles uniquely
        socials = set(merged.get("social_profiles", []))
        socials.update(source.get("social_profiles", []))
        merged["social_profiles"] = list(socials)

        # Combine raw provenance records
        prov1 = merged.get("raw_provenance", [])
        prov2 = source.get("raw_provenance", [])
        merged["raw_provenance"] = prov1 + prov2

        return merged
