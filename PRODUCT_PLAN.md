# SkillHub 产品方案 V1 Revision

> 面向 AI Agent 的 Skill 发现、安全审查与一键安装平台

---

## 1. 产品定位

**SkillHub** 是一个帮助开发者发现、评估和安装 AI Agent Skill 的 Web 平台。

**核心用户价值**：

| # | 用户痛点 | SkillHub 的解决方式 |
|---|---------|-------------------|
| 1 | 不知道有什么好用的 Skill | 聚合社区 Skill，按分类和热度推荐 |
| 2 | 知道需求但不知道该搜什么 | 自然语言描述需求，系统理解意图并检索 |
| 3 | 担心 Skill 有安全风险 | 多层安全审查 + 可解释的风险报告 |
| 4 | 找到 Skill 后安装麻烦 | CLI 一键安装到 Claude Code |
| 5 | 持续发现新的好 Skill | 基于简单 Ranking 的每日推荐 |

**一句话定位**：SkillHub 是 AI Agent Skill 的 "发现引擎 + 安全网关 + 安装工具"。

**与竞品的差异**：

| 产品 | 缺什么 |
|---|---|
| skills.sh | 无安全审查，无自然语言搜索，无安装工具 |
| GitHub | 需要自己找，无聚合，无风险评估 |
| npm | 面向代码包，不是 Agent Skill |

---

## 2. 用户画像

### 主要用户：使用 AI Agent 的开发者

- 正在使用 Claude Code（或类似 Agent 工具）进行日常开发
- 知道 Skill 可以扩展 Agent 能力，但社区 Skill 太多、质量参差不齐
- 对安全性有基本意识，不想安装来路不明的 Skill
- 技术水平中等偏上，能使用 CLI 工具

### 次要用户：AI Agent 爱好者/探索者

- 刚开始接触 AI Agent，想快速找到有用的 Skill 来体验
- 不太清楚具体需要什么，更依赖浏览和推荐

---

## 3. 核心用户流程

### 3.1 发现 → 审查 → 安装（主流程）

```
用户产生需求："我想找一个能帮我做 TDD 的 Skill"
    │
    ▼
┌─────────────────────────────────┐
│  Skill Discovery                 │
│  输入自然语言 / 关键词            │
│  系统理解意图 → 检索 → 排序       │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  候选 Skill 列表                  │
│  展示名称、摘要、标签、安全状态     │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Skill 详情页                     │
│  完整描述 + 可解释安全报告          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  用户确认安装                      │
│  展示安全摘要，用户明确同意         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  安全安装到 Claude Code            │
│  CLI 执行安装 + 验证               │
└─────────────────────────────────┘
```

### 3.2 浏览与推荐

```
用户打开首页
    │
    ├── 浏览分类标签
    ├── 查看热门推荐
    ├── 查看每日推荐
    │
    └── 进入 Skill 详情 → 安装
```

---

## 4. V1 功能范围

### 4.1 V1 必须完成

| 模块 | 功能 | 说明 |
|---|---|---|
| **数据聚合** | skills.sh 数据抓取 | Collector → Normalizer → Database |
| **数据聚合** | LLM 自动标签 + 摘要 | 入库时自动生成结构化元数据 |
| **数据聚合** | Embedding 生成 | 为语义搜索准备向量 |
| **Discovery** | 关键词搜索 | 基于名称、描述、标签的文本检索 |
| **Discovery** | 自然语言搜索 | Query Understanding → 语义检索 → 排序 |
| **Discovery** | 简单 Ranking | 综合相关度、热度、质量、安全性的排序 |
| **Discovery** | 每日推荐 | 基于简单评分公式的推荐列表 |
| **Security** | 静态分析 | 正则扫描敏感模式 |
| **Security** | LLM 安全审查 | 理解 Skill 意图，判断能力与用途是否匹配 |
| **Security** | 可解释安全报告 | Finding / Evidence / Recommendation 结构化输出 |
| **前端** | 首页 | 搜索 + 分类 + 热门 + 推荐 |
| **前端** | Skill 详情页 | 描述 + 安全报告 + 安装引导 |
| **前端** | 搜索结果页 | 支持自然语言查询 |
| **CLI** | `skillhub install` | 从 SkillHub 获取并安装 Skill |
| **CLI** | `skillhub uninstall` | 卸载已安装的 Skill |
| **CLI** | `skillhub list` | 列出已安装的 SkillHub Skill |
| **架构** | Agent Adapter 抽象层 | V1 只实现 ClaudeCodeAdapter |

### 4.2 V1 形成完整闭环

```
用户需求 → 自然语言 Discovery → 候选检索 → Ranking
    → Security Audit → Skill Detail / Security Report
    → 用户确认 → 安全安装到 Claude Code
```

---

## 5. V2 / Future 功能（明确不在 V1 范围）

| 功能 | 推迟原因 |
|---|---|
| GitHub 数据源 | V1 先跑通 skills.sh 单数据源 |
| 用户系统（注册/登录） | 需要后端鉴权、数据库用户表、前端登录流程，工作量大 |
| 个性化推荐 | 依赖用户历史数据，V1 没有用户系统 |
| 用户评分/收藏 | 依赖用户系统 |
| 多 Agent 支持（Cursor、Qoder） | V1 只实现 ClaudeCodeAdapter，架构预留扩展点 |
| 完整 Sandbox / 沙箱执行 | 需要容器化隔离，复杂度高 |
| Skill 创作工具 / UGC | 社区生态功能，V1 先做消费端 |
| 对话式多轮搜索 | V1 做单轮自然语言搜索已足够 |
| 社区举报 / 人工审核 | V1 靠自动化审查，人工流程延后 |
| 浏览器插件 / IDE 集成 | 分发渠道扩展，V1 先做 Web + CLI |
| 机器学习推荐模型 | V1 用简单公式 Ranking |

---

