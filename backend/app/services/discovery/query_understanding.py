import json
import logging
from dataclasses import dataclass, field

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.prompts.query_understanding import build_query_understanding_prompt

logger = logging.getLogger(__name__)


@dataclass
class QueryUnderstanding:
    keywords: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    intent: str = "find_skill"


def _parse_response(raw: str) -> QueryUnderstanding:
    text = raw.strip()
    if "```" in text:
        parts = text.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 1 and part.strip():
                text = part.strip()
                if text.startswith("json"):
                    text = text[4:].strip()
                break

    data = json.loads(text)
    return QueryUnderstanding(
        keywords=data.get("keywords", []),
        tags=data.get("tags", []),
        capabilities=data.get("capabilities", []),
        intent=data.get("intent", "find_skill"),
    )


async def understand_query(query: str) -> QueryUnderstanding:
    settings = get_settings()
    if not settings.LLM_API_KEY or settings.LLM_API_KEY == "sk-your-api-key-here":
        return _fallback_understanding(query)

    try:
        client = AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_API_BASE)
        messages = build_query_understanding_prompt(query)
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=300,
            timeout=15.0,
        )
        content = response.choices[0].message.content or ""
        return _parse_response(content)
    except Exception as e:
        logger.warning("Query understanding failed, using fallback: %s", e)
        return _fallback_understanding(query)


def _fallback_understanding(query: str) -> QueryUnderstanding:
    words = query.lower().split()
    stop_words = {"the", "a", "an", "is", "are", "for", "to", "how", "do", "i", "can", "what", "which", "with"}
    keywords = [w.strip(".,?!") for w in words if w not in stop_words and len(w) > 1]

    tag_hints: list[str] = []
    tag_map = {
        "python": ["python", "py"],
        "javascript": ["javascript", "js", "node"],
        "typescript": ["typescript", "ts"],
        "security": ["security", "safe", "audit", "scan"],
        "testing": ["test", "testing", "tdd", "unit"],
        "devops": ["devops", "deploy", "ci", "cd", "pipeline"],
        "docker": ["docker", "container"],
        "git": ["git", "commit", "branch", "merge"],
        "database": ["database", "db", "sql", "migrat"],
        "api": ["api", "rest", "endpoint", "http"],
        "ai": ["ai", "llm", "gpt", "model", "prompt"],
        "web": ["web", "html", "css", "frontend", "backend"],
        "automation": ["automat", "workflow", "script"],
        "monitoring": ["monitor", "log", "observ"],
        "documentation": ["doc", "readme", "markdown", "md"],
        "data": ["data", "transform", "etl", "process"],
    }
    for tag, triggers in tag_map.items():
        for kw in keywords:
            if any(trigger in kw for trigger in triggers):
                tag_hints.append(tag)
                break

    cap_hints: list[str] = []
    cap_map = {
        "file_read": ["read", "file", "parse", "load"],
        "file_write": ["write", "save", "create", "generat"],
        "network_access": ["http", "api", "fetch", "request", "web", "download"],
        "code_exec": ["run", "execut", "eval", "code"],
        "shell_exec": ["shell", "bash", "command", "terminal", "cli"],
        "process_exec": ["process", "subprocess", "spawn"],
    }
    for cap, triggers in cap_map.items():
        for kw in keywords:
            if any(trigger in kw for trigger in triggers):
                cap_hints.append(cap)
                break

    return QueryUnderstanding(
        keywords=keywords[:3],
        tags=tag_hints[:5],
        capabilities=cap_hints[:5],
        intent="find_skill",
    )
