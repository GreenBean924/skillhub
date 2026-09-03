import json
import logging
from datetime import UTC, datetime

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.prompts.security_review import build_security_review_prompt

logger = logging.getLogger(__name__)

VALID_RISK_LEVELS = {"safe", "low", "medium", "high", "critical"}
VALID_SEVERITIES = {"info", "low", "medium", "high", "critical"}


def _get_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_API_BASE)


def _fallback_report(capabilities: list[str]) -> dict:
    risk_level = "low"
    score = 80
    findings = []

    high_risk_caps = {
        "file_write": "Can write to local file system",
        "network_access": "Can make network requests",
        "code_exec": "Can execute arbitrary code",
        "shell_exec": "Can execute shell commands",
        "sudo": "Requests elevated privileges",
    }

    for i, cap in enumerate(capabilities):
        cap_lower = cap.lower()
        for risk_key, desc in high_risk_caps.items():
            if risk_key in cap_lower:
                risk_level = "medium"
                score = max(50, score - 10)
                findings.append(
                    {
                        "id": f"F{i + 1:03d}",
                        "severity": "medium",
                        "title": f"Capability: {cap}",
                        "description": desc,
                        "evidence": cap,
                        "recommendation": "Review this capability to ensure it aligns with expected behavior",
                    }
                )

    return {
        "risk_level": risk_level,
        "score": score,
        "findings": findings,
        "summary": f"Static analysis only — LLM review unavailable. Detected {len(capabilities)} capabilities.",
        "scannedAt": datetime.now(UTC).isoformat(),
        "review_version": "static-only",
    }


def _validate_report(report: dict) -> dict:
    if report.get("risk_level") not in VALID_RISK_LEVELS:
        report["risk_level"] = "medium"

    score = report.get("score")
    if not isinstance(score, int) or score < 0 or score > 100:
        report["score"] = 50

    findings = report.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    validated_findings = []
    for f in findings:
        if not isinstance(f, dict):
            continue
        validated_findings.append(
            {
                "id": str(f.get("id", "")),
                "severity": f.get("severity", "info") if f.get("severity") in VALID_SEVERITIES else "info",
                "title": str(f.get("title", "")),
                "description": str(f.get("description", "")),
                "evidence": f.get("evidence"),
                "recommendation": str(f.get("recommendation", "")),
            }
        )

    report["findings"] = validated_findings
    report["scannedAt"] = datetime.now(UTC).isoformat()
    report["review_version"] = "llm-v1"

    return report


def _parse_llm_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        text = "\n".join(lines)

    return json.loads(text)


async def review_skill(
    name: str,
    description: str,
    author: str,
    tags: list[str],
    capabilities: list[str],
    content: str,
) -> dict:
    settings = get_settings()

    if not settings.LLM_API_KEY or settings.LLM_API_KEY.startswith("sk-your"):
        logger.warning("LLM_API_KEY not configured, falling back to static analysis")
        return _fallback_report(capabilities)

    messages = build_security_review_prompt(
        name=name,
        description=description,
        author=author,
        tags=tags,
        capabilities=capabilities,
        content=content,
    )

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            timeout=30.0,
        )

        content_text = response.choices[0].message.content
        logger.info(
            "LLM review completed for %s: tokens=%d",
            name,
            response.usage.total_tokens if response.usage else 0,
        )

        report = _parse_llm_response(content_text)
        return _validate_report(report)

    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON for %s: %s", name, e)
        report = _fallback_report(capabilities)
        report["summary"] = f"LLM returned invalid JSON, fell back to static analysis. Error: {e}"
        return report

    except Exception as e:
        logger.error("LLM review failed for %s: %s", name, e)
        report = _fallback_report(capabilities)
        report["summary"] = f"LLM review failed, fell back to static analysis. Error: {e}"
        return report