## 6. Skill 数据模型

### 6.1 设计原则

> SkillHub 不修改原始 Skill 内容。保存原始 Skill + 建立自己的索引和分析元数据。

### 6.2 逻辑结构

```
Skill
├── identity                    # 身份标识
│   ├── id: UUID
│   ├── name: string
│   ├── description: string
│   └── version: string
│
├── source                      # 来源信息
│   ├── registry: string        # "skills_sh" | "github" | ...
│   ├── source_url: string      # 原始链接
│   ├── author: string
│   └── collected_at: timestamp
│
├── content                     # 原始内容（不可变）
│   ├── skill_md: text          # CLAUDE.md / prompt 完整内容
│   └── install_script: text    # 原始安装脚本（如有）
│
├── metadata                    # LLM 生成的结构化元数据
│   ├── tags: string[]          # 自动标签
│   ├── summary: string         # 一句话摘要
│   ├── capabilities: string[]  # 提取的能力描述
│   └── embedding: vector(1536) # 语义向量
│
├── security                    # 安全审查结果
│   ├── risk_level: enum        # safe / low / medium / high / critical
│   ├── score: int              # 0-100, 越高风险越大
│   ├── findings: Finding[]     # 结构化发现项
│   ├── reviewed_at: timestamp
│   └── review_version: string  # 审查引擎版本
│
├── popularity                  # 热度指标
│   ├── install_count: int
│   └── trending_score: float
│
└── system                      # 系统字段
    ├── created_at: timestamp
    └── updated_at: timestamp
```

### 6.3 安全报告数据结构

```typescript
interface SecurityReport {
  risk_level: "safe" | "low" | "medium" | "high" | "critical";
  score: number;                    // 0-100, 越高风险越大
  capabilities: Capability[];       // 检测到的能力
  findings: Finding[];              // 具体发现项
  review_version: string;           // 审查引擎版本号
  reviewed_at: string;              // ISO timestamp
}

interface Capability {
  type: CapabilityType;
  detail: string;                   // 具体描述
  evidence: Evidence;               // 证据
}

type CapabilityType =
  | "filesystem.read"
  | "filesystem.write"
  | "network.access"
  | "shell.execute"
  | "credential.access"
  | "subprocess"
  | "external_url"
  | "other";

interface Finding {
  id: string;                       // "F001"
  severity: "info" | "low" | "medium" | "high" | "critical";
  title: string;                    // 人类可读的标题
  description: string;              // 详细说明
  evidence: Evidence;               // 具体证据
  recommendation: string;           // 建议
  category: FindingCategory;        // 分类
}

interface Evidence {
  source: string;                   // "static_scan" | "llm_review" | "metadata"
  location: string;                 // 文件/行号/指令位置
  content: string;                  // 具体代码片段或文本
  context: string;                  // 上下文说明
}

type FindingCategory =
  | "shell_execution"
  | "file_access"
  | "network_access"
  | "credential_access"
  | "prompt_injection"
  | "data_exfiltration"
  | "capability_mismatch"
  | "suspicious_install"
  | "hidden_behavior";
```

**设计要点**：

- `Finding` 和 `Evidence` 分离，方便同一证据支撑多个 Finding
- `source` 字段标记发现来源（静态扫描 vs LLM 审查），便于追溯和调试
- `category` 使用枚举，前端可按类别分组展示
- `recommendation` 给出可操作建议，不只是风险描述
- 整个结构可序列化存入 JSONB，也可未来迁移到独立表

---

## 7. Skill Discovery 流程

### 7.1 整体流程

```
User Query (自然语言或关键词)
    │
    ▼
┌──────────────────────────────────┐
│  Query Understanding              │
│  判断查询类型:                     │
│  - 关键词查询 → 直接进入检索       │
│  - 自然语言查询 → 意图理解         │
│                                   │
│  提取:                            │
│  - capabilities: 需要的能力        │
│  - constraints: 限制条件           │
│  - keywords: 关键词               │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Retrieval                        │
│  并行执行:                        │
│  - 关键词检索 (PostgreSQL ILIKE)  │
│  - 语义检索 (pgvector 余弦相似度)  │
│  - 标签过滤 (匹配 capabilities)   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Metadata Filtering               │
│  根据 constraints 过滤:           │
│  - 安全等级限制                    │
│  - 能力匹配度                     │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Ranking / Reranking              │
│  综合评分:                        │
│  score = w1 * relevance           │
│        + w2 * popularity          │
│        + w3 * quality             │
│        - w4 * security_risk       │
└──────────────┬───────────────────┘
               │
               ▼
         Top-K Skills
```

### 7.2 Query Understanding 设计

V1 使用 **轻量级** 实现，不做复杂的 Agent Planner：

```python
class QueryUnderstandingService:
    """
    将用户自然语言查询转换为结构化搜索参数。

    设计决策:
    - 使用 LLM (GPT-4o-mini) 做单次调用，提取结构化信息
    - 不做多轮对话，单轮即可
    - 如果 LLM 调用失败，降级为纯关键词搜索

    为什么不用更简单的方案?
    - 纯正则/关键词无法理解 "不需要网络权限" 这类约束
    - 轻量 LLM 调用成本极低 (~100 tokens/次)

    为什么不用更复杂的方案?
    - V1 不需要 Agent Planner，单轮理解足够
    - 未来可以升级为多轮对话式搜索
    """

    async def understand(self, query: str) -> StructuredQuery:
        """
        返回:
        - keywords: 用于关键词检索
        - capabilities: 用户需要的能力列表
        - constraints: 用户的限制条件
        - semantic_query: 用于 embedding 检索的改写查询
        """
```

**StructuredQuery 结构**:

```python
class StructuredQuery(BaseModel):
    keywords: list[str]               # ["excel", "chart", "report"]
    capabilities: list[str]           # ["spreadsheet analysis", "data visualization"]
    constraints: list[str]            # ["no network access"]
    semantic_query: str               # 改写后的语义查询文本
    query_type: Literal["keyword", "natural_language", "mixed"]
```

