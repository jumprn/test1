# git-ai 本地防冲突脚本

该目录提供一组轻量脚本，用于减少本地开发时 AI 归因与 Git 流程冲突。

## 脚本清单

- `git-ai-preflight.sh`：执行本地预检（冲突状态、hooks、notes 拉取）
- `git-ai-sync-notes.sh`：同步 `refs/notes/ai`，检测 notes 分叉
- `git-ai-safe-pull.sh`：安全拉取（preflight + notes sync + rebase pull）
- `git-ai-safe-rebase.sh`：安全 rebase（自动建备份分支）
- `git-ai-safe-push.sh`：安全推送（代码分支 + notes 一起推）

## 初始化

```bash
chmod +x scripts/git-ai-safety/*.sh
```

## 示例用法

```bash
# 拉取前检查
scripts/git-ai-safety/git-ai-preflight.sh origin

# 安全 pull
scripts/git-ai-safety/git-ai-safe-pull.sh origin main

# 安全 rebase 到 origin/main
scripts/git-ai-safety/git-ai-safe-rebase.sh origin/main origin

# 安全 push 当前分支 + AI notes
scripts/git-ai-safety/git-ai-safe-push.sh origin
```

## 建议别名（可选）

```bash
alias gap='scripts/git-ai-safety/git-ai-preflight.sh'
alias gapull='scripts/git-ai-safety/git-ai-safe-pull.sh'
alias garebase='scripts/git-ai-safety/git-ai-safe-rebase.sh'
alias gapush='scripts/git-ai-safety/git-ai-safe-push.sh'
```

