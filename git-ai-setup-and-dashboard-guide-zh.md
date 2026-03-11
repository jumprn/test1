# git-ai 落地技术文档（MySQL 版：安装插件 / 部署服务 / 搭建看板）

## 1. 文档目标

本文用于指导团队从 0 到 1 搭建 git-ai 统计链路，实现以下目标：

- 在 Cursor / Claude Code 里采集 AI 代码归因
- 在 GitHub 流程（含 squash/rebase）中尽量保持归因连续
- 建立可视化看板，统计团队 AI 代码占比（成员/仓库/时间维度）

---

## 2. 方案总览

### 2.1 架构分层

1. **开发者侧（必选）**  
   安装 git-ai CLI + 编辑器插件（Cursor）+ agent hooks（Cursor/Claude）

2. **仓库侧 CI（强烈建议）**  
   安装 git-ai GitHub CI workflow，处理合并后归因维护

3. **数据与看板层（自建）**  
   采集脚本（collector）+ MySQL + Metabase/Grafana

### 2.2 为什么这么分层

- 开源 git-ai 侧重“归因采集与追踪”
- 团队级“报表与管理看板”通常需要你们自己做数据汇总
- 该方式成本低、可控、可扩展，适合内部长期运营

---

## 3. 开发者侧安装与接入

## 3.1 安装 git-ai CLI

Linux / macOS / WSL：

```bash
curl -sSL https://usegitai.com/install.sh | bash
source ~/.bashrc
git-ai --version
```

> 备注：Windows 非 WSL 场景可使用官方 PowerShell 安装脚本。

## 3.2 安装 Cursor 插件

- 在 Cursor 扩展市场搜索：`git-ai-vscode`
- 扩展 ID：`git-ai.git-ai-vscode`

安装后可获得行级归因提示（gutter blame 展示）。

## 3.3 安装/修复 hooks（Cursor + Claude Code）

```bash
git-ai install-hooks
git-ai git-hooks ensure
git-ai status
```

## 3.4 快速验证（建议每位成员完成）

1. 用 Cursor 或 Claude Code 修改并提交一次代码  
2. 本地执行：

```bash
git-ai stats --json
git-ai diff HEAD --json --include-stats
git-ai blame <文件路径>
```

能看到统计 JSON/行级归因，即接入成功。

---

## 4. 仓库侧：CI 工作流部署（GitHub）

为避免 squash/rebase 合并后归因丢失，建议每个仓库安装 git-ai 工作流：

```bash
git-ai ci github install
```

该命令会在仓库中生成或更新 `.github/workflows/git-ai.yaml`。  
建议在主干仓库统一启用。

---

## 5. 数据服务化：采集、入库、调度

## 5.1 推荐最小可用架构（MySQL）

- **采集任务**：Cron / GitHub Actions / Jenkins 定时运行
- **指标库**：MySQL 8.0+
- **可视化**：Metabase（免费）或 Grafana

## 5.2 采集逻辑（建议）

按仓库、按时间窗口拉取提交，然后逐个 commit 解析：

```bash
git-ai diff <commit_sha> --json --include-stats
```

从输出中提取：

- `commit_stats.ai_lines_added`
- `commit_stats.human_lines_added`
- `commit_stats.unknown_lines_added`
- `commit_stats.git_lines_added`
- `commit_stats.git_lines_deleted`
- `commit_stats.tool_model_breakdown`

并结合 commit 作者/时间，落库。

## 5.3 建议数据表（核心）

表名：`ai_commit_stats`

字段建议：

- `repo` (varchar(255))
- `commit_sha` (char(40), unique)
- `authored_at` (datetime)
- `author_email` (varchar(255))
- `ai_lines_added` (int)
- `human_lines_added` (int)
- `unknown_lines_added` (int)
- `git_lines_added` (int)
- `git_lines_deleted` (int)
- `tool` (varchar(64))
- `model` (varchar(128))
- `ai_lines_generated` (int)
- `ai_deletions_generated` (int)
- `ingested_at` (timestamp default current_timestamp)

> 实操中可将 `tool_model_breakdown` 拆表存储，便于画模型对比图。

## 5.4 MySQL 建表 SQL（可直接执行）

