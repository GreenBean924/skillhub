import re
from dataclasses import dataclass, field


@dataclass
class PromptFinding:
    pattern_type: str
    severity: str
    title: str
    evidence: str
    line_number: int | None = None


@dataclass
class PromptAnalysis:
    findings: list[PromptFinding] = field(default_factory=list)
    contains_instructions: bool = False
    instruction_sections: list[str] = field(default_factory=list)

    def to_context(self) -> dict:
        return {
            "prompt_findings": [
                {
                    "pattern_type": f.pattern_type,
                    "severity": f.severity,
                    "title": f.title,
                    "evidence": f.evidence,
                    "line_number": f.line_number,
                }
                for f in self.findings
            ],
            "contains_instructions": self.contains_instructions,
            "instruction_sections": self.instruction_sections[:5],
        }


INJECTION_PATTERNS = [
    {
        "type": "ignore_previous",
        "pattern": r"(?:ignore|disregard|forget|override)\s+(?:previous|above|all|prior)\s+(?:instructions?|prompts?|rules?)",
        "severity": "high",
        "title": "Instruction override attempt",
    },
    {
        "type": "role_override",
        "pattern": r"(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be|new\s+role|new\s+instructions)",
        "severity": "high",
        "title": "Role override attempt",
    },
    {
        "type": "hidden_command",
        "pattern": r"(?:<\|?(?:system|assistant|user)\|?>|###\s*(?:SYSTEM|INSTRUCTION))",
        "severity": "high",
        "title": "Hidden system/user command injection",
    },
    {
        "type": "data_request",
        "pattern": r"(?:send|transmit|exfiltrate|report)\s+(?:me\s+)?(?:all\s+)?(?:your\s+)?(?:data|files|credentials|keys|tokens)",
        "severity": "critical",
        "title": "Data exfiltration instruction",
    },
    {
        "type": "covert_action",
        "pattern": r"(?:silently|secretly|without\s+(?:the\s+)?user\s+(?:knowing|noticing)|in\s+the\s+background)",
        "severity": "high",
        "title": "Covert behavior instruction",
    },
    {
        "type": "purpose_mismatch",
        "pattern": r"(?:also|additionally|besides)\s+(?:mine|scrape|hack|attack|exploit|inject)",
        "severity": "medium",
        "title": "Purpose expansion to suspicious activity",
    },
]

INSTRUCTION_MARKERS = [
    r"^#\s*(?:Instructions?|Steps?|Workflow|Procedure)",
    r"^(?:Step|Phase|Stage)\s+\d+",
    r"(?:do\s+the\s+following|follow\s+these\s+(?:steps?|instructions?))",
    r"(?:first|then|next|finally)\s*,\s*(?:you\s+)?(?:must|should|will|need\s+to)",
]


def analyze_prompts(content: str, declared_tags: list[str] | None = None) -> PromptAnalysis:
    result = PromptAnalysis()

    if not content:
        return result

    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if not line_stripped or len(line_stripped) < 5:
            continue

        for pattern_config in INJECTION_PATTERNS:
            if re.search(pattern_config["pattern"], line, re.IGNORECASE):
                result.findings.append(PromptFinding(
                    pattern_type=pattern_config["type"],
                    severity=pattern_config["severity"],
                    title=pattern_config["title"],
                    evidence=line_stripped[:150],
                    line_number=i,
                ))

    for marker in INSTRUCTION_MARKERS:
        for i, line in enumerate(lines, 1):
            if re.search(marker, line.strip(), re.IGNORECASE):
                result.contains_instructions = True
                context_start = max(0, i - 1)
                context_end = min(len(lines), i + 3)
                section = "\n".join(lines[context_start:context_end])
                result.instruction_sections.append(section[:300])

    if declared_tags:
        tags_lower = [t.lower() for t in declared_tags]
        suspicious_for_tags = {
            "translation": r"(?:mine|crypto|bitcoin|hack|exploit)",
            "code-review": r"(?:exfiltrate|send.*data|upload.*credentials)",
            "i18n": r"(?:execute|run.*command|access.*system)",
        }
        for tag in tags_lower:
            if tag in suspicious_for_tags:
                pattern = suspicious_for_tags[tag]
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        result.findings.append(PromptFinding(
                            pattern_type="purpose_mismatch",
                            severity="high",
                            title=f"Content inconsistent with declared purpose ({tag})",
                            evidence=line.strip()[:150],
                            line_number=i,
                        ))

    return result