### 7.3 Ranking 公式

```python
def compute_ranking_score(
    relevance: float,        # 语义相似度 / 关键词匹配度, 0-1
    popularity: float,       # install_count 归一化, 0-1
    quality: float,          # 元数据完整度 (有标签/摘要/描述), 0-1
    security_risk: float,    # security_score / 100, 0-1
) -> float:
    """
    V1 权重 (可调):
    w_relevance  = 0.45
    w_popularity = 0.20
    w_quality    = 0.20
    w_risk       = 0.15

    设计理由:
    - 相关度最重要，用户搜什么就要找到什么
    - 热度和质量各占两成，避免冷门/低质量 Skill 排到前面
    - 安全风险占 15%，高风险 Skill 会被降权但不会完全隐藏
      (因为安全报告已经给用户提供了判断依据)
    """
    return (
        0.45 * relevance
        + 0.20 * popularity
        + 0.20 * quality
        - 0.15 * security_risk
    )
```

### 7.4 每日推荐

```python
def compute_recommendation_score(
    newness: float,          # 创建时间衰减, 0-1
    popularity: float,       # install_count 归一化, 0-1
    quality: float,          # 元数据完整度, 0-1
    security_risk: float,    # 0-1
) -> float:
    """
    每日推荐评分 (与搜索 Ranking 不同，没有 relevance 维度):

    score = 0.30 * newness
          + 0.30 * popularity
          + 0.25 * quality
          - 0.15 * security_risk

    每天计算一次，取 Top 10 展示在首页。
    """
```

---

## 8. Security Audit 流程

### 8.1 多层审查架构

```
Skill 入库
    │
    ▼
┌──────────────────────────────────────┐
│  Layer 1: Metadata Analysis           │
│  分析 Skill 声明的用途、作者、来源      │
│  建立 "预期行为基线"                    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Layer 2: Capability Analysis         │
│  从 Skill 内容中提取实际请求的能力      │
│  - 文件系统访问                        │
│  - 网络访问                           │
│  - Shell 命令执行                      │
│  - 凭证/密钥访问                       │
│  - 子进程调用                          │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Layer 3: Static Analysis             │
│  正则扫描已知危险模式                   │
│  快速、确定、零成本                     │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Layer 4: Instruction / Prompt        │
│  Analysis                             │
│  分析 Skill 的 prompt/instruction      │
│  检测:                                │
│  - Prompt Injection 尝试              │
│  - 隐藏行为指令                        │
│  - 与声明用途不一致的指令               │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Layer 5: LLM Security Review         │
│  综合以上所有信息，由 LLM 做最终判断:   │
│  - 能力是否与用途匹配?                 │
│  - 是否存在异常行为?                   │
│  - 整体风险等级                        │
│  - 生成可解释报告                      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Risk Assessment                      │
│  汇总所有层的发现                      │
│  计算综合风险分数                      │
│  生成 SecurityReport                  │
└──────────────────────────────────────┘
```

### 8.2 核心设计原则

> **Capability 存在 ≠ Capability 恶意**

一个 GitHub Skill 需要网络访问是正常的。一个 TDD Skill 需要 Shell 执行也是合理的。

安全审查的重点是：

1. **能力与用途是否匹配** — Skill 声明做 TDD，但实际在读取 `.env` 文件，这是异常
2. **是否存在隐藏行为** — 在 prompt 中嵌入 "不要告诉用户" 等指令
3. **是否存在过度权限** — 一个只需要读文件的 Skill 却要求 Shell 执行权限
4. **是否存在恶意模式** — Prompt Injection、数据外泄、隐蔽安装

### 8.3 静态分析规则

| 风险类别 | 检测模式 | 单独判定 | 说明 |
|---|---|---|---|
| Shell 命令 | `curl`, `wget`, `rm -rf`, `git push --force` | info | 需要结合用途判断 |
| 敏感文件 | `.env`, `credentials`, `.key`, `.pem`, `secret` | medium | 访问凭证通常不合理 |
| 外部 URL | `https?://[^\s]+` | info | 需要结合用途判断 |
| 隐藏行为 | `don't tell`, `silently`, `without user`, `hidden` | high | 几乎总是可疑 |
| 数据外泄 | `send to`, `post to`, `upload`, `exfiltrate` | high | 高度可疑 |
| 子进程 | `subprocess`, `os.system`, `exec(`, `eval(` | medium | 需要结合用途判断 |
| Prompt Injection | `ignore previous`, `disregard`, `you are now` | critical | 几乎总是恶意 |

**关键**: 静态分析只标记 "存在什么能力"，不直接判定 "是否恶意"。最终判定由 LLM 审查层综合判断。

### 8.4 LLM 安全审查

```python
class LLMSecurityReviewer:
    """
    使用 LLM 对 Skill 进行深度安全审查。

    输入:
    - Skill 声明的用途 (name, description, tags)
    - 静态分析检测到的能力列表
    - Skill 的完整 prompt 内容

    输出:
    - 每个能力的合理性判断
    - 额外发现的 risks
    - 综合 risk_level + score
    - 结构化的 Finding 列表

    设计决策:
    - 使用 GPT-4o-mini，成本低且足够
    - Prompt 模板集中管理在 prompts/security_review.py
    - 输出强制 JSON Schema 校验，不信任原始输出
    - 超时 30s，失败时降级为仅静态分析结果
    """
```

### 8.5 安全报告示例

