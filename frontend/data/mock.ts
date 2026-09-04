export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type SecurityLevel = "safe" | "low" | "medium" | "high" | "critical" | "pending";

export interface Finding {
  id: string;
  severity: Severity;
  title: string;
  description: string;
  evidence?: string;
  recommendation: string;
}

export interface SecurityReport {
  level: SecurityLevel;
  score: number;
  findings: Finding[];
  scannedAt: string;
}

export interface Skill {
  slug: string;
  name: string;
  author: string;
  description: string;
  tags: string[];
  capabilities: string[];
  security: SecurityReport;
  installCommand: string;
  downloads: number;
  stars: number;
  createdAt: string;
  updatedAt: string;
  content?: string;
}

export const mockSkills: Skill[] = [
  {
    slug: "web-scraper-pro",
    name: "Web Scraper Pro",
    author: "cyberdev",
    description:
      "高级网页爬虫技能，支持反检测、代理轮换和结构化数据提取。可处理动态 JS 渲染页面。",
    tags: ["scraping", "data-extraction", "automation", "puppeteer"],
    capabilities: ["network_access", "file_write", "process_exec"],
    security: {
      level: "medium",
      score: 58,
      findings: [
        {
          id: "f1",
          severity: "high",
          title: "无限制的网络访问",
          description:
            "该技能可以向任意域名发送 HTTP 请求，没有白名单限制。",
          evidence: `fetch(url, { method: "POST", body: data })`,
          recommendation:
            "添加域名白名单配置，限制出站请求只能访问可信端点。",
        },
        {
          id: "f2",
          severity: "medium",
          title: "文件系统写入无路径限制",
          description:
            "提取的数据直接写入磁盘，未验证输出路径，可能存在路径遍历风险。",
          evidence: `fs.writeFileSync(outputPath, JSON.stringify(data))`,
          recommendation:
            "验证并清理输出路径，限制写入到指定的输出目录。",
        },
        {
          id: "f3",
          severity: "low",
          title: "详细的错误日志",
          description:
            "错误信息可能包含 URL、请求头或部分响应体，这些内容可能包含敏感数据。",
          recommendation:
            "在输出前从错误日志中脱敏敏感字段。",
        },
      ],
      scannedAt: "2026-08-28T10:30:00Z",
    },
    installCommand: "skillhub install web-scraper-pro",
    downloads: 12480,
    stars: 342,
    createdAt: "2026-06-15T08:00:00Z",
    updatedAt: "2026-08-20T14:22:00Z",
    content: `// Web Scraper Pro - Main Entry
const puppeteer = require('puppeteer');

async function scrape(url, options = {}) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setUserAgent(options.userAgent || 'SkillHub-Scraper/1.0');
  await page.goto(url, { waitUntil: 'networkidle2' });
  
  const data = await page.evaluate(() => {
    return document.body.innerText;
  });
  
  await browser.close();
  return { url, data, timestamp: Date.now() };
}

module.exports = { scrape };`,
  },
  {
    slug: "code-reviewer",
    name: "Code Reviewer AI",
    author: "devtools-lab",
    description:
      "自动化代码审查技能，可分析 PR 中的 bug、安全漏洞、性能问题和代码风格一致性。",
    tags: ["code-review", "security", "quality", "AI"],
    capabilities: ["file_read", "llm_call"],
    security: {
      level: "safe",
      score: 92,
      findings: [
        {
          id: "f4",
          severity: "info",
          title: "使用 LLM API 进行分析",
          description:
            "该技能将代码片段发送到 LLM API 进行审查。代码内容通过 TLS 加密传输。",
          recommendation:
            "在用户文档中说明数据传输方式。对于敏感仓库，可考虑使用本地模型。",
        },
      ],
      scannedAt: "2026-08-30T09:15:00Z",
    },
    installCommand: "skillhub install code-reviewer",
    downloads: 28930,
    stars: 891,
    createdAt: "2026-05-10T12:00:00Z",
    updatedAt: "2026-08-25T16:45:00Z",
    content: `// Code Reviewer AI
const { analyzeWithLLM } = require('./analyzer');

async function reviewCode(diff, config = {}) {
  const prompt = buildReviewPrompt(diff, config);
  const result = await analyzeWithLLM(prompt);
  
  return {
    issues: result.issues,
    summary: result.summary,
    severity_counts: countSeverities(result.issues),
  };
}

function buildReviewPrompt(diff, config) {
  return [
    { role: 'system', content: REVIEW_SYSTEM_PROMPT },
    { role: 'user', content: \`Review this diff:\\n\${diff}\` },
  ];
}

module.exports = { reviewCode };`,
  },
  {
    slug: "db-migrator",
    name: "Database Migrator",
    author: "datacraft",
    description:
      "安全的数据库迁移技能，支持回滚、dry-run 模式和 schema diff 可视化。支持 PostgreSQL 和 MySQL。",
    tags: ["database", "migration", "postgresql", "mysql"],
    capabilities: ["network_access", "process_exec", "file_read", "file_write"],
    security: {
      level: "low",
      score: 75,
      findings: [
        {
          id: "f5",
          severity: "medium",
          title: "通过环境变量传递数据库凭证",
          description:
            "凭证从环境变量读取。虽然是标准做法，但可能通过错误信息或日志泄露。",
          evidence: `const connStr = process.env.DATABASE_URL;`,
          recommendation:
            "确保凭证不会包含在错误信息中。生产环境建议使用密钥管理服务。",
        },
        {
          id: "f6",
          severity: "low",
          title: "动态查询执行 SQL",
          description:
            "迁移脚本直接执行 SQL。该技能通过校验和验证迁移文件完整性。",
          recommendation:
            "继续使用校验和机制。可考虑添加语句白名单以增强安全性。",
        },
      ],
      scannedAt: "2026-08-29T11:00:00Z",
    },
    installCommand: "skillhub install db-migrator",
    downloads: 8720,
    stars: 215,
    createdAt: "2026-07-01T09:00:00Z",
    updatedAt: "2026-08-22T10:30:00Z",
    content: `// Database Migrator
const { Client } = require('pg');

async function migrate(config) {
  const client = new Client({ connectionString: config.dbUrl });
  await client.connect();
  
  const migrations = await loadMigrationFiles(config.dir);
  const applied = await getAppliedMigrations(client);
  const pending = migrations.filter(m => !applied.has(m.id));
  
  if (config.dryRun) {
    return { pending: pending.map(m => m.name) };
  }
  
  for (const migration of pending) {
    await client.query(migration.sql);
    await recordMigration(client, migration);
  }
  
  await client.end();
  return { applied: pending.length };
}

module.exports = { migrate };`,
  },
  {
    slug: "prompt-optimizer",
    name: "Prompt Optimizer",
    author: "ai-tools",
    description:
      "分析和优化 LLM 提示词，提升输出质量。包含 token 计数、结构建议和 few-shot 示例生成。",
    tags: ["LLM", "prompt-engineering", "optimization", "NLP"],
    capabilities: ["llm_call", "file_read"],
    security: {
      level: "safe",
      score: 95,
      findings: [
        {
          id: "f7",
          severity: "info",
          title: "提示词内容发送进行分析",
          description:
            "用户提示词被发送到 LLM 进行优化建议。无副作用或系统访问需求。",
          recommendation:
            "无需操作。在文档中说明提示词内容会被传输用于分析。",
        },
      ],
      scannedAt: "2026-08-31T08:00:00Z",
    },
    installCommand: "skillhub install prompt-optimizer",
    downloads: 15600,
    stars: 478,
    createdAt: "2026-06-20T10:00:00Z",
    updatedAt: "2026-08-28T12:00:00Z",
    content: `// Prompt Optimizer
const { countTokens } = require('./tokenizer');
const { callLLM } = require('./llm');

async function optimize(prompt, options = {}) {
  const analysis = {
    tokenCount: countTokens(prompt),
    structure: analyzeStructure(prompt),
    clarity: analyzeClarity(prompt),
  };
  
  const suggestions = await callLLM(
    \`Optimize this prompt: \${prompt}\\nAnalysis: \${JSON.stringify(analysis)}\`
  );
  
  return { original: prompt, optimized: suggestions, analysis };
}

module.exports = { optimize };`,
  },
  {
    slug: "system-monitor",
    name: "System Monitor",
    author: "ops-guru",
    description:
      "实时系统监控技能。跟踪 CPU、内存、磁盘和网络使用情况，支持告警阈值和历史趋势分析。",
    tags: ["monitoring", "devops", "system", "alerts"],
    capabilities: ["process_exec", "network_access", "file_write"],
    security: {
      level: "medium",
      score: 52,
      findings: [
        {
          id: "f8",
          severity: "high",
          title: "通过 shell 命令获取系统指标",
          description:
            "该技能执行系统命令（top、df、netstat）收集指标。如果参数未清理，可能存在命令注入风险。",
          evidence: `execSync(\`top -bn1 | grep \${processName}\`)`,
          recommendation:
            "使用白名单命令，禁止用户控制插值。优先使用原生 OS API 而非 shell 命令。",
        },
        {
          id: "f9",
          severity: "medium",
          title: "告警 webhook 外发",
          description:
            "告警 webhook 将系统指标发送到外部 URL。URL 由用户配置但未经验证。",
          recommendation:
            "针对已知告警服务的 URL 白名单进行验证。",
        },
        {
          id: "f10",
          severity: "low",
          title: "指标存储在本地文件",
          description:
            "历史指标以 JSON 文件形式写入技能的数据目录。",
          recommendation:
            "确保数据目录具有适当的权限。考虑日志轮转机制。",
        },
      ],
      scannedAt: "2026-08-27T14:20:00Z",
    },
    installCommand: "skillhub install system-monitor",
    downloads: 6340,
    stars: 156,
    createdAt: "2026-07-10T11:00:00Z",
    updatedAt: "2026-08-15T09:45:00Z",
    content: `// System Monitor
const { execSync } = require('child_process');

function getCpuUsage() {
  const output = execSync('top -bn1 | head -5').toString();
  return parseCpuLine(output);
}

function getMemoryUsage() {
  const output = execSync('free -m').toString();
  return parseMemoryLines(output);
}

function checkThresholds(metrics, thresholds) {
  const alerts = [];
  for (const [key, limit] of Object.entries(thresholds)) {
    if (metrics[key] > limit) {
      alerts.push({ metric: key, value: metrics[key], threshold: limit });
    }
  }
  return alerts;
}

module.exports = { getCpuUsage, getMemoryUsage, checkThresholds };`,
  },
  {
    slug: "git-workflow",
    name: "Git Workflow Helper",
    author: "devtools-lab",
    description:
      "自动化常见 git 工作流：功能分支、PR 创建、rebase、冲突解决建议和 changelog 生成。",
    tags: ["git", "workflow", "automation", "CLI"],
    capabilities: ["process_exec", "file_read", "file_write"],
    security: {
      level: "low",
      score: 78,
      findings: [
        {
          id: "f11",
          severity: "medium",
          title: "Git 命令执行",
          description:
            "通过 child_process 执行 git 命令。分支名和提交信息被插值到命令中。",
          evidence: `execSync(\`git checkout -b \${branchName}\`)`,
          recommendation:
            "根据 git ref 命名规则验证分支名。对所有插值值进行转义。",
        },
        {
          id: "f12",
          severity: "low",
          title: "Changelog 写入仓库",
          description:
            "生成的 changelog 直接写入仓库。对现有文件没有覆盖保护。",
          recommendation:
            "添加标志控制覆盖行为。写入前备份现有 changelog。",
        },
      ],
      scannedAt: "2026-08-30T16:00:00Z",
    },
    installCommand: "skillhub install git-workflow",
    downloads: 19200,
    stars: 567,
    createdAt: "2026-05-25T14:00:00Z",
    updatedAt: "2026-08-26T11:30:00Z",
    content: `// Git Workflow Helper
const { execSync } = require('child_process');

function createFeatureBranch(name) {
  const sanitized = name.replace(/[^a-zA-Z0-9\\-_\\/]/g, '');
  execSync(\`git checkout -b feature/\${sanitized}\`);
  return \`feature/\${sanitized}\`;
}

function generateChangelog(since) {
  const logs = execSync(
    \`git log \${since}..HEAD --pretty=format:"- %s (%h)"\`
  ).toString();
  return logs;
}

module.exports = { createFeatureBranch, generateChangelog };`,
  },
  {
    slug: "api-fuzzer",
    name: "API Fuzzer",
    author: "sec-research",
    description:
      "自动化 API 模糊测试技能，生成边界输入、测试错误处理，并报告 REST API 中的潜在漏洞。",
    tags: ["security", "testing", "API", "fuzzing"],
    capabilities: ["network_access", "process_exec", "file_write"],
    security: {
      level: "high",
      score: 35,
      findings: [
        {
          id: "f13",
          severity: "critical",
          title: "任意 HTTP 请求构造",
          description:
            "该技能构造并发送任意 HTTP 请求，包括畸形负载。如果没有适当的作用域限制，可能会 targeting 非预期服务。",
          evidence: `axios.request({ method, url: targetUrl, data: payload })`,
          recommendation:
            "要求显式的目标 URL 白名单。扫描非本地端点前需用户确认。",
        },
        {
          id: "f14",
          severity: "high",
          title: "报告生成时的进程执行",
          description:
            "调用外部工具（如 jq、python）进行报告格式化。命令参数包含用户提供的数据。",
          evidence: `execSync(\`python report_gen.py --input \${outputFile}\`)`,
          recommendation:
            "避免 shell 执行。使用原生 Node.js 进行报告生成，或严格验证所有输入。",
        },
        {
          id: "f15",
          severity: "high",
          title: "模糊测试请求无速率限制",
          description:
            "模糊测试请求发送时没有速率限制，可能会压垮目标服务或触发滥用检测。",
          recommendation:
            "添加可配置的速率限制和请求延迟。默认使用保守的速率。",
        },
        {
          id: "f16",
          severity: "medium",
          title: "模糊测试结果中的敏感数据",
          description:
            "模糊测试结果可能包含响应体中的敏感服务器信息。",
          recommendation:
            "在报告中脱敏响应体。仅包含相关错误信息和状态码。",
        },
      ],
      scannedAt: "2026-08-26T09:00:00Z",
    },
    installCommand: "skillhub install api-fuzzer",
    downloads: 3200,
    stars: 89,
    createdAt: "2026-07-20T08:00:00Z",
    updatedAt: "2026-08-18T15:00:00Z",
    content: `// API Fuzzer
const axios = require('axios');

const STRATEGIES = {
  boundary: (field) => [0, -1, Number.MAX_SAFE_INTEGER, '', ' '.repeat(10000)],
  type: (field) => [null, undefined, true, [], {}, 'NaN'],
  injection: (field) => ["' OR 1=1 --", '<script>alert(1)</script>', '{{7*7}}'],
};

async function fuzzEndpoint(baseUrl, schema) {
  const results = [];
  for (const field of Object.keys(schema)) {
    for (const [strategy, values] of Object.entries(STRATEGIES)) {
      for (const value of values) {
        try {
          const res = await axios.post(baseUrl, { [field]: value });
          results.push({ field, strategy, value, status: res.status });
        } catch (err) {
          results.push({ field, strategy, value, error: err.message });
        }
      }
    }
  }
  return results;
}

module.exports = { fuzzEndpoint };`,
  },
  {
    slug: "markdown-translator",
    name: "Markdown Translator",
    author: "i18n-tools",
    description:
      "翻译 markdown 文档，同时保留格式、链接、图片和代码块。支持 30+ 种语言，可自定义术语表。",
    tags: ["i18n", "translation", "markdown", "LLM"],
    capabilities: ["file_read", "file_write", "llm_call"],
    security: {
      level: "safe",
      score: 90,
      findings: [
        {
          id: "f17",
          severity: "info",
          title: "文件内容发送用于翻译",
          description:
            "Markdown 内容被发送到 LLM 进行翻译。默认情况下代码块不参与翻译。",
          recommendation:
            "无需操作。在文档中说明文件内容会被传输用于翻译。",
        },
      ],
      scannedAt: "2026-09-01T07:30:00Z",
    },
    installCommand: "skillhub install markdown-translator",
    downloads: 9870,
    stars: 312,
    createdAt: "2026-06-05T10:00:00Z",
    updatedAt: "2026-08-30T18:00:00Z",
    content: `// Markdown Translator
const { callLLM } = require('./llm');
const { parseMarkdown, rebuildMarkdown } = require('./parser');

async function translate(filePath, targetLang, glossary = {}) {
  const content = await fs.readFile(filePath, 'utf-8');
  const ast = parseMarkdown(content);
  
  const translatable = extractTextNodes(ast);
  const translated = await callLLM(
    \`Translate to \${targetLang}. Glossary: \${JSON.stringify(glossary)}\\n\${translatable.join('\\n')}\`
  );
  
  applyTranslations(ast, translated);
  return rebuildMarkdown(ast);
}

module.exports = { translate };`,
  },
  {
    slug: "env-secrets-scanner",
    name: "Env Secrets Scanner",
    author: "sec-research",
    description:
      "扫描代码库中意外提交的密钥、API key、token 和凭证。支持自定义模式和 CI 集成。",
    tags: ["security", "secrets", "scanning", "CI"],
    capabilities: ["file_read", "process_exec"],
    security: {
      level: "low",
      score: 82,
      findings: [
        {
          id: "f18",
          severity: "medium",
          title: "读取扫描目录中的所有文件",
          description:
            "扫描器递归读取所有文件。二进制文件和大资源文件按扩展名跳过，但其他敏感文件可能被读入内存。",
          recommendation:
            "添加可配置的忽略列表。跳过超过大小阈值的文件。",
        },
        {
          id: "f19",
          severity: "low",
          title: "通过正则表达式进行模式匹配",
          description:
            "密钥检测使用正则表达式模式。自定义模式由用户提供，编译时没有沙箱保护。",
          evidence: `const re = new RegExp(userPattern);`,
          recommendation:
            "验证自定义正则表达式是否存在灾难性回溯。为模式匹配添加超时机制。",
        },
      ],
      scannedAt: "2026-08-31T13:00:00Z",
    },
    installCommand: "skillhub install env-secrets-scanner",
    downloads: 22100,
    stars: 678,
    createdAt: "2026-05-15T09:00:00Z",
    updatedAt: "2026-08-29T20:00:00Z",
    content: `// Env Secrets Scanner
const fs = require('fs');
const path = require('path');

const DEFAULT_PATTERNS = [
  { name: 'AWS Key', pattern: /AKIA[0-9A-Z]{16}/ },
  { name: 'GitHub Token', pattern: /ghp_[a-zA-Z0-9]{36}/ },
  { name: 'Generic Secret', pattern: /(?i)(api[_-]?key|secret|password)\\s*[:=]\\s*['\"][^'\"]{8,}/ },
];

function scanFile(filePath, patterns = DEFAULT_PATTERNS) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const findings = [];
  
  for (const { name, pattern } of patterns) {
    const matches = content.matchAll(new RegExp(pattern, 'g'));
    for (const match of matches) {
      findings.push({ file: filePath, type: name, line: match.index });
    }
  }
  return findings;
}

module.exports = { scanFile, DEFAULT_PATTERNS };`,
  },
  {
    slug: "docker-compose-gen",
    name: "Docker Compose Generator",
    author: "ops-guru",
    description:
      "分析项目结构并生成优化的 docker-compose.yml 文件，包含健康检查、网络配置和卷管理。",
    tags: ["docker", "devops", "automation", "infrastructure"],
    capabilities: ["file_read", "file_write", "process_exec"],
    security: {
      level: "low",
      score: 72,
      findings: [
        {
          id: "f20",
          severity: "medium",
          title: "通过 shell 命令检测项目结构",
          description:
            "使用 find 和 grep 命令检测项目类型。文件路径未完全清理。",
          evidence: `execSync(\`find \${projectDir} -name 'package.json' -maxdepth 2\`)`,
          recommendation:
            "使用 Node.js fs API 代替 shell 命令进行文件检测。验证 projectDir 在预期范围内。",
        },
        {
          id: "f21",
          severity: "low",
          title: "生成的 compose 文件包含默认端口",
          description:
            "默认端口映射可能与主机上现有服务冲突。",
          recommendation:
            "生成前检查端口可用性。允许通过配置覆盖端口。",
        },
      ],
      scannedAt: "2026-08-29T10:45:00Z",
    },
    installCommand: "skillhub install docker-compose-gen",
    downloads: 7450,
    stars: 198,
    createdAt: "2026-07-05T13:00:00Z",
    updatedAt: "2026-08-24T08:15:00Z",
    content: `// Docker Compose Generator
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

function detectProjectType(dir) {
  if (fs.existsSync(path.join(dir, 'package.json'))) return 'node';
  if (fs.existsSync(path.join(dir, 'requirements.txt'))) return 'python';
  if (fs.existsSync(path.join(dir, 'go.mod'))) return 'go';
  return 'unknown';
}

function generateCompose(projectType, options = {}) {
  const services = {};
  
  services.app = {
    build: '.',
    ports: [options.port || '3000:3000'],
    healthcheck: {
      test: ['CMD', 'curl', '-f', 'http://localhost:3000/health'],
      interval: '30s',
      timeout: '10s',
      retries: 3,
    },
  };
  
  if (options.database) {
    services.db = {
      image: options.database === 'postgres' ? 'postgres:16' : 'mysql:8',
      environment: { POSTGRES_PASSWORD: 'changeme' },
      volumes: ['db_data:/var/lib/postgresql/data'],
    };
  }
  
  return yaml.dump({ version: '3.8', services, volumes: { db_data: {} } });
}

module.exports = { detectProjectType, generateCompose };`,
  },
];

export const popularTags = [
  "security",
  "automation",
  "LLM",
  "devops",
  "API",
  "database",
  "git",
  "docker",
  "monitoring",
  "testing",
];

export function getSkillBySlug(slug: string): Skill | undefined {
  return mockSkills.find((s) => s.slug === slug);
}

export function searchSkills(query: string): Skill[] {
  const q = query.toLowerCase();
  return mockSkills.filter(
    (s) =>
      s.name.toLowerCase().includes(q) ||
      s.description.toLowerCase().includes(q) ||
      s.tags.some((t) => t.toLowerCase().includes(q)) ||
      s.capabilities.some((c) => c.toLowerCase().includes(q))
  );
}
