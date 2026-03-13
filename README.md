# git-ai 覆盖率统计脚本

这个仓库提供了一个零第三方 Python 依赖的脚本，用来基于 [`git-ai`](https://usegitai.com/docs/cli) 统计 AI 生成代码覆盖率。

支持两种场景：

1. **本地个人统计**：直接在当前仓库统计“我个人”的 AI 代码覆盖率。
2. **远程全员统计**：传入远程仓库地址后，克隆/更新仓库并统计所有贡献者的 AI 代码覆盖率。

脚本路径：

```bash
scripts/git_ai_coverage.py
```

## 一、前置条件

### 1. 安装 git-ai

```bash
curl -sSL https://usegitai.com/install.sh | bash
```

安装后建议确认：

```bash
git-ai --help
```

### 2. 确保仓库已经有 git-ai 数据

这个脚本依赖 `git-ai stats <commit> --json` 返回的提交级统计数据，因此前提是：

- 你的开发流程已经接入 `git-ai`
- 已经正确安装 hooks / checkpoint
- 目标仓库中的提交包含 git-ai 可识别的 AI 归因信息

如果仓库没有接入 git-ai，脚本仍然可以运行，但统计结果可能全是 0，或者部分 commit 无法读取。

## 二、本地统计我个人的 AI 覆盖率

默认读取当前仓库和当前 Git 身份（`git config user.name` / `git config user.email`）：

```bash
python3 scripts/git_ai_coverage.py local
```

如果你的提交邮箱和本机 Git 配置不一致，可以显式指定：

```bash
python3 scripts/git_ai_coverage.py local --author-email you@example.com
```

如果你要统计指定时间段内我个人的 AI 覆盖率：

```bash
python3 scripts/git_ai_coverage.py local \
  --since 2026-03-01 \
  --until 2026-03-31
```

如果要输出 JSON：

```bash
python3 scripts/git_ai_coverage.py local --json
```

如果要把 JSON 结果写入文件：

```bash
python3 scripts/git_ai_coverage.py local --json-output ./local-ai-coverage.json
```

## 三、配置远程仓库地址后，统计所有贡献者 AI 覆盖率

最直接的用法：

```bash
python3 scripts/git_ai_coverage.py remote-all \
  --remote-url https://github.com/your-org/your-repo.git
```

如果你希望复用一个本地 clone 目录，避免每次都重新拉仓库：

```bash
python3 scripts/git_ai_coverage.py remote-all \
  --remote-url https://github.com/your-org/your-repo.git \
  --clone-dir ./.cache/your-repo
```

如果远程仓库需要先切到指定分支再统计：

```bash
python3 scripts/git_ai_coverage.py remote-all \
  --remote-url https://github.com/your-org/your-repo.git \
  --branch master
```

如果你要统计指定时间段内所有贡献者的 AI 覆盖率：

```bash
python3 scripts/git_ai_coverage.py remote-all \
  --remote-url https://github.com/your-org/your-repo.git \
  --since 2026-03-01 \
  --until 2026-03-31
```

如果要导出 JSON：

```bash
python3 scripts/git_ai_coverage.py remote-all \
  --remote-url https://github.com/your-org/your-repo.git \
  --json-output ./all-contributors-ai-coverage.json
```

## 四、统计口径说明

脚本主要聚合 `git-ai stats --json` 中这些字段：

- `ai_additions`
- `human_additions`
- `mixed_additions`
- `ai_accepted`
- `total_ai_additions`
- `total_ai_deletions`
- `time_waiting_for_ai`

其中脚本里的**AI 覆盖率**定义为：

```text
AI 覆盖率 = ai_additions / (ai_additions + human_additions) * 100%
```

另外还会额外输出：

- **直接接受 AI 覆盖率** = `ai_accepted / (ai_additions + human_additions)`
- **混合改写占比** = `mixed_additions / (ai_additions + human_additions)`
- **AI 接受率** = `ai_accepted / ai_additions`

## 五、常用参数

### 通用参数

```bash
--revision <rev>
```

默认 `HEAD`，也支持：

- 分支名：`master`
- 标签：`v1.0.0`
- 范围：`abc123..def456`

```bash
--since <time>
```

仅统计该时间之后（含）的提交。

```bash
--until <time>
```

仅统计该时间之前（含）的提交。

时间参数直接使用 Git 的日期解析能力，常见写法包括：

- `2026-03-01`
- `2026-03-01 00:00:00`
- `yesterday`
- `2.weeks.ago`

其中如果传入纯日期（如 `2026-03-01`），脚本会自动按本地时区扩展为整天范围：

- `--since 2026-03-01` -> 当天 `00:00:00`
- `--until 2026-03-31` -> 当天 `23:59:59`

```bash
--workers <N>
```

并发读取 `git-ai stats` 的 worker 数。仓库提交很多时可适当调大。

```bash
--no-merges
```

忽略 merge commit。

```bash
--json
```

将结果直接以 JSON 打印到标准输出。

```bash
--json-output <file>
```

把 JSON 结果写入文件。

## 六、示例输出

### 1. 本地个人统计

```text
Git AI 本地个人覆盖率统计
================================
仓库路径: /path/to/repo
统计范围: HEAD
时间范围: 2026-03-01 ~ 2026-03-31
统计对象: Alice <alice@example.com>
提交数: 12
提交入库总行数: 1830
AI 行数(ai_additions): 910
人工行数(human_additions): 920
混合行数(mixed_additions): 210
直接接受的 AI 行数(ai_accepted): 700
AI 覆盖率: 49.73%
直接接受 AI 覆盖率: 38.25%
混合改写占比: 11.48%
AI 接受率(ai_accepted / ai_additions): 76.92%
```

### 2. 所有贡献者统计

```text
Git AI 全量贡献者覆盖率统计
================================
远程仓库: https://github.com/your-org/your-repo.git
统计范围: HEAD
时间范围: 2026-03-01 ~ 2026-03-31

排序规则: 按提交入库总行数(committed_additions)降序

贡献者                                     提交数       总行数       AI行数      AI覆盖率    直接接受AI
----------------------------------------------------------------------------------------------------
Alice <alice@example.com>                    12        1830        910       49.73%       38.25%
Bob <bob@example.com>                         8         940        120       12.77%        7.45%
Carol <carol@example.com>                     5         420          0        0.00%        0.00%
```

## 七、注意事项

1. 远程仓库模式统计的是 **git revision 范围内、且满足 `--since/--until` 条件的提交作者**，默认是 `HEAD` 所在历史。
2. 作者归并使用 `git log --use-mailmap`，因此仓库如果配置了 `.mailmap`，别名邮箱会自动折叠。
3. 如果某些 commit 没有 git-ai 元数据，脚本会在结果里给出失败列表，不会直接中断整个统计流程。
4. 仓库很大时，逐 commit 调用 `git-ai stats` 可能需要较长时间，建议使用 `--workers` 和 `--clone-dir`。
