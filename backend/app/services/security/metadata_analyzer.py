import re
from dataclasses import dataclass, field


@dataclass
class MetadataAnalysis:
    declared_purpose: str = ""
    author_reputation: str = "unknown"
    source_trustworthiness: str = "unknown"
    expected_capabilities: list[str] = field(default_factory=list)
    suspicious_metadata: list[dict] = field(default_factory=list)

    def to_context(self) -> dict:
        return {
            "declared_purpose": self.declared_purpose,
            "author_reputation": self.author_reputation,
            "source_trustworthiness": self.source_trustworthiness,
            "expected_capabilities": self.expected_capabilities,
            "suspicious_metadata": self.suspicious_metadata,
        }


PURPOSE_KEYWORDS = {
    "scraping": ["scrape", "crawl", "extract", "parse", "fetch"],
    "code-review": ["review", "analyze", "lint", "check", "audit"],
    "migration": ["migrate", "migration", "schema", "database", "upgrade"],
    "monitoring": ["monitor", "metrics", "alert", "watch", "track"],
    "translation": ["translate", "i18n", "localize", "language"],
    "testing": ["test", "fuzz", "benchmark", "validate"],
    "automation": ["automate", "workflow", "pipeline", "deploy"],
    "security": ["scan", "detect", "audit", "vulnerability", "secrets"],
}

CAPABILITY_BY_PURPOSE = {
    "scraping": ["network_access", "file_write", "process_exec"],
    "code-review": ["file_read", "llm_call"],
    "migration": ["network_access", "file_read", "file_write"],
    "monitoring": ["process_exec", "network_access", "file_write"],
    "translation": ["file_read", "llm_call"],
    "testing": ["network_access", "file_write"],
    "automation": ["process_exec", "file_read", "file_write"],
    "security": ["file_read", "process_exec"],
}


def analyze_metadata(
    name: str,
    description: str,
    author: str,
    tags: list[str],
    capabilities: list[str],
) -> MetadataAnalysis:
    result = MetadataAnalysis()

    desc_lower = description.lower()
    for purpose, keywords in PURPOSE_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            result.declared_purpose = purpose
            result.expected_capabilities = CAPABILITY_BY_PURPOSE.get(purpose, [])
            break

    if not result.declared_purpose:
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in PURPOSE_KEYWORDS:
                result.declared_purpose = tag_lower
                result.expected_capabilities = CAPABILITY_BY_PURPOSE.get(tag_lower, [])
                break

    known_authors = {"devtools-lab", "sec-research", "ops-guru", "ai-tools", "datacraft", "i18n-tools", "cyberdev"}
    if author.lower() in known_authors:
        result.author_reputation = "known"
    else:
        result.author_reputation = "unknown"

    name_lower = name.lower()
    suspicious_patterns = [
        (r"free\s+(money|crypto|bitcoin)", "Potentially misleading name"),
        (r"hack|exploit|backdoor", "Name contains suspicious terms"),
        (r"system|root|admin", "Name implies elevated access"),
    ]
    for pattern, reason in suspicious_patterns:
        if re.search(pattern, name_lower):
            result.suspicious_metadata.append({"type": "name", "reason": reason, "evidence": name})

    declared_set = set(capabilities)
    expected_set = set(result.expected_capabilities)
    unexpected_caps = declared_set - expected_set
    high_risk_unexpected = unexpected_caps & {"code_exec", "sudo", "shell_exec"}
    if high_risk_unexpected:
        result.suspicious_metadata.append({
            "type": "capability_mismatch",
            "reason": f"High-risk capabilities not expected for stated purpose: {', '.join(high_risk_unexpected)}",
            "evidence": list(high_risk_unexpected),
        })

    return result
