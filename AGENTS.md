# AGENTS.md — SkillHub 开发约束与规范

> 本文件是所有 AI Agent 和开发者在本仓库中工作时必须遵守的约束和规范。

---

## 1. 项目概览

SkillHub 是一个 AI Agent Skill 发现、安全审查与一键安装平台。

- **前端**: Next.js 14 (App Router) + TypeScript
- **后端**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL + pgvector
- **LLM**: OpenAI API (GPT-4o-mini / text-embedding-3-small)
- **CLI**: Python + Typer + Rich
- **部署**: Vercel (前端) + Railway (后端) + Docker (本地开发)

---

## 2. 目录结构

```
SkillHub/
├── frontend/                # Next.js 前端
│   ├── app/                 # App Router 页面
│   ├── components/          # 可复用组件
│   │   ├── ui/              # 基础 UI 组件
│   │   └── features/        # 业务组件
│   ├── lib/                 # 工具函数、API 客户端
│   ├── styles/              # 全局样式
│   └── types/               # TypeScript 类型定义
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/          # 路由层 (薄)
│   │   ├── core/            # 配置、安全、依赖注入
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # 业务逻辑层
│   │   │   ├── discovery/   # Query Understanding + Search + Ranking
│   │   │   ├── security/    # 多层安全审查 (static/capability/llm/pipeline)
│   │   │   ├── ingestion/   # Collector + Normalizer + Enricher
│   │   │   ├── installation/# AgentAdapter + ClaudeCodeAdapter
│   │   │   └── recommendation/ # 每日推荐
│   │   ├── prompts/         # LLM Prompt 模板 (集中管理)
│   │   └── tasks/           # APScheduler 定时任务
│   ├── migrations/          # Alembic 数据库迁移
│   └── tests/
├── cli/                     # SkillHub CLI (Typer + Rich)
│   ├── commands/            # CLI 命令 (install/uninstall/list/audit)
│   ├── adapters/            # AgentAdapter 引用 (与后端共享或独立)
│   └── tests/
├── scripts/                 # 独立脚本（种子数据等）
├── docker-compose.yml       # 本地开发环境
└── docs/                    # 文档
```

**约束**:
- 严格前后端分离，前端不得直接访问数据库
- 所有共享类型在 `types/` (前端) 和 `schemas/` (后端) 中定义
- 禁止在 `components/` 中直接发起 HTTP 请求，统一通过 `lib/api` 调用
- 后端 services 按业务域划分 (discovery/security/ingestion/installation)，不按技术层划分
- CLI 与后端共享 Pydantic schemas，避免重复定义数据结构
- LLM Prompt 模板集中在 `backend/app/prompts/` 目录，禁止散落在业务代码中

---

## 3. 代码风格

### 3.1 前端 (TypeScript / Next.js)

- 使用 **TypeScript strict 模式**，禁止 `any` 类型
- 组件使用 **函数式组件 + Hooks**，禁止 Class 组件
- 文件命名: 组件用 **PascalCase** (`SkillCard.tsx`)，工具用 **camelCase** (`formatDate.ts`)
- 样式优先使用 **Tailwind CSS**，避免内联样式
- 使用 `next/link` 和 `next/image`，禁止原生 `<a>` 和 `<img>` 做站内导航
- 服务端组件为默认选择，仅在需要交互时使用 `"use client"`
- 每个页面组件不超过 **200 行**，超出则拆分为子组件

### 3.2 后端 (Python / FastAPI)

- 遵循 **PEP 8**，行宽 120
- 使用 **type hints**，所有函数签名必须有类型标注
- 异步优先: I/O 操作必须使用 `async/await`
- 导入顺序: 标准库 → 第三方 → 本地，用空行分隔
- 文件命名: **snake_case** (`skill_service.py`)
- 类命名: **PascalCase** (`SkillService`)
- 常量: **UPPER_SNAKE_CASE** (`MAX_SEARCH_RESULTS`)
- 每个路由函数不超过 **50 行**，业务逻辑下沉到 `services/`