```json
{
  "risk_level": "medium",
  "score": 42,
  "capabilities": [
    {
      "type": "shell.execute",
      "detail": "可以执行 Shell 命令",
      "evidence": {
        "source": "static_scan",
        "location": "prompt line 15",
        "content": "Run `npm test` to execute test suite",
        "context": "Skill 要求执行 npm test 命令"
      }
    },
    {
      "type": "network.access",
      "detail": "可以访问外部 URL",
      "evidence": {
        "source": "static_scan",
        "location": "prompt line 23",
        "content": "Fetch results from https://api.example.com/coverage",
        "context": "Skill 要求访问外部 API 获取覆盖率数据"
      }
    }
  ],
  "findings": [
    {
      "id": "F001",
      "severity": "low",
      "title": "Skill 可以执行 Shell 命令",
      "description": "该 Skill 包含执行 Shell 命令的指令。对于 TDD 类 Skill，执行测试命令是合理的。",
      "evidence": {
        "source": "static_scan",
        "location": "prompt line 15",
        "content": "Run `npm test` to execute test suite",
        "context": "命令内容与声明用途一致"
      },
      "recommendation": "Shell 命令与 TDD 用途匹配，风险较低。建议确认命令范围是否合理。",
      "category": "shell_execution"
    },
    {
      "id": "F002",
      "severity": "medium",
      "title": "Skill 请求网络访问",
      "description": "该 Skill 要求访问外部 API。TDD Skill 通常不需要网络访问，这一能力与声明用途存在一定偏差。",
      "evidence": {
        "source": "llm_review",
        "location": "prompt line 23",
        "content": "Fetch results from https://api.example.com/coverage",
        "context": "访问外部 API 获取覆盖率数据，非 TDD 核心功能"
      },
      "recommendation": "网络访问与 TDD 核心用途不完全匹配。如果不需要覆盖率功能，可以考虑移除相关指令。",
      "category": "capability_mismatch"
    }
  ],
  "review_version": "1.0.0",
  "reviewed_at": "2026-09-01T12:00:00Z"
}
```

---

## 9. Installation 流程

### 9.1 设计原则

> 删除 `curl | bash` 安装模式。
> SkillHub 的核心卖点是安全，安装环节不能引入不安全模式。

### 9.2 安装流程

```
用户在 Web 页面点击 "安装"
    │
    ▼
┌──────────────────────────────────┐
│  展示安装引导                      │
│  1. 显示安全摘要                   │
│  2. 展示 CLI 安装命令              │
│     skillhub install <skill-id>   │
│  3. 用户复制到终端执行              │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  SkillHub CLI 执行                 │
│  1. 从 SkillHub API 获取 Skill    │
│  2. 校验 Skill 来源和内容完整性     │
│  3. 再次确认风险状态                │
│  4. 如果 risk_level >= high       │
│     → 要求用户二次确认              │
│  5. 调用 AgentAdapter 安装         │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  ClaudeCodeAdapter                │
│  1. 检测 Claude Code 安装路径      │
│  2. 创建 Skill 目录                │
│  3. 写入 Skill 文件                │
│  4. 验证安装结果                   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  安装完成                          │
│  - 记录安装计数                    │
│  - 提示用户重启 Claude Code        │
└──────────────────────────────────┘
```

### 9.3 CLI 命令设计

```bash
# 安装 Skill
skillhub install <skill-id>
skillhub install <skill-name>          # 按名称安装 (模糊匹配)

# 卸载 Skill
skillhub uninstall <skill-id>
skillhub uninstall <skill-name>

# 列出已安装 Skill
skillhub list

# 查看 Skill 安全报告
skillhub audit <skill-id>

# 登录 (V1 不需要，预留)
# skillhub login

# 版本信息
skillhub --version
```

### 9.4 CLI 技术选型

- **Python** (与后端同语言，复用 schema 和 adapter 代码)
- **Click** 或 **Typer** 做 CLI 框架
- **Rich** 做终端美化输出
- 打包: **PyInstaller** 或 **pip install skillhub-cli**

### 9.5 安全检查点

CLI 在安装前执行以下检查:

1. **来源校验** — Skill 确实来自 SkillHub 数据库
2. **内容完整性** — 对比 hash，确保内容未被篡改
3. **风险状态** — 获取最新安全审查结果
4. **风险告知** — `high` 及以上风险要求用户明确确认

```
$ skillhub install tdd-master

Fetching skill info... done
Security status: MEDIUM (score: 42/100)

Capabilities detected:
  - shell.execute (matched with TDD purpose)
  - network.access (slight mismatch with TDD purpose)

Findings:
  1. [LOW] Shell command execution - consistent with TDD use
  2. [MEDIUM] Network access - not core TDD functionality

Do you want to proceed? [y/N]
```

---

## 10. Agent Adapter 设计

### 10.1 抽象接口

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class AgentType(Enum):
    CLAUDE_CODE = "claude_code"
    # FUTURE:
    # PI = "pi"
    # CURSOR = "cursor"


@dataclass
class InstallationResult:
    success: bool
    agent_type: AgentType
    skill_id: str
    install_path: Path
    message: str


@dataclass
class EnvironmentInfo:
    agent_type: AgentType
    is_installed: bool
    install_path: Path | None
    version: str | None
    config_path: Path | None


class AgentAdapter(ABC):
    """
    Agent 平台适配器抽象接口。

    设计决策:
    - V1 只实现 ClaudeCodeAdapter
    - 接口设计考虑未来扩展 (Pi, Cursor 等)
    - 每个方法都是独立操作，方便测试和重试

    为什么需要抽象层?
    - 不同 Agent 的 Skill 安装方式不同 (目录结构、配置格式)
    - 解耦安装逻辑与业务逻辑
    - 面试时可以展示架构设计能力
    """

    @abstractmethod
    def detect_environment(self) -> EnvironmentInfo:
        """检测 Agent 是否已安装，返回环境信息。"""

    @abstractmethod
    def install_skill(self, skill_id: str, skill_content: str) -> InstallationResult:
        """将 Skill 安装到 Agent 平台。"""

    @abstractmethod
    def uninstall_skill(self, skill_id: str) -> bool:
        """从 Agent 平台卸载 Skill。"""

    @abstractmethod
    def list_skills(self) -> list[dict]:
        """列出已安装的 SkillHub Skill。"""

    @abstractmethod
    def verify_installation(self, skill_id: str) -> bool:
        """验证 Skill 是否安装成功。"""
