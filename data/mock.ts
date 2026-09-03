export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type SecurityLevel = "safe" | "low" | "medium" | "high";

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
      "Advanced web scraping skill with anti-detection, proxy rotation, and structured data extraction. Supports dynamic JS-rendered pages.",
    tags: ["scraping", "data-extraction", "automation", "puppeteer"],
    capabilities: ["network_access", "file_write", "process_exec"],
    security: {
      level: "medium",
      score: 58,
      findings: [
        {
          id: "f1",
          severity: "high",
          title: "Unrestricted network access",
          description:
            "The skill can make arbitrary HTTP requests to any domain without allowlist restrictions.",
          evidence: `fetch(url, { method: "POST", body: data })`,
          recommendation:
            "Add a domain allowlist configuration to limit outbound requests to trusted endpoints.",
        },
        {
          id: "f2",
          severity: "medium",
          title: "File system write without path restriction",
          description:
            "Extracted data is written to disk without validating the output path, which could allow path traversal.",
          evidence: `fs.writeFileSync(outputPath, JSON.stringify(data))`,
          recommendation:
            "Validate and sanitize output paths. Restrict writes to a designated output directory.",
        },
        {
          id: "f3",
          severity: "low",
          title: "Verbose error logging",
          description:
            "Error messages may include URLs, headers, or partial response bodies that could contain sensitive data.",
          recommendation:
            "Redact sensitive fields from error logs before outputting.",
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
      "Automated code review skill that analyzes PRs for bugs, security vulnerabilities, performance issues, and style consistency.",
    tags: ["code-review", "security", "quality", "AI"],
    capabilities: ["file_read", "llm_call"],
    security: {
      level: "safe",
      score: 92,
      findings: [
        {
          id: "f4",
          severity: "info",
          title: "LLM API calls for analysis",
          description:
            "This skill sends code snippets to an LLM API for review. Code content is transmitted over TLS.",
          recommendation:
            "Document data transmission in user-facing docs. Consider local model option for sensitive repos.",
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
      "Safe database migration skill with rollback support, dry-run mode, and schema diff visualization. Supports PostgreSQL and MySQL.",
    tags: ["database", "migration", "postgresql", "mysql"],
    capabilities: ["network_access", "process_exec", "file_read", "file_write"],
    security: {
      level: "low",
      score: 75,
      findings: [
        {
          id: "f5",
          severity: "medium",
          title: "Database credentials via environment variables",
          description:
            "Credentials are read from env vars. While standard practice, they could leak through error messages or logs.",
          evidence: `const connStr = process.env.DATABASE_URL;`,
          recommendation:
            "Ensure credentials are never included in error messages. Use a secrets manager for production.",
        },
        {
          id: "f6",
          severity: "low",
          title: "SQL execution with dynamic queries",
          description:
            "Migration scripts execute SQL directly. The skill does validate migration file integrity via checksums.",
          recommendation:
            "Continue using checksums. Consider adding a statement allowlist for extra safety.",
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
      "Analyze and optimize LLM prompts for better output quality. Includes token counting, structure suggestions, and few-shot example generation.",
    tags: ["LLM", "prompt-engineering", "optimization", "NLP"],
    capabilities: ["llm_call", "file_read"],
    security: {
      level: "safe",
      score: 95,
      findings: [
        {
          id: "f7",
          severity: "info",
          title: "Prompt content sent for analysis",
          description:
            "User prompts are sent to an LLM for optimization suggestions. No side effects or system access required.",
          recommendation:
            "No action needed. Document that prompt content is transmitted for analysis.",
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
      "Real-time system monitoring skill. Tracks CPU, memory, disk, and network usage with alerting thresholds and historical trending.",
    tags: ["monitoring", "devops", "system", "alerts"],
    capabilities: ["process_exec", "network_access", "file_write"],
    security: {
      level: "medium",
      score: 52,
      findings: [
        {
          id: "f8",
          severity: "high",
          title: "Shell command execution for system metrics",
          description:
            "The skill executes system commands (top, df, netstat) to gather metrics. Command injection is possible if parameters are not sanitized.",
          evidence: `execSync(\`top -bn1 | grep \${processName}\`)`,
          recommendation:
            "Use allowlisted commands with no user-controlled interpolation. Prefer native OS APIs over shell commands.",
        },
        {
          id: "f9",
          severity: "medium",
          title: "Outbound webhook for alerts",
          description:
            "Alert webhooks send system metrics to external URLs. The URL is user-configured but not validated.",
          recommendation:
            "Validate webhook URLs against an allowlist of known alerting services.",
        },
        {
          id: "f10",
          severity: "low",
          title: "Metrics stored in local files",
          description:
            "Historical metrics are written to JSON files in the skill's data directory.",
          recommendation:
            "Ensure data directory has appropriate permissions. Consider log rotation.",
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
      "Automate common git workflows: feature branches, PR creation, rebasing, conflict resolution suggestions, and changelog generation.",
    tags: ["git", "workflow", "automation", "CLI"],
    capabilities: ["process_exec", "file_read", "file_write"],
    security: {
      level: "low",
      score: 78,
      findings: [
        {
          id: "f11",
          severity: "medium",
          title: "Git command execution",
          description:
            "Executes git commands via child_process. Branch names and commit messages are interpolated into commands.",
          evidence: `execSync(\`git checkout -b \${branchName}\`)`,
          recommendation:
            "Validate branch names against git ref naming rules. Escape all interpolated values.",
        },
        {
          id: "f12",
          severity: "low",
          title: "Changelog written to repository",
          description:
            "Generated changelogs are written directly to the repo. No overwrite protection for existing files.",
          recommendation:
            "Add a flag to control overwrite behavior. Back up existing changelog before writing.",
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
      "Automated API fuzzing skill that generates edge-case inputs, tests error handling, and reports potential vulnerabilities in REST APIs.",
    tags: ["security", "testing", "API", "fuzzing"],
    capabilities: ["network_access", "process_exec", "file_write"],
    security: {
      level: "high",
      score: 35,
      findings: [
        {
          id: "f13",
          severity: "critical",
          title: "Arbitrary HTTP request construction",
          description:
            "The skill constructs and sends arbitrary HTTP requests including malformed payloads. Without proper scoping, it could target unintended services.",
          evidence: `axios.request({ method, url: targetUrl, data: payload })`,
          recommendation:
            "Require explicit target URL allowlist. Add confirmation before scanning non-local endpoints.",
        },
        {
          id: "f14",
          severity: "high",
          title: "Process execution for report generation",
          description:
            "External tools (e.g., jq, python) are invoked for report formatting. Command arguments include user-provided data.",
          evidence: `execSync(\`python report_gen.py --input \${outputFile}\`)`,
          recommendation:
            "Avoid shell execution. Use native Node.js for report generation or validate all inputs strictly.",
        },
        {
          id: "f15",
          severity: "high",
          title: "No rate limiting on fuzz requests",
          description:
            "Fuzz requests are sent without rate limiting, which could overwhelm target services or trigger abuse detection.",
          recommendation:
            "Add configurable rate limiting and request delays. Default to conservative rates.",
        },
        {
          id: "f16",
          severity: "medium",
          title: "Sensitive data in fuzz results",
          description:
            "Fuzz results may include response bodies containing sensitive server information.",
          recommendation:
            "Redact response bodies in reports. Only include relevant error messages and status codes.",
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
      "Translate markdown documents while preserving formatting, links, images, and code blocks. Supports 30+ languages with glossary customization.",
    tags: ["i18n", "translation", "markdown", "LLM"],
    capabilities: ["file_read", "file_write", "llm_call"],
    security: {
      level: "safe",
      score: 90,
      findings: [
        {
          id: "f17",
          severity: "info",
          title: "File content sent for translation",
          description:
            "Markdown content is sent to an LLM for translation. Code blocks are excluded from translation by default.",
          recommendation:
            "No action needed. Document that file content is transmitted for translation.",
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
      "Scan codebases for accidentally committed secrets, API keys, tokens, and credentials. Supports custom patterns and CI integration.",
    tags: ["security", "secrets", "scanning", "CI"],
    capabilities: ["file_read", "process_exec"],
    security: {
      level: "low",
      score: 82,
      findings: [
        {
          id: "f18",
          severity: "medium",
          title: "Reads all files in scan directory",
          description:
            "The scanner reads all files recursively. Binary files and large assets are skipped by extension, but other sensitive files may be read into memory.",
          recommendation:
            "Add a configurable ignore list. Skip files above a size threshold.",
        },
        {
          id: "f19",
          severity: "low",
          title: "Pattern matching via regex",
          description:
            "Secret detection uses regex patterns. Custom patterns are user-provided and compiled without sandboxing.",
          evidence: `const re = new RegExp(userPattern);`,
          recommendation:
            "Validate custom regex patterns for catastrophic backtracking. Add a timeout for pattern matching.",
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
      "Analyze your project structure and generate optimized docker-compose.yml files with health checks, networking, and volume management.",
    tags: ["docker", "devops", "automation", "infrastructure"],
    capabilities: ["file_read", "file_write", "process_exec"],
    security: {
      level: "low",
      score: 72,
      findings: [
        {
          id: "f20",
          severity: "medium",
          title: "Project structure detection via shell commands",
          description:
            "Uses find and grep commands to detect project type. File paths are not fully sanitized.",
          evidence: `execSync(\`find \${projectDir} -name 'package.json' -maxdepth 2\`)`,
          recommendation:
            "Use Node.js fs APIs instead of shell commands for file detection. Validate projectDir is within expected bounds.",
        },
        {
          id: "f21",
          severity: "low",
          title: "Generated compose file includes default ports",
          description:
            "Default port mappings could conflict with existing services on the host machine.",
          recommendation:
            "Check for port availability before generating. Allow port override via config.",
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
