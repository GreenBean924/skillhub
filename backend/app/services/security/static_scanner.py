import re
from dataclasses import dataclass, field


@dataclass
class StaticFinding:
    category: str
    severity: str
    title: str
    evidence: str
    line_number: int | None = None


@dataclass
class StaticAnalysis:
    findings: list[StaticFinding] = field(default_factory=list)

    def to_context(self) -> dict:
        return {
            "static_findings": [
                {
                    "category": f.category,
                    "severity": f.severity,
                    "title": f.title,
                    "evidence": f.evidence,
                    "line_number": f.line_number,
                }
                for f in self.findings
            ]
        }


SCAN_CATEGORIES = {
    "shell_injection": {
        "patterns": [
            (r"(?:exec|execSync)\s*\(\s*[`'\"]\s*(?:top|df|netstat|ps|kill|curl|wget)", "Shell command with system utility"),
            (r"(?:exec|execSync)\s*\(\s*`[^`]*\$\{", "Shell command with string interpolation"),
            (r"(?:exec|execSync)\s*\(\s*['\"].*\+\s*\w+", "Shell command with concatenation"),
            (r"child_process\.(?:exec|execSync)\s*\(", "child_process exec usage"),
        ],
        "severity": "medium",
    },
    "sensitive_file_access": {
        "patterns": [
            (r"(?:\.ssh|\.aws|\.gnupg|\.env|\.git/config)", "Sensitive config file access"),
            (r"(?:/etc/passwd|/etc/shadow|/etc/hosts)", "System file access"),
            (r"(?:credentials|\.pem|\.key|id_rsa)", "Credential file access"),
            (r"(?:process\.env\.(?:HOME|USERPROFILE))", "Home directory access"),
        ],
        "severity": "medium",
    },
    "hidden_behavior": {
        "patterns": [
            (r"(?:atob|btoa)\s*\(\s*(?:process\.env|secret|key|token|password)", "Encoded sensitive data"),
            (r"(?:Buffer\.from\s*\(\s*\w+,\s*['\"]base64['\"])", "Base64 decoding"),
            (r"(?:eval|Function)\s*\(\s*(?:atob|Buffer)", "Dynamic code from encoded source"),
            (r"(?:setTimeout|setInterval)\s*\(\s*(?:eval|Function|new\s+Function)", "Delayed code execution"),
        ],
        "severity": "high",
    },
    "data_exfiltration": {
        "patterns": [
            (r"(?:fetch|axios|http)\s*\(\s*[^)]*(?:process\.env|secret|key|token|password)", "Sending sensitive data over network"),
            (r"(?:FormData|URLSearchParams)\s*\(.*(?:password|token|secret|key)", "Form data with sensitive fields"),
            (r"(?:btoa|Buffer\.from)\s*\(.*(?:env|secret|key|token)", "Encoding sensitive data for transmission"),
        ],
        "severity": "high",
    },
    "subprocess_risk": {
        "patterns": [
            (r"subprocess\.(?:call|run|Popen)\s*\(.*shell\s*=\s*True", "Subprocess with shell=True"),
            (r"os\.system\s*\(", "os.system() call"),
            (r"os\.popen\s*\(", "os.popen() call"),
        ],
        "severity": "medium",
    },
    "prompt_injection_risk": {
        "patterns": [
            (r"(?:ignore\s+(?:previous|above|all)\s+instructions)", "Prompt injection pattern"),
            (r"(?:you\s+are\s+now|disregard|override|jailbreak)", "Prompt override pattern"),
            (r"(?:system\s*:\s*['\"].*ignore)", "System prompt manipulation"),
        ],
        "severity": "high",
    },
    "crypto_mining": {
        "patterns": [
            (r"(?:coinhive|CoinHive|cryptonight|stratum\+tcp)", "Known mining software"),
            (r"(?:mining|miner|minerWorker|hashrate)", "Mining-related terms"),
            (r"(?:xmrig|nicehash|nanopool)", "Known mining pool/software"),
        ],
        "severity": "critical",
    },
}


def scan_content(content: str) -> StaticAnalysis:
    result = StaticAnalysis()

    if not content:
        return result

    lines = content.split("\n")

    for category, config in SCAN_CATEGORIES.items():
        for pattern, description in config["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    result.findings.append(StaticFinding(
                        category=category,
                        severity=config["severity"],
                        title=description,
                        evidence=line.strip()[:150],
                        line_number=i,
                    ))

    return result
