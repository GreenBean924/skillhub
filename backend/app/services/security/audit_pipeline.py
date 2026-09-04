import asyncio
import json
import logging
from datetime import UTC, datetime

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.prompts.security_review import build_security_review_prompt
from app.services.security.capability_analyzer import analyze_capabilities
from app.services.security.metadata_analyzer import analyze_metadata
from app.services.security.prompt_analyzer import analyze_prompts
from app.services.security.static_scanner import scan_content

logger = logging.getLogger(__name__)

VALID_RISK_LEVELS = {"safe", "low", "medium", "high", "critical", "pending"}
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


def _build_layer_context(
    name: str,
    description: str,
    author: str,
    tags: list[str],
    capabilities: list[str],
    content: str,
) -> dict:
    metadata = analyze_metadata(name, description, author, tags, capabilities)
    capability = analyze_capabilities(content)
    static = scan_content(content)
    prompt = analyze_prompts(content, tags)

    return {
        "metadata": metadata.to_context(),
        "capability": capability.to_context(),
        "static": static.to_context(),
        "prompt": prompt.to_context(),
    }


def _build_enhanced_prompt(
    name: str,
    description: str,
    author: str,
    tags: list[str],
    capabilities: list[str],
    content: str,
    layer_context: dict,
) -> list[dict[str, str]]:
    base_messages = build_security_review_prompt(
        name=name,
        description=description,
        author=author,
        tags=tags,
        capabilities=capabilities,
        content=content,
    )

    context_summary = _format_layer_context(layer_context)

    enhanced_user_content = base_messages[1]["content"]
    if context_summary:
        enhanced_user_content += f"\n\n## 自动化分析结果\n\n{context_summary}\n\n请结合以上自动化分析结果，给出更准确的安全评估。"

    base_messages[1]["content"] = enhanced_user_content
    return base_messages


def _format_layer_context(ctx: dict) -> str:
    parts = []

    metadata = ctx.get("metadata", {})
    if metadata.get("declared_purpose"):
        parts.append(f"**声明用途**: {metadata['declared_purpose']}")
    if metadata.get("suspicious_metadata"):
        suspicious = "; ".join(s.get("reason", "") for s in metadata["suspicious_metadata"])
        parts.append(f"**元数据疑点**: {suspicious}")

    static_findings = ctx.get("static", {}).get("static_findings", [])
    if static_findings:
        high_severity = [f for f in static_findings if f["severity"] in ("high", "critical")]
        if high_severity:
            parts.append(f"**高危静态发现 ({len(high_severity)})**:")
            for f in high_severity[:5]:
                parts.append(f"  - [{f['severity']}] {f['title']}: `{f['evidence'][:80]}`")
        medium_severity = [f for f in static_findings if f["severity"] == "medium"]
        if medium_severity:
            parts.append(f"**中危静态发现 ({len(medium_severity)})**: {', '.join(f['title'] for f in medium_severity[:5])}")

    prompt_findings = ctx.get("prompt", {}).get("prompt_findings", [])
    if prompt_findings:
        parts.append(f"**提示词分析发现 ({len(prompt_findings)})**:")
        for f in prompt_findings[:3]:
            parts.append(f"  - [{f['severity']}] {f['title']}: `{f['evidence'][:80]}`")

    if ctx.get("prompt", {}).get("contains_instructions"):
        parts.append("**注意**: 内容包含指令式文本，可能不是纯代码")

    return "\n".join(parts)


def _merge_findings(
    layer_context: dict,
    llm_findings: list[dict],
) -> list[dict]:
    seen_evidence = set()
    merged = []

    for finding in llm_findings:
        evidence_key = finding.get("evidence", "")[:50]
        if evidence_key and evidence_key not in seen_evidence:
            seen_evidence.add(evidence_key)
            merged.append(finding)

    static_findings = layer_context.get("static", {}).get("static_findings", [])
    for sf in static_findings:
        if sf["severity"] in ("high", "critical"):
            evidence_key = sf.get("evidence", "")[:50]
            if evidence_key and evidence_key not in seen_evidence:
                seen_evidence.add(evidence_key)
                merged.append({
                    "id": f"S{len(merged) + 1:03d}",
                    "severity": sf["severity"],
                    "title": sf["title"],
                    "description": f"Static scan detected: {sf['title']}",
                    "evidence": sf["evidence"],
                    "recommendation": "Review this pattern and verify it aligns with expected behavior",
                })

    prompt_findings = layer_context.get("prompt", {}).get("prompt_findings", [])
    for pf in prompt_findings:
        if pf["severity"] in ("high", "critical"):
            evidence_key = pf.get("evidence", "")[:50]
            if evidence_key and evidence_key not in seen_evidence:
                seen_evidence.add(evidence_key)
                merged.append({
                    "id": f"P{len(merged) + 1:03d}",
                    "severity": pf["severity"],
                    "title": pf["title"],
                    "description": f"Prompt analysis detected: {pf['title']}",
                    "evidence": pf["evidence"],
                    "recommendation": "Review this instruction pattern for potential malicious intent",
                })

    return merged


async def review_skill(
    name: str,
    description: str,
    author: str,
    tags: list[str],
    capabilities: list[str],
    content: str,
) -> dict:
    settings = get_settings()

    layer_context = _build_layer_context(name, description, author, tags, capabilities, content)

    if not settings.LLM_API_KEY or settings.LLM_API_KEY.startswith("sk-your"):
        logger.warning("LLM_API_KEY not configured, falling back to static analysis")
        report = _fallback_report(capabilities)
        report["findings"] = _merge_findings(layer_context, report["findings"])
        report["layer_context"] = layer_context
        return report

    messages = _build_enhanced_prompt(
        name, description, author, tags, capabilities, content, layer_context
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
        report = _validate_report(report)
        report["findings"] = _merge_findings(layer_context, report["findings"])
        report["layer_context"] = layer_context
        return report

    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON for %s: %s", name, e)
        report = _fallback_report(capabilities)
        report["summary"] = f"LLM returned invalid JSON, fell back to static analysis. Error: {e}"
        report["findings"] = _merge_findings(layer_context, report["findings"])
        report["layer_context"] = layer_context
        return report

    except Exception as e:
        logger.error("LLM review failed for %s: %s", name, e)
        report = _fallback_report(capabilities)
        report["summary"] = f"LLM review failed, fell back to static analysis. Error: {e}"
        report["findings"] = _merge_findings(layer_context, report["findings"])
        report["layer_context"] = layer_context
        return report
