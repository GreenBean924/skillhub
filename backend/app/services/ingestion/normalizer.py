import re
import unicodedata


def _generate_slug(name: str) -> str:
    slug = unicodedata.normalize("NFKD", name)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = slug.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    return slug


def normalize_skills(skills: list[dict]) -> list[dict]:
    seen_slugs: set[str] = set()
    result: list[dict] = []

    for skill in skills:
        if not skill.get("name"):
            continue

        if not skill.get("slug"):
            skill["slug"] = _generate_slug(skill["name"])

        slug = skill["slug"]
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        skill.setdefault("description", "")
        skill.setdefault("author", "unknown")
        skill.setdefault("tags", [])
        skill.setdefault("capabilities", [])
        skill.setdefault("risk_level", "pending")
        skill.setdefault("security_score", 0)
        skill.setdefault("security_report", {})
        skill.setdefault("downloads", 0)
        skill.setdefault("stars", 0)
        skill.setdefault("content", "")
        skill.setdefault("version", None)
        skill.setdefault("registry", None)
        skill.setdefault("source_url", None)
        skill.setdefault("install_command", None)

        result.append(skill)

    return result
