from abc import ABC, abstractmethod


class Collector(ABC):
    @abstractmethod
    async def collect(self) -> list[dict]:
        ...


class SeedDataCollector(Collector):
    def __init__(self, skills_data: list[dict]):
        self._skills_data = skills_data

    async def collect(self) -> list[dict]:
        return [dict(skill) for skill in self._skills_data]


class SkillsShCollector(Collector):
    """
    Collects skills from skills.sh by scraping the listing page,
    fetching individual skill details, and retrieving SKILL.md content
    from the corresponding GitHub repositories.
    """

    BASE_URL = "https://skills.sh"
    LISTING_URL = "https://skills.sh"
    RAW_GITHUB_BASE = "https://raw.githubusercontent.com"

    def __init__(
        self,
        max_skills: int = 50,
        request_timeout: float = 15.0,
        rate_limit_delay: float = 1.0,
    ):
        self._max_skills = max_skills
        self._timeout = request_timeout
        self._rate_limit_delay = rate_limit_delay

    async def collect(self) -> list[dict]:
        """
        Main entry point: scrape the skills.sh listing page, then fetch
        detail and content for each skill. Returns a list of skill dicts
        compatible with the ingestion pipeline normalizer.
        """
        import asyncio
        import logging

        logger = logging.getLogger(__name__)
        skills: list[dict] = []

        try:
            logger.info("SkillsShCollector: fetching listing page from %s", self.LISTING_URL)
            html = await self._fetch_listing_page()
        except Exception as e:
            logger.error("SkillsShCollector: failed to fetch listing page: %s", e)
            return skills

        listings = self._parse_skill_listings(html)
        logger.info("SkillsShCollector: found %d skill listings on skills.sh", len(listings))

        # Limit to max_skills to avoid excessive scraping
        listings = listings[: self._max_skills]

        for i, listing in enumerate(listings):
            owner = listing.get("owner", "")
            repo = listing.get("repo", "")

            if not owner or not repo:
                logger.warning("SkillsShCollector: skipping listing with missing owner/repo at index %d", i)
                continue

            try:
                logger.info("SkillsShCollector: [%d/%d] fetching detail for %s/%s", i + 1, len(listings), owner, repo)
                detail = await self._fetch_skill_detail(owner, repo)

                if detail is None:
                    logger.warning("SkillsShCollector: no detail returned for %s/%s", owner, repo)
                    continue

                # Merge listing metadata into detail
                detail.setdefault("owner", owner)
                detail.setdefault("repo", repo)
                detail.setdefault("name", listing.get("name", f"{owner}/{repo}"))
                detail.setdefault("source_url", listing.get("source_url", f"{self.BASE_URL}/s/{owner}/{repo}"))

                # Fetch SKILL.md content from GitHub
                github_url = detail.get("github_url") or f"https://github.com/{owner}/{repo}"
                logger.info("SkillsShCollector: [%d/%d] fetching SKILL.md for %s/%s", i + 1, len(listings), owner, repo)
                content = await self._fetch_skill_content(github_url)
                detail["content"] = content

                # Build the final skill dict in the shape the pipeline expects
                slug = f"{owner}-{repo}".lower().replace("/", "-").replace("_", "-")
                install_command = detail.get("install_command") or f"npx skills add {owner}/{repo}"

                skill_dict = {
                    "slug": slug,
                    "name": detail.get("name", f"{owner}/{repo}"),
                    "author": owner,
                    "description": detail.get("description", ""),
                    "tags": detail.get("tags", []),
                    "capabilities": detail.get("capabilities", []),
                    "source_url": detail.get("source_url", f"{self.BASE_URL}/s/{owner}/{repo}"),
                    "registry": "skills_sh",
                    "content": content,
                    "install_command": install_command,
                }
                skills.append(skill_dict)

            except Exception as e:
                logger.error("SkillsShCollector: error processing %s/%s: %s", owner, repo, e)

            # Polite rate limiting between requests
            if i < len(listings) - 1:
                await asyncio.sleep(self._rate_limit_delay)

        logger.info("SkillsShCollector: collection complete, %d skills gathered", len(skills))
        return skills

    async def _fetch_listing_page(self) -> str:
        """Fetch the HTML from the skills.sh listing page."""
        import httpx

        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.get(self.LISTING_URL)
            response.raise_for_status()
            return response.text

    def _parse_skill_listings(self, html: str) -> list[dict]:
        """
        Parse skill entries from the skills.sh listing page HTML.

        skills.sh renders a list of skills with links in the pattern /s/{owner}/{repo}.
        We extract these using regex to avoid requiring BeautifulSoup as a dependency.
        """
        import re

        listings: list[dict] = []
        seen: set[str] = set()

        # Match links like /s/owner/repo or https://www.skills.sh/s/owner/repo
        pattern = r'href=["\'](?:https?://(?:www\.)?skills\.sh)?/s/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)["\']'
        matches = re.findall(pattern, html)

        for owner, repo in matches:
            key = f"{owner}/{repo}"
            if key in seen:
                continue
            seen.add(key)

            listings.append({
                "owner": owner,
                "repo": repo,
                "name": f"{owner}/{repo}",
                "source_url": f"{self.BASE_URL}/s/{owner}/{repo}",
            })

        return listings

    async def _fetch_skill_detail(self, owner: str, repo: str) -> dict | None:
        """
        Fetch the individual skill detail page from skills.sh.
        Returns a dict with name, description, tags, capabilities, install_command, github_url.
        Returns None if the page cannot be fetched.
        """
        import logging
        import re
        import httpx

        logger = logging.getLogger(__name__)
        url = f"{self.BASE_URL}/s/{owner}/{repo}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text
        except httpx.HTTPStatusError as e:
            logger.warning("SkillsShCollector: HTTP %s fetching %s", e.response.status_code, url)
            return None
        except Exception as e:
            logger.warning("SkillsShCollector: failed to fetch detail page %s: %s", url, e)
            return None

        detail: dict = {
            "name": f"{owner}/{repo}",
            "description": "",
            "tags": [],
            "capabilities": [],
            "install_command": f"npx skills add {owner}/{repo}",
            "github_url": f"https://github.com/{owner}/{repo}",
            "source_url": url,
        }

        # Try to extract a description from meta tags or page content
        desc_match = re.search(
            r'<meta\s+(?:name|property)=["\'](?:description|og:description)["\']\s+content=["\']([^"\']*)["\']',
            html,
            re.IGNORECASE,
        )
        if desc_match:
            detail["description"] = desc_match.group(1).strip()

        # Try to extract a GitHub link from the page
        gh_match = re.search(r'href=["\']?(https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)["\']?', html)
        if gh_match:
            detail["github_url"] = gh_match.group(1)

        # Try to extract install command if shown on the page
        install_match = re.search(r'npx\s+skills\s+add\s+[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', html)
        if install_match:
            detail["install_command"] = install_match.group(0)

        # Try to extract tags from the page (look for tag-like elements)
        tag_matches = re.findall(r'<(?:span|a|div)[^>]*class=["\'][^"\']*tag[^"\']*["\'][^>]*>([^<]+)</', html, re.IGNORECASE)
        if tag_matches:
            detail["tags"] = [t.strip() for t in tag_matches if t.strip()]

        # If no description found, try to extract from first <p> or title
        if not detail["description"]:
            title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
            if title_match:
                detail["description"] = title_match.group(1).strip()

        return detail

    async def _fetch_skill_content(self, github_url: str) -> str:
        """
        Fetch the SKILL.md content from the GitHub repository.
        Tries the raw.githubusercontent.com URL for common SKILL.md paths.
        Falls back to the GitHub API if raw fetch fails.
        Returns empty string if content cannot be fetched.
        """
        import logging
        import re
        import httpx

        logger = logging.getLogger(__name__)

        # Parse owner/repo from the GitHub URL
        match = re.search(r'github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)', github_url)
        if not match:
            logger.warning("SkillsShCollector: could not parse owner/repo from %s", github_url)
            return ""

        owner, repo = match.group(1), match.group(2)
        # Clean up repo name (remove trailing slashes, etc.)
        repo = repo.rstrip("/")

        # Try common paths for SKILL.md
        candidate_paths = [
            f"{self.RAW_GITHUB_BASE}/{owner}/{repo}/main/SKILL.md",
            f"{self.RAW_GITHUB_BASE}/{owner}/{repo}/master/SKILL.md",
            f"{self.RAW_GITHUB_BASE}/{owner}/{repo}/main/skill.md",
            f"{self.RAW_GITHUB_BASE}/{owner}/{repo}/master/skill.md",
            f"{self.RAW_GITHUB_BASE}/{owner}/{repo}/main/SKILL.MD",
        ]

        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            for url in candidate_paths:
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        logger.info("SkillsShCollector: fetched SKILL.md from %s", url)
                        return response.text
                except Exception:
                    continue

        # Try GitHub API as fallback
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(api_url)
                if response.status_code == 200:
                    files = response.json()
                    if isinstance(files, list):
                        for f in files:
                            name = f.get("name", "").upper()
                            if name in ("SKILL.MD", "README.MD"):
                                download_url = f.get("download_url")
                                if download_url:
                                    content_resp = await client.get(download_url)
                                    if content_resp.status_code == 200:
                                        logger.info("SkillsShCollector: fetched %s via GitHub API for %s/%s", f.get("name"), owner, repo)
                                        return content_resp.text
        except Exception as e:
            logger.warning("SkillsShCollector: GitHub API fallback failed for %s/%s: %s", owner, repo, e)

        logger.warning("SkillsShCollector: could not fetch SKILL.md for %s/%s", owner, repo)
        return ""