### 3.3 通用规则

- **不提交注释掉的代码**，直接删除；需要追溯用 git history
- **不写冗余注释**，代码本身应自解释；注释只解释 "为什么" 而非 "是什么"
- 所有公开函数/接口必须有 docstring 或 JSDoc
- 禁止 `console.log` / `print` 调试代码提交到仓库

---

## 4. API 设计规范

### 4.1 RESTful 约定

- 所有接口以 `/api/v1/` 为前缀
- 资源名使用 **复数名词**: `/skills`, `/tags`
- 使用 HTTP 方法语义正确: `GET` 读取, `POST` 创建, `PUT` 全量更新, `PATCH` 部分更新, `DELETE` 删除
- 分页参数统一: `?page=1&page_size=20`
- 排序参数: `?sort=created_at&order=desc`

### 4.2 响应格式

```json
{
  "data": {},
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

- 成功响应使用 `{ "data": ... }` 包裹
- 错误响应统一格式: `{ "error": { "code": "NOT_FOUND", "message": "..." } }`
- HTTP 状态码: `200` 成功, `201` 创建成功, `400` 参数错误, `404` 未找到, `422` 校验失败, `500` 服务器错误

### 4.3 约束

- 所有接口必须有 **请求参数校验** (Pydantic schema / Zod)
- 所有接口必须有 **错误处理**，禁止裸 500
- 搜索接口必须限制 `limit` 上限 (默认 20, 最大 50)
- API 变更必须保持 **向后兼容**，破坏性变更需要新版本号 (`/api/v2/`)

---

## 5. 数据库规范

### 5.1 Schema 设计

- 所有表必须有 `id` (UUID), `created_at`, `updated_at` 字段
- 使用 `created_at TIMESTAMP DEFAULT NOW()` 和 `updated_at TIMESTAMP DEFAULT NOW()`
- `updated_at` 必须在每次更新时自动刷新 (通过 SQLAlchemy 事件或数据库触发器)
- 外键使用 `UUID` 类型，命名: `{resource}_id`
- 布尔字段以 `is_` 或 `has_` 开头
- 枚举字段使用 `VARCHAR` + CHECK 约束，不使用 PostgreSQL 原生 ENUM 类型

### 5.2 迁移

- 使用 **Alembic** 管理数据库迁移
- 每次变更必须生成迁移文件，禁止手动修改数据库
- 迁移文件必须有清晰的描述性 message
- **禁止在生产环境执行 destructive migration** (DROP TABLE, DROP COLUMN)  without explicit approval
- 迁移必须可回滚: 每个 `upgrade()` 必须有对应的 `downgrade()`

### 5.3 查询

- 禁止 `SELECT *`，明确列出需要的字段
- 大数据量查询必须分页，禁止一次加载全部
- 向量搜索必须设置 `limit`，禁止无限制返回
- 敏感数据 (如 API key) **禁止存入数据库**

---

## 6. 安全规范

### 6.1 输入处理

- 所有用户输入必须 **校验 + 转义**，防止 XSS 和 SQL 注入
- 使用参数化查询，**禁止字符串拼接 SQL**
- URL 参数、路径参数必须做类型和范围校验

### 6.2 敏感信息

- **禁止** 在代码中硬编码 API Key、密码、数据库连接串
- 所有密钥通过 **环境变量** 注入
- `.env` 文件必须加入 `.gitignore`
- 日志中 **禁止输出** 敏感信息 (token, password, API key)

### 6.3 Skill 安全审查

安全审查采用多层架构，详见 PRODUCT_PLAN.md 第 8 节。核心约束:

- 所有入库的 Skill 必须经过完整审查管道 (Metadata → Capability → Static → Prompt → LLM)
- 审查结果以 `SecurityReport` (JSONB) 持久化到 `security_report` 字段
- **Capability 存在 ≠ Capability 恶意** — 静态扫描只标记能力，最终判定由 LLM 审查层综合判断
- 安全报告必须可解释: 每个 Finding 必须有 Evidence 和 Recommendation
- `risk_level` 为 `high` 或 `critical` 的 Skill 必须在详情页 **显著警告**
- CLI 安装 `high` 及以上风险的 Skill 时，必须要求用户 **二次确认**
- LLM 审查失败时降级为仅静态分析结果，并在报告中标注 `review_version`
- 禁止使用 `curl | bash` 模式安装 Skill

### 6.4 CORS 与鉴权

- 后端 CORS 只允许前端域名，禁止 `allow_origins=["*"]`
- MVP 阶段无用户系统，但 API 应预留鉴权中间件位置
- 管理接口 (如手动触发数据聚合) 必须有访问控制

---

## 7. 前端页面规范

### 7.1 SEO

- 每个页面必须设置 `metadata` (title, description)
- Skill 详情页使用动态 metadata
- 使用语义化 HTML 标签 (`<main>`, `<nav>`, `<article>`, `<section>`)

### 7.2 性能

- 图片使用 `next/image` 并指定 `width` / `height`
- 列表组件使用合理的 `key`
- 大数据列表考虑虚拟滚动
- 首屏关键 CSS 内联，非关键 CSS 异步加载

### 7.3 可访问性 (a11y)

- 交互元素必须有 `aria-label` 或可见文本
- 颜色对比度满足 WCAG AA 标准
- 支持键盘导航
- 表单元素必须关联 `<label>`

---

## 8. 测试规范

### 8.1 后端测试

- 使用 **pytest** + **httpx** (AsyncClient)
- 每个 API 端点必须有 **至少一个正常路径 + 一个异常路径** 测试
- Service 层核心逻辑必须有单元测试
- 安全审查模块必须有 **覆盖所有风险类型** 的测试用例
- 测试数据库与开发数据库 **隔离**，使用独立的测试数据库或 SQLite

### 8.2 前端测试

- 使用 **Vitest** + **React Testing Library**
- 核心交互组件 (搜索框、安装命令复制) 必须有测试
- 页面级 smoke test: 确保页面能正常渲染不报错

### 8.3 约束

- 提交前必须通过所有测试: `npm test` / `pytest`
- 测试文件命名: `test_*.py` (后端), `*.test.ts(x)` (前端)
- **禁止 mock 数据库连接**，使用测试数据库
- CI 中测试覆盖率不低于 **70%**

---

## 9. Git 工作流

### 9.1 分支

- `main`: 生产分支，只接受 PR 合并
- `dev`: 开发分支，日常开发在此进行
- `feature/{name}`: 功能分支，从 `dev` 拉出
- `fix/{name}`: 修复分支
- `chore/{name}`: 工具链、配置变更

### 9.2 提交信息

格式: `<type>(<scope>): <description>`

| type | 用途 |
|---|---|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档变更 |
| `style` | 代码格式 (不影响逻辑) |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具链 |

示例: `feat(search): add semantic search with pgvector`

### 9.3 约束

- **禁止 force push** 到 `main` 和 `dev`
- 每个 PR 必须有清晰的描述，说明做了什么和为什么
- 提交前确保代码能通过 lint 和测试
- 一个 PR 只做一件事，禁止混合不相关变更

---

## 10. 环境与配置

### 10.1 环境变量

后端必需的环境变量 (`.env`):

```
DATABASE_URL=postgresql+asyncpg://...
OPENAI_API_KEY=sk-...
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development|production
```

前端必需的环境变量 (`.env.local`):

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 10.2 约束

- 环境变量变更必须同步更新 `.env.example`
- 配置项集中在 `backend/app/core/config.py` 管理，使用 Pydantic Settings
- 禁止在代码中使用 `os.environ.get()` 直接读取环境变量

---

## 11. 错误处理

### 11.1 后端

- 使用全局异常处理器 (`@app.exception_handler`)
- 业务异常自定义: `SkillNotFoundError`, `SafetyCheckError` 等
- 外部服务调用 (OpenAI API, skills.sh 抓取) 必须有 **超时 + 重试 + 降级**
- 所有异常必须记录日志，包含上下文信息

### 11.2 前端

- API 调用错误统一在 `lib/api` 层处理
- 页面展示 **用户友好的错误信息**，禁止暴露技术细节
- 网络错误、加载失败使用 Error Boundary 兜底
- Loading 状态必须有明确的视觉反馈

---

## 12. 性能约束

- API 响应时间: 普通接口 < **200ms**, 搜索接口 < **500ms**
- 前端 LCP (Largest Contentful Paint) < **2.5s**
- 数据库单次查询 < **100ms**
- 向量搜索必须设置合理的 `limit` (默认 10, 最大 50)
- 定时任务 (数据聚合) 必须 **幂等**，重复执行不产生重复数据
- 批量操作使用批量插入，禁止循环单条写入

---

## 13. LLM 调用规范

- 所有 LLM 调用必须设置 **超时** (默认 30s)
- 必须处理 **速率限制** (429)，实现指数退避重试
- Token 消耗必须记录日志，用于成本监控
- Prompt 模板集中管理在 `backend/app/prompts/`，禁止散落在业务代码中
- Embedding 维度必须与数据库向量维度一致 (1536 for text-embedding-3-small)
- LLM 返回结果必须做 **格式校验** (JSON Schema / Pydantic)，不信任原始输出
- LLM 调用失败时必须有 **降级方案** (如 Query Understanding 降级为纯关键词搜索，LLM 审查降级为仅静态分析)

---

## 14. CLI 开发规范

- 使用 **Typer** 作为 CLI 框架，**Rich** 做终端输出
- CLI 代码在 `cli/` 目录，与后端代码分离
- CLI 通过 HTTP API 与后端通信，不直接访问数据库
- 安装操作前必须展示安全摘要，`high` 及以上风险要求用户明确确认
- CLI 命令必须有 `--dry-run` 选项，预览操作而不实际执行
- 所有 CLI 命令必须有 `--help` 说明
- 安装路径检测失败时给出清晰的错误提示和手动安装指引
- CLI 版本号通过 `--version` 展示，API 请求携带 `X-SkillHub-CLI-Version` header

---

## 15. Agent Adapter 规范

- `AgentAdapter` 是抽象基类，定义 `detect_environment` / `install_skill` / `uninstall_skill` / `list_skills` / `verify_installation` 五个方法
- V1 只实现 `ClaudeCodeAdapter`，其他 Agent 类型只定义接口不实现
- 使用 `AdapterFactory` 根据 `AgentType` 枚举创建对应 Adapter
- Adapter 内部的文件操作必须有错误处理 (目录不存在、权限不足、文件冲突)
- 安装操作必须是 **幂等的** — 重复安装同一 Skill 结果一致
- 卸载操作前必须确认 Skill 存在，不存在时给出明确提示
- 新增 Agent 类型时，只需实现 `AgentAdapter` 子类，不修改现有代码

---

## 16. 禁止事项清单

| 禁止行为 | 原因 |
|---|---|
| 硬编码密钥/密码 | 安全红线 |
| `SELECT *` | 性能与安全性 |
| `any` 类型 (TS) | 破坏类型安全 |
| 注释掉的代码 | 代码噪音 |
| 未分页的大查询 | 内存溢出风险 |
| 字符串拼接 SQL | SQL 注入风险 |
| 跳过安全审查入库 | 核心功能缺失 |
| 生产环境 destructive migration | 数据丢失风险 |
| `console.log` / `print` 调试 | 代码质量 |
| 直接 `os.environ.get()` | 配置管理混乱 |
| `curl \| bash` 安装模式 | 与核心安全定位矛盾 |
| 静态扫描直接判定 Skill 为恶意 | 违反 "能力 ≠ 恶意" 原则 |
| 绕过 AgentAdapter 直接操作文件 | 破坏安装抽象层 |
| 在业务代码中写 LLM Prompt | Prompt 必须集中管理 |
