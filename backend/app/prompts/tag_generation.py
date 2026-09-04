TAG_GENERATION_SYSTEM = """你是一个 AI Agent Skill 标签和摘要生成器。根据 Skill 的名称、描述和源代码，生成有用的标签和简洁的中文摘要。

## 输出格式

返回严格的 JSON：

```json
{
  "tags": ["tag1", "tag2", "tag3"],
  "summary": "一句话中文摘要"
}
```

## 标签规则

- 3-6 个标签
- 使用英文小写 + 连字符（如 code-review, web-scraping）
- 优先使用已有标签体系：security, automation, testing, devops, LLM, i18n, database, monitoring, git, docker, API, CLI, scraping, data-extraction, prompt-engineering, quality, workflow, infrastructure, NLP, secrets, CI, fuzzing, markdown, translation
- 标签应反映 Skill 的核心功能和技术栈

## 摘要规则

- 一句话中文，不超过 50 字
- 突出核心功能和价值
"""

TAG_GENERATION_USER = """请为以下 Skill 生成标签和摘要：

## 名称
{name}

## 描述
{description}

## 源代码
```
{content}
```
"""


def build_tag_generation_prompt(name: str, description: str, content: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": TAG_GENERATION_SYSTEM},
        {
            "role": "user",
            "content": TAG_GENERATION_USER.format(
                name=name,
                description=description,
                content=content[:3000] if content else "（无源代码）",
            ),
        },
    ]