```sql
CREATE DATABASE IF NOT EXISTS ai_metrics
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE ai_metrics;

CREATE TABLE IF NOT EXISTS ai_commit_stats (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  repo VARCHAR(255) NOT NULL,
  commit_sha CHAR(40) NOT NULL,
  authored_at DATETIME NOT NULL,
  author_email VARCHAR(255) NOT NULL,
  ai_lines_added INT NOT NULL DEFAULT 0,
  human_lines_added INT NOT NULL DEFAULT 0,
  unknown_lines_added INT NOT NULL DEFAULT 0,
  git_lines_added INT NOT NULL DEFAULT 0,
  git_lines_deleted INT NOT NULL DEFAULT 0,
  tool VARCHAR(64) NOT NULL DEFAULT 'unknown',
  model VARCHAR(128) NOT NULL DEFAULT 'unknown',
  ai_lines_generated INT NOT NULL DEFAULT 0,
  ai_deletions_generated INT NOT NULL DEFAULT 0,
  ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_repo_commit_tool_model (repo, commit_sha, tool, model),
  KEY idx_authored_at (authored_at),
  KEY idx_author_email (author_email),
  KEY idx_repo_authored_at (repo, authored_at),
  KEY idx_tool_model (tool, model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

## 5.5 采集入库 UPSERT（MySQL）

建议采集脚本按 commit+tool+model 做幂等写入：

```sql
INSERT INTO ai_commit_stats (
  repo, commit_sha, authored_at, author_email,
  ai_lines_added, human_lines_added, unknown_lines_added,
  git_lines_added, git_lines_deleted,
  tool, model, ai_lines_generated, ai_deletions_generated
) VALUES (
  ?, ?, ?, ?,
  ?, ?, ?,
  ?, ?,
  ?, ?, ?, ?
)
ON DUPLICATE KEY UPDATE
  authored_at = VALUES(authored_at),
  author_email = VALUES(author_email),
  ai_lines_added = VALUES(ai_lines_added),
  human_lines_added = VALUES(human_lines_added),
  unknown_lines_added = VALUES(unknown_lines_added),
  git_lines_added = VALUES(git_lines_added),
  git_lines_deleted = VALUES(git_lines_deleted),
  ai_lines_generated = VALUES(ai_lines_generated),
  ai_deletions_generated = VALUES(ai_deletions_generated),
  ingested_at = CURRENT_TIMESTAMP;
```

---

## 6. 看板搭建（Metabase + MySQL 示例）

## 6.1 启动 Metabase + MySQL（Docker）

```yaml
version: "3.9"

services:
  mysql:
    image: mysql:8.4
    command: --default-authentication-plugin=mysql_native_password
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: ai_metrics
      MYSQL_USER: ai
      MYSQL_PASSWORD: ai123
      TZ: Asia/Shanghai
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-proot123"]
      interval: 10s
      timeout: 5s
      retries: 10
    volumes:
      - mysql_data:/var/lib/mysql

  metabase:
    image: metabase/metabase:latest
    depends_on:
      mysql:
        condition: service_healthy
    ports:
      - "3000:3000"

volumes:
  mysql_data:
```

启动：

```bash
docker compose up -d
```

访问 `http://<server>:3000`，选择 MySQL 数据源（host 填 `mysql` 或服务器地址，端口 `3306`）后创建问题（Question）与仪表盘（Dashboard）。

## 6.2 核心指标 SQL（可直接使用）

### 1）团队日维度 AI 占比

```sql
SELECT
  date(authored_at) AS day,
  SUM(ai_lines_added) AS ai_lines,
  SUM(git_lines_added) AS total_lines,
  ROUND(100.0 * SUM(ai_lines_added) / NULLIF(SUM(git_lines_added), 0), 2) AS ai_pct
FROM ai_commit_stats
WHERE authored_at >= NOW() - INTERVAL 30 DAY
GROUP BY day
ORDER BY day;
```

### 2）成员维度 AI 占比

```sql
SELECT
  author_email,
  SUM(ai_lines_added) AS ai_lines,
  SUM(git_lines_added) AS total_lines,
  ROUND(100.0 * SUM(ai_lines_added) / NULLIF(SUM(git_lines_added), 0), 2) AS ai_pct
FROM ai_commit_stats
WHERE authored_at >= NOW() - INTERVAL 30 DAY
GROUP BY author_email
ORDER BY ai_pct DESC;
```

### 3）仓库维度 AI 占比

```sql
SELECT
  repo,
  ROUND(100.0 * SUM(ai_lines_added) / NULLIF(SUM(git_lines_added), 0), 2) AS ai_pct
FROM ai_commit_stats
WHERE authored_at >= NOW() - INTERVAL 30 DAY
GROUP BY repo
ORDER BY ai_pct DESC;
```

### 4）工具/模型贡献（需要拆分后表）

```sql
SELECT
  tool,
  model,
  SUM(ai_lines_added) AS ai_lines
FROM ai_commit_stats
WHERE authored_at >= NOW() - INTERVAL 30 DAY
GROUP BY tool, model
ORDER BY ai_lines DESC;
```

## 6.3 推荐看板布局（优化版）

建议首页按“总览 + 诊断”两层展示：

