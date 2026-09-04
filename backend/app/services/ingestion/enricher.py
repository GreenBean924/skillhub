import json
import logging

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.prompts.tag_generation import build_tag_generation_prompt

logger = logging.getLogger(__name__)


class Enricher:
    def __init__(self):
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_API_BASE,
        )
        self._model = settings.LLM_MODEL

    async def generate_tags_and_summary(
        self, name: str, description: str, content: str
    ) -> dict:
        settings = get_settings()
        if not settings.LLM_API_KEY or settings.LLM_API_KEY.startswith("sk-your"):
            logger.warning("LLM not configured, skipping tag generation")
            return {"tags": [], "summary": description}

        messages = build_tag_generation_prompt(name, description, content)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                timeout=20.0,
            )

            text = response.choices[0].message.content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                text = "\n".join(lines)

            data = json.loads(text)
            return {
                "tags": data.get("tags", []),
                "summary": data.get("summary", description),
            }

        except Exception as e:
            logger.error("Tag generation failed for %s: %s", name, e)
            return {"tags": [], "summary": description}
