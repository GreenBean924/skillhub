import re
from dataclasses import dataclass, field


@dataclass
class CapabilityFinding:
    capability: str
    evidence: str
    line_number: int | None = None


@dataclass
class CapabilityAnalysis:
    findings: list[CapabilityFinding] = field(default_factory=list)

    def to_context(self) -> dict:
        return {
            "detected_capabilities": [
                {
                    "capability": f.capability,
                    "evidence": f.evidence,
                    "line_number": f.line_number,
                }
                for f in self.findings
            ]
        }


CAPABILITY_PATTERNS = {
    "network_access": [
        (r"(?:fetch|axios|http\.get|https\.get|requests\.get|urllib)\s*\(", "HTTP request"),
        (r"(?:XMLHttpRequest|WebSocket|\.ajax)\s*\(", "Network client"),
        (r"(?:socket\.connect|net\.connect|tls\.connect)\s*\(", "Socket connection"),
        (r"import\s+(?:requests|aiohttp|httpx|urllib3)", "HTTP library import"),
    ],
    "file_read": [
        (r"(?:fs\.readFile|fs\.readFileSync|open\s*\(.*['\"]r)", "File read operation"),
        (r"(?:path\.join|path\.resolve|os\.homedir)", "File path construction"),
        (r"import\s+fs\b", "Filesystem module import"),
    ],
    "file_write": [
        (r"(?:fs\.writeFile|fs\.writeFileSync|open\s*\(.*['\"]w)", "File write operation"),
        (r"(?:fs\.appendFile|fs\.createWriteStream)", "File append/stream"),
        (r"(?:shutil\.copy|shutil\.move|os\.rename)", "File system modification"),
    ],
    "process_exec": [
        (r"(?:exec|execSync|spawn|spawnSync)\s*\(", "Process execution"),
        (r"(?:subprocess\.(?:run|call|Popen|check_output))\s*\(", "Subprocess call"),
        (r"(?:child_process|os\.system|os\.popen)", "System command execution"),
    ],
    "code_exec": [
        (r"\beval\s*\(", "eval() call"),
        (r"\bexec\s*\((?!Sync)", "exec() on dynamic code"),
        (r"(?:new\s+Function|compile\s*\()", "Dynamic code compilation"),
    ],
    "llm_call": [
        (r"(?:openai|OpenAI|chat\.completions)", "LLM API call"),
        (r"(?:callLLM|analyzeWithLLM|promptLLM)", "LLM wrapper function"),
        (r"(?:dashscope|anthropic|gemini)", "Alternative LLM provider"),
    ],
    "sudo": [
        (r"(?:sudo\s|pkexec|doas\s)", "Privilege escalation command"),
        (r"(?:geteuid|setuid|setgid)", "UID/GID manipulation"),
    ],
    "shell_exec": [
        (r"(?:/bin/(?:ba)?sh|/usr/bin/(?:ba)?sh)", "Shell invocation"),
        (r"(?:cmd\.exe|powershell)", "Windows shell invocation"),
        (r"shell:\s*true", "Shell mode enabled"),
    ],
}


def analyze_capabilities(content: str) -> CapabilityAnalysis:
    result = CapabilityAnalysis()

    if not content:
        return result

    lines = content.split("\n")

    for cap_type, patterns in CAPABILITY_PATTERNS.items():
        for pattern, description in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    result.findings.append(CapabilityFinding(
                        capability=cap_type,
                        evidence=f"{description}: {line.strip()[:120]}",
                        line_number=i,
                    ))
                    break

    return result
