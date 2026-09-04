from app.models.skill import Skill


RISK_PENALTY = {
    "safe": 0.0,
    "low": 0.05,
    "medium": 0.15,
    "high": 0.30,
    "critical": 0.50,
    "pending": 0.10,
}


def compute_ranking_score(
    skill: Skill,
    relevance_score: float = 0.0,
) -> float:
    popularity = _normalize_popularity(skill)
    quality = _normalize_quality(skill)
    security_risk = RISK_PENALTY.get(skill.risk_level, 0.10)

    score = (
        0.45 * relevance_score
        + 0.20 * popularity
        + 0.20 * quality
        - 0.15 * security_risk
    )
    return round(max(0.0, min(1.0, score)), 4)


def rank_skills(
    results: list[dict],
) -> list[dict]:
    for item in results:
        skill = item["skill"]
        relevance = item.get("relevance_score", 0.0)
        item["ranking_score"] = compute_ranking_score(skill, relevance)

    results.sort(key=lambda x: x["ranking_score"], reverse=True)
    return results


def _normalize_popularity(skill: Skill) -> float:
    downloads = min(skill.downloads or 0, 100000)
    stars = min(skill.stars or 0, 10000)
    installs = min(skill.install_count or 0, 50000)

    dl_score = downloads / 100000
    star_score = stars / 10000
    install_score = installs / 50000

    return 0.4 * dl_score + 0.35 * star_score + 0.25 * install_score


def _normalize_quality(skill: Skill) -> float:
    score = 0.0

    if skill.version:
        score += 0.15

    if skill.content and len(skill.content) > 100:
        score += 0.25
    elif skill.content:
        score += 0.1

    if skill.tags and len(skill.tags) >= 3:
        score += 0.15
    elif skill.tags:
        score += 0.05

    if skill.capabilities and len(skill.capabilities) >= 2:
        score += 0.15

    security_score = skill.security_score or 0
    score += 0.30 * (security_score / 100)

    return min(1.0, score)