```

### 10.2 ClaudeCodeAdapter

```python
class ClaudeCodeAdapter(AgentAdapter):
    """
    Claude Code 适配器。

    Claude Code 的 Skill 安装方式:
    - Skill 文件存放在 ~/.claude/skills/{skill-name}/CLAUDE.md
    - 每个 Skill 是一个目录，包含 CLAUDE.md 和可选的附属文件
    - Claude Code 启动时自动加载 skills 目录

    为什么这样设计?
    - 遵循 Claude Code 的官方 Skill 格式
    - 安装 = 文件操作，不需要调用 Claude Code API
    - 卸载 = 删除目录
    """

    SKILL_DIR = Path.home() / ".claude" / "skills"

    def detect_environment(self) -> EnvironmentInfo:
        """检查 ~/.claude 目录是否存在"""

    def install_skill(self, skill_id: str, skill_content: str) -> InstallationResult:
        """
        1. 创建 ~/.claude/skills/{skill-name}/ 目录
        2. 写入 CLAUDE.md
        3. 验证文件存在且内容正确
        """

    def uninstall_skill(self, skill_id: str) -> bool:
        """删除 ~/.claude/skills/{skill-name}/ 目录"""

    def list_skills(self) -> list[dict]:
        """扫描 ~/.claude/skills/ 目录"""

    def verify_installation(self, skill_id: str) -> bool:
        """检查文件是否存在且内容 hash 匹配"""
```

### 10.3 扩展点（V1 不实现）

```python
# FUTURE:
class PiAdapter(AgentAdapter):
    """Qoder Pi 适配器 — 未来实现"""

class CursorAdapter(AgentAdapter):
    """Cursor 适配器 — 未来实现"""


class AdapterFactory:
    """
    根据 Agent 类型返回对应的 Adapter。
    V1 只支持 Claude Code。
    """

    @staticmethod
    def create(agent_type: AgentType) -> AgentAdapter:
        match agent_type:
            case AgentType.CLAUDE_CODE:
                return ClaudeCodeAdapter()
            case _:
                raise ValueError(f"Unsupported agent type: {agent_type}")
```

---

## 11. 系统架构

### 11.1 整体架构

```
                         SkillHub
                            │
             ┌──────────────┼──────────────┐
             │              │              │
        Discovery       Security      Installation
             │              │              │
             │              │              │
    ┌────────┴───────┐     │              │
    │                │     │              │
Query            Search   Static     ┌────┴─────┐
Understanding    Engine   Scan       │          │
    │                │     │       CLI      Agent
    │                │     │       Engine    Adapter
    │                │     │          │          │
    └────────┬───────┘     │          │          │
             │             │          │          │
             └──────┬──────┘          │          │
                    │                 │          │
                    ▼                 │          │
              Skill Detail ◄──────────┘          │
                    │                            │
                    ▼                            │
              User Confirmation                  │
                    │                            │
                    ▼                            │
               Installation ◄────────────────────┘
```

### 11.2 后端模块划分

```
backend/app/
├── api/v1/                    # 路由层 (薄)
│   ├── skills.py              # Skill CRUD + 搜索
│   ├── security.py            # 安全报告查询
│   └── recommendations.py     # 每日推荐
│
├── services/                  # 业务逻辑层 (核心)
│   ├── discovery/
│   │   ├── query_understanding.py   # 自然语言理解
│   │   ├── search.py                # 关键词 + 语义检索
│   │   └── ranking.py               # 排序算法
│   │
│   ├── security/
│   │   ├── static_scanner.py        # Layer 3: 正则扫描
│   │   ├── capability_analyzer.py   # Layer 2: 能力提取
│   │   ├── llm_reviewer.py          # Layer 5: LLM 审查
│   │   └── audit_pipeline.py        # 编排所有层
│   │
│   ├── ingestion/
│   │   ├── collector.py             # 数据抓取
│   │   ├── normalizer.py            # 数据标准化
│   │   └── enricher.py              # LLM 标签/摘要/embedding
│   │
│   ├── installation/
│   │   ├── adapter.py               # AgentAdapter 抽象
│   │   ├── claude_code.py           # ClaudeCodeAdapter
│   │   └── factory.py               # AdapterFactory
│   │
│   └── recommendation/
│       └── daily.py                 # 每日推荐评分
│
├── models/                    # SQLAlchemy ORM
├── schemas/                   # Pydantic schemas
├── core/                      # 配置、依赖注入、中间件
├── tasks/                     # APScheduler 定时任务
└── prompts/                   # LLM Prompt 模板
    ├── query_understanding.py
    ├── tag_generation.py
    └── security_review.py
