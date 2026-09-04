# SkillHub

> AI Agent Skill 发现、安全审查与一键安装平台

SkillHub 帮助开发者从海量 Agent Skill 中**找到**合适的工具、**看懂**它的安全风险、并**安全地安装**到自己的 Agent 环境中。核心闭环为 **Discovery（发现） → Security Audit（安全审查） → Installation（安装）**。

**核心理念**：`Capability 存在 ≠ Capability 恶意`。静态扫描只标记 Skill 具备的能力，最终风险判定由 LLM 审查层综合给出，并输出可解释的安全报告。

---

## 在线体验

| 服务 | 地址 |
|---|---|
| 前端 (Vercel) | https://skillhub-ecru-two.vercel.app/ |
| 后端 API (Railway) | https://skillhub-production-a4e4.up.railway.app/ |
| API 文档 | https://skillhub-production-a4e4.up.railway.app/docs |

---

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS |
| 后端 | FastAPI + SQLAlchemy (async) + Alembic |
| 数据库 | PostgreSQL + pgvector |
| LLM | 通义千问 Qwen (DashScope) + text-embedding-v3（1024 维） |
| CLI | Python + Typer + Rich |
| 部署 | Railway（后端） + Vercel（前端） + Docker（本地） |
| 测试 | pytest + httpx（后端/CLI）、Vitest + React Testing Library（前端） |

---

## 功能特性

### 发现 Discovery
- **混合搜索**：语义向量检索 + 关键词检索 + 多因子排序
- **Query Understanding**：LLM 解析自然语言查询意图，失败时降级为纯关键词搜索
- **标签浏览**：按分类标签筛选 Skill
- **每日推荐**：精选优质 Skill

### 安全审查 Security Audit
多层审查管道，输出结构化、可解释的 `SecurityReport`：

```
Metadata → Capability → Static → Prompt → LLM
```

- 每个 Finding 都带有 Evidence（证据）与 Recommendation（建议）
- `high` / `critical` 风险在详情页显著警告
- LLM 审查失败时降级为仅静态分析，并标注 `review_version`

### 安装 Installation
- **AgentAdapter 抽象层**：统一 `detect_environment` / `install_skill` / `uninstall_skill` / `list_skills` / `verify_installation` 接口
- **ClaudeCodeAdapter**：V1 已实现，其他 Agent 类型预留扩展
- 安装操作幂等，禁止 `curl | bash` 模式
- `high` 及以上风险安装需二次确认

### CLI
```bash
skillhub install <skill>      # 安装 Skill（展示安全摘要，高风险需确认）
skillhub uninstall <skill>    # 卸载 Skill
skillhub list                 # 列出已安装 Skill
skillhub search <query>       # 搜索 Skill
skillhub audit <skill>        # 查看安全审查报告
```
所有命令支持 `--dry-run` 预览。

---

## 项目结构

```
SkillHub/
├── frontend/          # Next.js 前端（首页 / 搜索 / 详情 / 标签）
├── backend/
│   ├── app/
│   │   ├── api/v1/        # 路由层
│   │   ├── core/          # 配置、安全、依赖注入
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # 业务逻辑
│   │   │   ├── discovery/     # Query Understanding + Search + Ranking
│   │   │   ├── security/      # 多层安全审查
│   │   │   ├── ingestion/     # Collector + Normalizer + Enricher + Seed
│   │   │   ├── installation/  # AgentAdapter + ClaudeCodeAdapter
│   │   │   └── recommendation/
│   │   ├── prompts/       # LLM Prompt 模板（集中管理）
│   │   └── tasks/         # APScheduler 定时任务
│   ├── migrations/    # Alembic 迁移
│   └── tests/
├── cli/               # SkillHub CLI (Typer + Rich)
├── scripts/           # 独立脚本
└── docker-compose.yml # 本地开发环境
```

---

## API 接口

所有接口以 `/api/v1/` 为前缀。

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/skills` | Skill 列表（分页） |
| GET | `/skills/search` | 混合搜索 |
| GET | `/skills/{slug}` | Skill 详情 |
| GET | `/skills/{slug}/install` | 获取安装信息 |
| GET | `/tags` | 标签列表 |
| GET | `/stats` | 平台统计 |
| GET | `/recommendations` | 每日推荐 |
| POST | `/ingest/skills-sh` | 触发 skills.sh 数据聚合（管理接口） |

---

## 本地开发

### 前置要求
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

### 环境变量

后端 `backend/.env`：
```
DATABASE_URL=postgresql+asyncpg://...
LLM_API_KEY=sk-...            # DashScope (通义千问)
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

前端 `frontend/.env.local`：
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 使用 Docker 一键启动
```bash
docker compose up
```
启动时后端会自动执行数据库迁移，并在检测到空库时导入 50 条 demo 数据。

### 分别启动

**后端**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**前端**
```bash
cd frontend
npm install
npm run dev
```

**CLI**
```bash
cd cli
pip install -e .
skillhub --help
```

---

## 测试

```bash
# 后端
cd backend && pytest

# CLI
cd cli && pytest

# 前端
cd frontend && npm test
```

当前 **167 个测试全部通过**（138 后端 + 13 CLI + 16 前端）。

---

## 项目进度

**V1 已完成并上线** ✅ —— 发现 → 安全审查 → 安装完整闭环已打通。

| Phase | 内容 | 状态 |
|---|---|---|
| Phase 1 | 数据库 Schema 扩展（install_logs、pgvector、新字段） | ✅ |
| Phase 2 | 多层安全审查管道（1-4 层 + LLM 编排） | ✅ |
| Phase 3 | 数据聚合管道（Collector / Normalizer / Enricher） | ✅ |
| Phase 4 | 混合搜索引擎（语义 + 关键词 + 排序） | ✅ |
| Phase 5 | 安装系统 + AgentAdapter + CLI | ✅ |
| Phase 6 | 前端增强（标签浏览 / 推荐 / Vitest 测试） | ✅ |
| 部署 | Railway（后端） + Vercel（前端） + Docker | ✅ |

后续将进入 **V2 迭代**。

---

## 相关文档

- [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) —— 完整产品方案与模块设计
- [AGENTS.md](./AGENTS.md) —— 开发约束与规范
