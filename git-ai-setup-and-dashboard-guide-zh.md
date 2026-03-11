# git-ai 落地技术文档（安装插件 / 部署服务 / 搭建看板）

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
   采集脚本（collector）+ PostgreSQL + Metabase/Grafana

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

## 5.1 推荐最小可用架构

- **采集任务**：Cron / GitHub Actions / Jenkins 定时运行
- **指标库**：PostgreSQL
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

- `repo` (text)
- `commit_sha` (text, unique)
- `authored_at` (timestamp)
- `author_email` (text)
- `ai_lines_added` (int)
- `human_lines_added` (int)
- `unknown_lines_added` (int)
- `git_lines_added` (int)
- `git_lines_deleted` (int)
- `tool` (text)
- `model` (text)
- `ai_lines_generated` (int)
- `ai_deletions_generated` (int)
- `ingested_at` (timestamp default now)

> 实操中可将 `tool_model_breakdown` 拆表存储，便于画模型对比图。

---

## 6. 看板搭建（Metabase 示例）

## 6.1 启动 Metabase + PostgreSQL（Docker）

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: ai
      POSTGRES_PASSWORD: ai123
      POSTGRES_DB: ai_metrics
    ports:
      - "5432:5432"

  metabase:
    image: metabase/metabase:latest
    depends_on:
      - postgres
    ports:
      - "3000:3000"
```

启动：

```bash
docker compose up -d
```

访问 `http://<server>:3000`，连接 PostgreSQL 后创建问题（Question）与仪表盘（Dashboard）。

## 6.2 核心指标 SQL（可直接使用）

### 1）团队日维度 AI 占比

```sql
SELECT
  date(authored_at) AS day,
  SUM(ai_lines_added) AS ai_lines,
  SUM(git_lines_added) AS total_lines,
  ROUND(100.0 * SUM(ai_lines_added) / NULLIF(SUM(git_lines_added), 0), 2) AS ai_pct
FROM ai_commit_stats
WHERE authored_at >= now() - interval '30 days'
GROUP BY 1
ORDER BY 1;
```

### 2）成员维度 AI 占比

```sql
SELECT
  author_email,
  SUM(ai_lines_added) AS ai_lines,
  SUM(git_lines_added) AS total_lines,
  ROUND(100.0 * SUM(ai_lines_added) / NULLIF(SUM(git_lines_added), 0), 2) AS ai_pct
FROM ai_commit_stats
WHERE authored_at >= now() - interval '30 days'
GROUP BY 1
ORDER BY ai_pct DESC;
```

### 3）仓库维度 AI 占比

```sql
SELECT
  repo,
  ROUND(100.0 * SUM(ai_lines_added) / NULLIF(SUM(git_lines_added), 0), 2) AS ai_pct
FROM ai_commit_stats
WHERE authored_at >= now() - interval '30 days'
GROUP BY 1
ORDER BY ai_pct DESC;
```

### 4）工具/模型贡献（需要拆分后表）

```sql
SELECT
  tool,
  model,
  SUM(ai_lines_added) AS ai_lines
FROM ai_commit_stats
WHERE authored_at >= now() - interval '30 days'
GROUP BY 1,2
ORDER BY ai_lines DESC;
```

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

## 10. 实施里程碑（建议）

- **第 1 周**：开发者安装 + 2 仓库接入 + 基础采集入库  
- **第 2 周**：看板上线 + 指标复核 + 误差评估  
- **第 3 周**：扩展到更多仓库并形成内部规范

---

## 11. 参考链接

- git-ai GitHub：`https://github.com/git-ai-project/git-ai`
- git-ai Docs：`https://usegitai.com/docs/cli`
- Cursor 扩展（git-ai-vscode）：`https://marketplace.visualstudio.com/items?itemName=git-ai.git-ai-vscode`