1. **总览区**
   - 最近 30 天 AI 新增占比（折线）
   - 本周 AI 行数 / 总新增行（指标卡）
   - Top 仓库 AI 占比（条形图）

2. **诊断区**
   - 成员维度 AI 占比分布（条形图）
   - 工具/模型贡献趋势（堆叠图）
   - 异常仓库（AI 占比突增）告警表

> 告警建议：当某仓库周环比增幅 > 30% 且总新增行 > 阈值时标红。

---

## 7. 统计口径建议（上线前先统一）

建议默认主口径：

- **AI 新增占比** = `ai_lines_added / git_lines_added`

可选补充口径：

- **AI 变更占比** = `AI 变更行 / (git_lines_added + git_lines_deleted)`
- **成员 AI 占比分布**：P50 / P90
- **仓库 AI 占比趋势**：按周滚动

> 重点：口径一旦发布，尽量不要频繁变化，否则跨周期不可比。

---

## 8. 运行与治理建议

1. **先 PoC 再全量**  
   先选 1~2 个仓库、8~15 人，跑 2 周验证稳定性与可信度。

2. **排除噪音文件**  
   生成代码、lockfile、snapshot 建议剔除，避免占比虚高。

3. **不要单独用于绩效考核**  
   AI 占比应与质量指标（缺陷率、回滚率、review 通过率）联合评估。

4. **关注隐私与合规**  
   若要保存 prompts/transcript，需遵循内部数据治理要求。

5. **MySQL 运维建议（生产）**  
   建议开启 binlog、定期备份（全量+增量），并对 `ai_commit_stats` 做月度归档或分区策略。

---

## 9. 运维排障清单

### 9.1 常用命令

```bash
git-ai --help
git-ai status
git-ai stats --json
git-ai diff HEAD --json --include-stats
git-ai git-hooks ensure
```

### 9.2 常见问题

- **问题：统计一直为 0**  
  排查：是否已安装 hooks、是否确实使用 AI 工具改动代码、是否提交到了目标分支。

- **问题：Cursor 插件未自动安装**  
  排查：手动在扩展市场安装 `git-ai-vscode`。

- **问题：合并后归因断裂**  
  排查：仓库是否启用 `git-ai ci github install` 生成的 workflow。

---

## 10. git-ai 本地防冲突脚本（新增）

为降低本地开发中的分支冲突、notes 分叉、hooks 失效风险，建议在仓库中统一使用以下脚本：

- `scripts/git-ai-safety/git-ai-preflight.sh`
- `scripts/git-ai-safety/git-ai-sync-notes.sh`
- `scripts/git-ai-safety/git-ai-safe-pull.sh`
- `scripts/git-ai-safety/git-ai-safe-rebase.sh`
- `scripts/git-ai-safety/git-ai-safe-push.sh`

### 10.1 一次性初始化

```bash
chmod +x scripts/git-ai-safety/*.sh
```

### 10.2 推荐日常流程

```bash
# 1) 拉取前预检
scripts/git-ai-safety/git-ai-preflight.sh origin

# 2) 安全 pull（rebase 模式）
scripts/git-ai-safety/git-ai-safe-pull.sh origin main

# 3) 开发与提交（正常 git add/commit）

# 4) 需要对齐主干时，使用安全 rebase
scripts/git-ai-safety/git-ai-safe-rebase.sh origin/main origin

# 5) 推送代码 + AI notes
scripts/git-ai-safety/git-ai-safe-push.sh origin
```

### 10.3 脚本能力说明

- `preflight`：检查未完成 rebase/merge、索引冲突、hooks 状态，并尝试同步远端信息
- `sync-notes`：同步 `refs/notes/ai`；若检测到分叉会保留远端临时 ref，避免直接覆盖
- `safe-pull`：仅在工作区干净时执行，默认 `pull --rebase --autostash`
- `safe-rebase`：rebase 前自动创建备份分支，冲突时可快速回滚
- `safe-push`：先推代码分支，再推 `refs/notes/ai`，保证归因链尽量同步

> 说明：脚本采用“保守策略”（遇到风险先阻断），优先保证归因数据不被误覆盖。

---

## 11. 实施里程碑（建议）

- **第 1 周**：开发者安装 + 2 仓库接入 + 基础采集入库  
- **第 2 周**：看板上线 + 指标复核 + 误差评估  
- **第 3 周**：扩展到更多仓库并形成内部规范

---

## 12. 参考链接

- git-ai GitHub：`https://github.com/git-ai-project/git-ai`
- git-ai Docs：`https://usegitai.com/docs/cli`
- Cursor 扩展（git-ai-vscode）：`https://marketplace.visualstudio.com/items?itemName=git-ai.git-ai-vscode`