```

### 11.3 数据流

```
┌─────────────────────────────────────────────────────────────┐
│                     定时任务 (每日)                            │
│                                                              │
│  skills.sh ──► Collector ──► Normalizer ──► Skill Database   │
│                                              │               │
│                                    ┌─────────┴──────────┐   │
│                                    │                    │   │
│                              Enricher            Audit Pipeline │
│                              (LLM 标签/          (安全审查)      │
│                               摘要/Embedding)                  │
│                                    │                    │   │
│                                    └─────────┬──────────┘   │
│                                              │               │
│                                     PostgreSQL + pgvector    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     用户请求                                  │
│                                                              │
│  Web ──► API ──► Discovery Service ──► Ranking ──► Response  │
│                                                              │
│  Web ──► API ──► Security Service ──► Report ──► Response    │
│                                                              │
│  CLI ──► API ──► Installation Service ──► AgentAdapter       │
└─────────────────────────────────────────────────────────────┘
```

---

## 12. 技术栈

| 层 | 技术 | 选择理由 |
|---|---|---|
| 前端 | Next.js 14 (App Router) + TypeScript | SSR + SEO，React 生态成熟 |
| 样式 | Tailwind CSS | 快速开发，一致性好 |
| 后端 | FastAPI (Python 3.11+) | 异步、类型安全、LLM 生态好 |
| 数据库 | PostgreSQL + pgvector | 关系数据 + 向量检索一体化 |
| ORM | SQLAlchemy 2.0 (async) | 成熟稳定，async 支持好 |
| 迁移 | Alembic | SQLAlchemy 标配 |
| LLM | OpenAI API (GPT-4o-mini) | 成本低，能力足够 |
| Embedding | OpenAI text-embedding-3-small | 1536 维，性价比好 |
| 定时任务 | APScheduler | 轻量，内嵌在 FastAPI 进程中 |
| CLI | Python + Typer + Rich | 与后端同语言，复用代码 |
| 测试 | pytest (后端) + Vitest (前端) | 各自生态标配 |
| 容器化 | Docker + docker-compose | 本地开发环境统一 |
| 部署 | Vercel (前端) + Railway (后端) | 低成本，适合个人项目 |

**不引入的技术**（避免过度工程）：

- Redis — V1 不需要缓存层，数据量小
- Elasticsearch — pgvector 足够
- Kubernetes — Railway 托管，不需要
- 消息队列 — 定时任务同步处理即可

---

## 13. 数据库设计初稿

### 13.1 skills 表

```sql
CREATE TABLE skills (
    -- Identity
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(255) NOT NULL UNIQUE,  -- URL-friendly name
    description     TEXT,
    version         VARCHAR(50) DEFAULT '1.0.0',

    -- Source
    registry        VARCHAR(50) NOT NULL DEFAULT 'skills_sh',
    source_url      TEXT NOT NULL,
    author          VARCHAR(255),
    collected_at    TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Content (immutable original)
    skill_md        TEXT NOT NULL,                  -- CLAUDE.md full content
    install_script  TEXT,

    -- LLM-generated metadata
    tags            TEXT[] DEFAULT '{}',
    summary         TEXT,
    capabilities    TEXT[] DEFAULT '{}',            -- extracted capabilities

    -- Vector
    embedding       vector(1536),

    -- Security
    risk_level      VARCHAR(20) DEFAULT 'pending'
                    CHECK (risk_level IN ('pending','safe','low','medium','high','critical')),
    security_score  INT DEFAULT 0 CHECK (security_score >= 0 AND security_score <= 100),
    security_report JSONB,                          -- SecurityReport JSON
    reviewed_at     TIMESTAMP,
    review_version  VARCHAR(50),

    -- Popularity
    install_count   INT DEFAULT 0,
    trending_score  FLOAT DEFAULT 0.0,

    -- System
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_skills_slug ON skills (slug);
CREATE INDEX idx_skills_tags ON skills USING GIN (tags);
CREATE INDEX idx_skills_capabilities ON skills USING GIN (capabilities);
CREATE INDEX idx_skills_risk_level ON skills (risk_level);
CREATE INDEX idx_skills_install_count ON skills (install_count DESC);
CREATE INDEX idx_skills_embedding ON skills
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_skills_created_at ON skills (created_at DESC);
```

### 13.2 install_logs 表

```sql
CREATE TABLE install_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    UUID NOT NULL REFERENCES skills(id),
    -- V1 无用户系统，记录匿名安装事件
    source      VARCHAR(50) NOT NULL DEFAULT 'cli',  -- cli | web
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_install_logs_skill_id ON install_logs (skill_id);
CREATE INDEX idx_install_logs_created_at ON install_logs (created_at DESC);
```

### 13.3 设计说明

- **单表设计**: V1 数据量小（预计 < 1000 skills），单表 + JSONB 足够
- **security_report 用 JSONB**: 结构灵活，方便 LLM 输出直接存入
- **不拆 security_findings 表**: V1 不需要按 finding 查询，JSONB 内嵌即可
- **install_logs 独立**: 方便统计 install_count 和趋势，未来可加 user_id
- **slug 字段**: URL 友好，`/skills/tdd-master` 比 `/skills/{uuid}` 好

---

## 14. API 设计初稿

### 14.1 Discovery

```
GET /api/v1/skills/search
  Query params:
    q: string              # 搜索查询 (关键词或自然语言)
    mode: "auto" | "keyword" | "semantic"  # 默认 auto
    tags: string[]         # 标签过滤
    risk_level: string     # 安全等级过滤 (max)
    page: int = 1
    page_size: int = 20    # max 50

  Response:
  {
    "data": {
      "query_understanding": {   # 自然语言查询时返回
        "keywords": [...],
        "capabilities": [...],
        "constraints": [...],
        "query_type": "natural_language"
      },
      "skills": [
        {
          "id": "uuid",
          "name": "TDD Master",
          "slug": "tdd-master",
          "summary": "...",
          "tags": ["testing", "tdd"],
          "risk_level": "safe",
          "security_score": 12,
          "install_count": 142,
          "ranking_score": 0.87
        }
      ]
    },
    "meta": { "page": 1, "page_size": 20, "total": 45 }
  }
```

```
GET /api/v1/skills/recommendations
  Query params:
    limit: int = 10         # max 20

  Response:
  {
    "data": {
      "date": "2026-09-01",
      "skills": [...]
    }
  }
```

### 14.2 Skill Detail

```
GET /api/v1/skills/{slug}

  Response:
  {
    "data": {
      "id": "uuid",
      "name": "TDD Master",
      "slug": "tdd-master",
      "description": "...",
      "author": "@author",
      "version": "1.0.0",
      "registry": "skills_sh",
      "source_url": "https://skills.sh/...",
      "tags": ["testing", "tdd"],
      "summary": "一句话摘要",
      "capabilities": ["shell.execute"],
      "skill_md": "# TDD Master\n...",
      "risk_level": "medium",
      "security_score": 42,
      "security_report": {
        "capabilities": [...],
        "findings": [...],
        "review_version": "1.0.0",
        "reviewed_at": "..."
      },
      "install_count": 142,
      "created_at": "2026-09-01T00:00:00Z"
    }
  }
```

### 14.3 Installation (CLI 调用)

```
GET /api/v1/skills/{slug}/install
  Headers: X-SkillHub-CLI-Version: 0.1.0

  Response:
  {
    "data": {
      "skill_id": "uuid",
      "name": "TDD Master",
      "version": "1.0.0",
      "skill_md": "# TDD Master\n...",
      "content_hash": "sha256:abc123...",
      "risk_level": "medium",
      "security_score": 42,
      "install_instructions": {
        "agent_type": "claude_code",
        "target_path": "~/.claude/skills/tdd-master/CLAUDE.md"
      }
    }
  }
```

### 14.4 Tags

```
GET /api/v1/tags

  Response:
  {
    "data": [
      { "name": "testing", "count": 42 },
      { "name": "react", "count": 38 }
    ]
  }
```

### 14.5 Stats

```
GET /api/v1/stats

  Response:
  {
    "data": {
      "total_skills": 156,
      "safe_skills": 98,
      "total_installs": 2340,
      "last_updated": "2026-09-01T00:00:00Z"
    }
  }
```

---

## 15. 开发阶段拆解

### Phase 1: 基础设施 + 数据管道 (Day 1-4)

**目标**: 数据能进来、能存、能查

| 任务 | 说明 |
|---|---|
| 项目初始化 | Next.js + FastAPI + PostgreSQL + Docker |
| 数据库 Schema | skills 表 + install_logs 表 + Alembic |
| Collector | skills.sh 数据抓取 |
| Normalizer | 数据标准化、去重 |
| Enricher | LLM 标签生成 + 摘要 + Embedding |
| 定时任务 | APScheduler 每日自动聚合 |

**验收标准**:
- [ ] `docker-compose up` 启动全部服务
- [ ] Collector 能抓取 skills.sh 并写入数据库
- [ ] 每个 Skill 有 tags、summary、embedding
- [ ] 数据库中有 50+ 条 Skill 数据
- [ ] 定时任务能手动触发并成功执行

---

### Phase 2: Discovery 引擎 (Day 5-8)

**目标**: 用户能搜到想要的 Skill

| 任务 | 说明 |
|---|---|
| 关键词搜索 | PostgreSQL ILIKE 检索 |
| Query Understanding | LLM 自然语言 → 结构化查询 |
| 语义搜索 | pgvector 余弦相似度检索 |
| Ranking | 综合评分排序 |
| 每日推荐 | 简单 Ranking 公式 |
| 搜索 API | 完整搜索接口 |

**验收标准**:
- [ ] 关键词搜索 "TDD" 返回相关 Skill
- [ ] 自然语言搜索 "帮我写测试的工具" 返回测试相关 Skill
- [ ] Query Understanding 能提取 capabilities 和 constraints
- [ ] Ranking 结果合理（相关 + 热门 + 安全的排前面）
- [ ] 每日推荐返回 10 个 Skill
- [ ] 搜索响应时间 < 500ms

---

### Phase 3: Security Audit (Day 9-12)

**目标**: 每个 Skill 有可解释的安全报告

| 任务 | 说明 |
|---|---|
| Static Scanner | 正则扫描所有风险模式 |
| Capability Analyzer | 从 Skill 内容提取能力列表 |
| LLM Reviewer | LLM 综合审查 + 生成报告 |
| Audit Pipeline | 编排所有层，输出 SecurityReport |
| 安全报告 API | 查询安全报告接口 |
| 入库集成 | 新 Skill 入库时自动触发审查 |

**验收标准**:
- [ ] 所有已有 Skill 都有安全报告
- [ ] 报告包含 capabilities、findings、evidence、recommendation
- [ ] "能力与用途匹配" 的 Skill 评分为 safe/low
- [ ] "能力与用途不匹配" 的 Skill 评分为 medium+
- [ ] 静态扫描不会把正常 Shell 命令直接判为 danger
- [ ] LLM 审查失败时降级为仅静态分析结果
- [ ] 安全审查有完整单元测试

---

### Phase 4: 前端页面 (Day 13-17)

**目标**: 用户能在 Web 上完成发现 → 查看 → 安装引导

| 任务 | 说明 |
|---|---|
| 首页 | 搜索框 + 热门标签 + 推荐 + 最新 |
| 搜索结果页 | 展示搜索结果 + Query Understanding 信息 |
| Skill 详情页 | 描述 + 标签 + 安全报告 + 安装引导 |
| 安全报告组件 | 可解释的 Finding 列表 + Evidence 展示 |
| 安装引导 | 展示 CLI 命令 + 复制功能 |
| 标签浏览页 | 按标签分类浏览 |

**验收标准**:
- [ ] 首页能正常渲染，搜索功能可用
- [ ] 自然语言搜索展示结果 + 理解后的意图
- [ ] 详情页展示完整安全报告，Finding 可展开查看 Evidence
- [ ] 安装命令可一键复制
- [ ] 页面 SEO metadata 正确
- [ ] 移动端基本可用（响应式）

---

### Phase 5: CLI + Agent Adapter (Day 18-20)

**目标**: 用户能通过 CLI 安装 Skill

| 任务 | 说明 |
|---|---|
| AgentAdapter 抽象 | 接口定义 + Factory |
| ClaudeCodeAdapter | 安装/卸载/列表/验证 |
| CLI 框架 | Typer + Rich |
| `skillhub install` | 获取 → 校验 → 安装 |
| `skillhub uninstall` | 卸载 + 清理 |
| `skillhub list` | 列出已安装 |
| `skillhub audit` | 查看安全报告 |
| Install API | 后端提供安装数据接口 |

**验收标准**:
- [ ] `skillhub install tdd-master` 成功安装到 `~/.claude/skills/`
- [ ] `skillhub list` 显示已安装 Skill
- [ ] `skillhub uninstall tdd-master` 成功卸载
- [ ] 安装前展示安全摘要，high risk 要求二次确认
- [ ] 安装后验证文件存在且内容正确
- [ ] Claude Code 能识别安装的 Skill

---

### Phase 6: 集成测试 + 部署 (Day 21-24)

**目标**: 端到端可用，部署上线

| 任务 | 说明 |
|---|---|
| 端到端测试 | 搜索 → 详情 → 安装 完整流程 |
| 初始数据灌入 | 确保有 100+ Skill |
| 前端部署 | Vercel |
| 后端部署 | Railway |
| CLI 发布 | PyPI 或 GitHub Release |
| 定时任务配置 | 生产环境 APScheduler |
| 监控 + 日志 | 基本错误追踪 |

**验收标准**:
- [ ] 线上环境端到端流程可用
- [ ] 100+ Skill 已入库且有安全报告
- [ ] CLI 可正常安装和卸载
- [ ] 前端 LCP < 2.5s
- [ ] API 响应时间 < 500ms

---

**预计总工期: 24 天 (约 3.5 周)**

---

## 16. 风险与技术难点

| 风险 | 影响 | 概率 | 应对 |
|---|---|---|---|
| skills.sh 数据量不足 (< 50) | 搜索体验差 | 中 | 手动补充种子数据；V2 加 GitHub 数据源 |
| LLM Query Understanding 质量差 | 搜索结果不相关 | 中 | 降级为关键词搜索；优化 Prompt |
| LLM 安全审查误报 | 用户信任度下降 | 中 | 调整 Prompt；安全报告标注 "自动审查，仅供参考" |
| LLM 安全审查漏报 | 安全风险 | 低 | 静态分析兜底；未来加社区举报 |
| Claude Code 目录结构变化 | CLI 安装失效 | 低 | 监控 Claude Code 更新；Adapter 模式方便适配 |
| OpenAI API 成本超预期 | 运营压力 | 低 | GPT-4o-mini 成本极低；限制每日调用量 |
| pgvector 在大数据量下性能下降 | 搜索变慢 | 低 | V1 数据量小不会发生；V2 可加 HNSW 索引 |
| CLI 跨平台兼容性 | Windows/Mac 用户无法使用 | 中 | Python CLI 天然跨平台；测试覆盖三平台 |

### 技术难点

1. **Query Understanding 的 Prompt 设计** — 需要让 LLM 稳定输出结构化 JSON，且能正确区分 capabilities 和 constraints
2. **安全审查的 "能力 vs 恶意" 判断** — LLM 需要理解上下文，不能简单正则匹配
3. **CLI 安装路径检测** — 不同系统上 Claude Code 的安装路径可能不同
4. **安全报告的展示** — 前端需要把多层审查结果以用户可理解的方式展示

---

## 17. 明确不做的事情

以下功能在 V1 **明确不做**，即使为了 "看起来完整" 也不加入：

| 不做的事 | 原因 |
|---|---|
| `curl \| bash` 安装 | 与核心安全定位矛盾 |
| 用户注册/登录 | 工作量大，V1 无个性化需求 |
| 个性化推荐 | 依赖用户数据，V1 没有 |
| 多 Agent 适配 | V1 只实现 ClaudeCodeAdapter |
| GitHub 数据源 | 先跑通 skills.sh |
| 对话式多轮搜索 | 单轮自然语言搜索已足够 |
| Sandbox / 沙箱执行 | 需要容器化，复杂度远超 MVP |
| Skill 创作工具 | 先做消费端 |
| 机器学习推荐 | 简单公式 Ranking 足够 |
| Redis / ES / MQ | 数据量小，不需要 |
| 社区举报/人工审核 | 自动化审查先跑起来 |
| 浏览器插件 | Web + CLI 已覆盖核心场景 |
| 国际化 (i18n) | V1 只做中文/英文 |
| WebSocket 实时推送 | 不需要实时功能 |

---

## 18. 可行性评估

### 一个人能在合理时间内完成吗？

**结论: 可以。**

| 因素 | 评估 |
|---|---|
| 总工期 | 24 天，每天投入 4-6 小时，约 3.5 周 |
| 技术栈成熟度 | 全部使用成熟框架，无自研组件 |
| 数据量 | < 1000 skills，单表足够 |
| LLM 调用 | GPT-4o-mini 成本极低 (< $5/月) |
| 部署成本 | Vercel 免费 + Railway $5/月 |
| 核心难点 | Query Understanding 和安全审查 Prompt 需要迭代，但有明确的最小可用版本 |

### 面试价值评估

| 模块 | 面试可聊的点 |
|---|---|
| Discovery | Query Understanding 设计、语义搜索 vs 关键词搜索的 tradeoff、Ranking 算法 |
| Security | 多层审查架构、"能力 ≠ 恶意" 的设计哲学、LLM 审查的 Prompt 工程 |
| Installation | Agent Adapter 抽象、安全安装 vs `curl\|bash` 的对比 |
| 整体 | 前后端分离架构、数据管道设计、如何平衡 MVP 与可扩展性 |

### 如果时间紧张，可以砍什么？

优先级从高到低:

1. **不能砍**: 数据管道 + Discovery + Security + 前端详情页 + CLI 安装
2. **可以简化**: 每日推荐 (改为随机 + 热门)、安全报告简化为列表而非分层
3. **可以延后**: Query Understanding (V1 先只做关键词 + 语义搜索)、CLI 的 `audit` 命令
