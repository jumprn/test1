#!/usr/bin/env python3
"""Aggregate git-ai authorship coverage for local or remote repositories.

This script provides two workflows:
1. local:    calculate AI code coverage for the current user in the current repo.
2. remote-all: clone/fetch a remote repo and calculate AI coverage for all contributors.

The implementation relies on `git-ai stats <commit> --json` and aggregates metrics
per commit author. It does not require any third-party Python packages.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


NUMERIC_FIELDS = (
    "ai_additions",
    "human_additions",
    "mixed_additions",
    "ai_accepted",
    "total_ai_additions",
    "total_ai_deletions",
    "time_waiting_for_ai",
)

DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ScriptError(RuntimeError):
    """Raised when the script cannot continue."""


@dataclass(frozen=True)
class Contributor:
    """Canonical contributor identity after `git log --use-mailmap`."""

    name: str
    email: str

    @property
    def label(self) -> str:
        return f"{self.name} <{self.email}>"


def run_command(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a command and return the completed process."""

    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=capture_output,
        check=False,
    )
    if check and result.returncode != 0:
        command_text = " ".join(cmd)
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        message = stderr or stdout or f"exit code {result.returncode}"
        raise ScriptError(f"命令执行失败: {command_text}\n{message}")
    return result


def ensure_command_exists(command: str, install_hint: str) -> None:
    """Ensure an external command exists."""

    if shutil.which(command):
        return
    raise ScriptError(f"未检测到 `{command}` 命令。\n{install_hint}")


def ensure_git_repository(repo: Path) -> None:
    """Ensure the target path is a git repository."""

    run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo)


def git_config_get(repo: Path, key: str) -> str | None:
    """Read a git config value or return None."""

    result = run_command(["git", "config", "--get", key], cwd=repo, check=False)
    value = result.stdout.strip()
    return value or None


def normalize_number(value: Any) -> float:
    """Convert numeric-ish values to float."""

    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return 0.0
        try:
            return float(stripped)
        except ValueError as exc:
            raise ScriptError(f"无法解析数字字段值: {value!r}") from exc
    raise ScriptError(f"不支持的数字字段类型: {type(value).__name__}")


def merge_nested_numbers(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Recursively merge numeric leaves inside nested mappings."""

    for key, value in source.items():
        if isinstance(value, dict):
            existing = target.setdefault(key, {})
            if not isinstance(existing, dict):
                target[key] = {}
                existing = target[key]
            merge_nested_numbers(existing, value)
            continue

        target[key] = normalize_number(target.get(key, 0.0)) + normalize_number(value)


def make_empty_summary() -> dict[str, Any]:
    """Build a blank aggregate summary."""

    summary = {field: 0.0 for field in NUMERIC_FIELDS}
    summary.update(
        {
            "commits": 0,
            "tool_model_breakdown": {},
        }
    )
    return summary


def annotate_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Attach derived metrics for display/export."""

    committed_additions = summary["ai_additions"] + summary["human_additions"]
    summary["committed_additions"] = committed_additions
    summary["ai_coverage_pct"] = (
        summary["ai_additions"] / committed_additions * 100.0 if committed_additions else 0.0
    )
    summary["accepted_ai_coverage_pct"] = (
        summary["ai_accepted"] / committed_additions * 100.0 if committed_additions else 0.0
    )
    summary["mixed_additions_pct"] = (
        summary["mixed_additions"] / committed_additions * 100.0 if committed_additions else 0.0
    )
    summary["accepted_of_ai_pct"] = (
        summary["ai_accepted"] / summary["ai_additions"] * 100.0 if summary["ai_additions"] else 0.0
    )
    return summary


def aggregate_stats(stats_list: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate a list of git-ai stats objects."""

    summary = make_empty_summary()
    for item in stats_list:
        summary["commits"] += 1
        for field in NUMERIC_FIELDS:
            summary[field] += normalize_number(item.get(field, 0.0))
        breakdown = item.get("tool_model_breakdown") or {}
        if not isinstance(breakdown, dict):
            raise ScriptError("git-ai 返回的 tool_model_breakdown 不是对象。")
        merge_nested_numbers(summary["tool_model_breakdown"], breakdown)
    return annotate_summary(summary)


def append_time_filters(cmd: list[str], *, since: str | None, until: str | None) -> None:
    """Append git-log compatible time filters."""

    if since:
        cmd.extend(["--since", normalize_git_time_input(since, is_until=False)])
    if until:
        cmd.extend(["--until", normalize_git_time_input(until, is_until=True)])


def local_timezone_suffix() -> str:
    """Return the local timezone offset in ISO-8601 form."""

    offset = datetime.now().astimezone().strftime("%z")
    return f"{offset[:3]}:{offset[3:]}"


def normalize_git_time_input(value: str, *, is_until: bool) -> str:
    """Normalize date-only inputs so common range queries match full days.

    Git's natural date parser can be inconsistent for bare YYYY-MM-DD values across
    environments. When a user passes a date-only string, expand it to the full day
    in the local timezone so common reporting commands behave predictably.
    """

    normalized = value.strip()
    if not DATE_ONLY_RE.fullmatch(normalized):
        return normalized

    boundary = "23:59:59" if is_until else "00:00:00"
    return f"{normalized}T{boundary}{local_timezone_suffix()}"


def format_time_filter_label(*, since: str | None, until: str | None) -> str:
    """Return a human-readable time range label."""

    if since and until:
        return f"{since} ~ {until}"
    if since:
        return f">= {since}"
    if until:
        return f"<= {until}"
    return "全部时间"


def parse_git_log(
    repo: Path,
    revision: str,
    no_merges: bool,
    *,
    since: str | None,
    until: str | None,
) -> list[tuple[str, Contributor]]:
    """Return commit -> contributor pairs from git log using mailmap."""

    format_spec = "%H%x1f%aN%x1f%aE%x1e"
    cmd = ["git", "log", "--use-mailmap", f"--format={format_spec}"]
    if no_merges:
        cmd.append("--no-merges")
    append_time_filters(cmd, since=since, until=until)
    cmd.append(revision)

    output = run_command(cmd, cwd=repo).stdout
    entries: list[tuple[str, Contributor]] = []
    for raw_record in output.split("\x1e"):
        record = raw_record.strip()
        if not record:
            continue
        parts = record.split("\x1f")
        if len(parts) != 3:
            raise ScriptError(f"无法解析 git log 记录: {record!r}")
        commit, name, email = (part.strip() for part in parts)
        if not commit:
            continue
        entries.append((commit, Contributor(name=name, email=email)))
    return entries


def select_local_contributor(
    contributors: list[Contributor],
    *,
    author_name: str | None,
    author_email: str | None,
) -> Contributor:
    """Resolve the current user against contributors found in the repository."""

    if not author_name and not author_email:
        raise ScriptError(
            "无法确定本地身份，请先设置 git config user.name / user.email，"
            "或使用 --author-name / --author-email 显式传入。"
        )

    if author_email:
        for contributor in contributors:
            if contributor.email.lower() == author_email.lower():
                return contributor

    if author_name:
        exact_name_matches = [c for c in contributors if c.name == author_name]
        if len(exact_name_matches) == 1:
            return exact_name_matches[0]

    debug_identities = ", ".join(sorted({contributor.label for contributor in contributors}))
    raise ScriptError(
        "在当前 revision 中未找到与本地身份匹配的提交作者。\n"
        f"传入的身份: name={author_name!r}, email={author_email!r}\n"
        f"当前可识别作者: {debug_identities or '无'}"
    )


def git_ai_stats_for_commit(repo: Path, commit: str) -> dict[str, Any]:
    """Get `git-ai stats` JSON for one commit with a fallback flag order."""

    commands = (
        ["git-ai", "stats", commit, "--json"],
        ["git-ai", "stats", "--json", commit],
    )
    last_error: str | None = None

    for cmd in commands:
        result = run_command(cmd, cwd=repo, check=False)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()
            last_error = stderr or stdout or f"exit code {result.returncode}"
            continue
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ScriptError(
                f"git-ai stats 输出不是合法 JSON，commit={commit}\n输出内容:\n{result.stdout}"
            ) from exc
        if not isinstance(data, dict):
            raise ScriptError(f"git-ai stats JSON 顶层不是对象，commit={commit}")
        return data

    raise ScriptError(f"无法读取 commit {commit} 的 git-ai 统计信息。\n{last_error or ''}".strip())


def load_commit_stats(
    repo: Path,
    commits: list[str],
    *,
    workers: int,
    progress: bool,
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Load git-ai stats for a commit list concurrently."""

    if not commits:
        return {}, {}

    stats_by_commit: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    total = len(commits)

    with ThreadPoolExecutor(max_workers=max(workers, 1)) as executor:
        future_map = {
            executor.submit(git_ai_stats_for_commit, repo, commit): commit for commit in commits
        }
        completed = 0
        for future in as_completed(future_map):
            commit = future_map[future]
            completed += 1
            try:
                stats_by_commit[commit] = future.result()
            except Exception as exc:  # noqa: BLE001
                errors[commit] = str(exc)

            if progress and (completed == total or completed == 1 or completed % 25 == 0):
                print(
                    f"[progress] 已处理 {completed}/{total} 个 commit",
                    file=sys.stderr,
                )

    return stats_by_commit, errors


def format_number(value: float) -> str:
    """Render numbers cleanly for humans."""

    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.2f}"


def format_pct(value: float) -> str:
    """Render percentages cleanly."""

    return f"{value:.2f}%"


def render_local_report(
    *,
    repo: Path,
    revision: str,
    time_range: str,
    contributor: Contributor,
    summary: dict[str, Any],
    errors: dict[str, str],
) -> str:
    """Render a human-readable local report."""

    lines = [
        "Git AI 本地个人覆盖率统计",
        "=" * 32,
        f"仓库路径: {repo}",
        f"统计范围: {revision}",
        f"时间范围: {time_range}",
        f"统计对象: {contributor.label}",
        f"提交数: {summary['commits']}",
        f"提交入库总行数: {format_number(summary['committed_additions'])}",
        f"AI 行数(ai_additions): {format_number(summary['ai_additions'])}",
        f"人工行数(human_additions): {format_number(summary['human_additions'])}",
        f"混合行数(mixed_additions): {format_number(summary['mixed_additions'])}",
        f"直接接受的 AI 行数(ai_accepted): {format_number(summary['ai_accepted'])}",
        f"AI 覆盖率: {format_pct(summary['ai_coverage_pct'])}",
        f"直接接受 AI 覆盖率: {format_pct(summary['accepted_ai_coverage_pct'])}",
        f"混合改写占比: {format_pct(summary['mixed_additions_pct'])}",
        f"AI 接受率(ai_accepted / ai_additions): {format_pct(summary['accepted_of_ai_pct'])}",
        f"AI 生成总行数(total_ai_additions): {format_number(summary['total_ai_additions'])}",
        f"AI 删除总行数(total_ai_deletions): {format_number(summary['total_ai_deletions'])}",
        f"等待 AI 总时长(秒): {format_number(summary['time_waiting_for_ai'])}",
    ]

    if errors:
        lines.append("")
        lines.append(f"警告: 有 {len(errors)} 个 commit 无法读取 git-ai 数据。")
        for commit, message in list(errors.items())[:5]:
            lines.append(f"  - {commit}: {message}")
        if len(errors) > 5:
            lines.append("  - ...")

    return "\n".join(lines)


def render_remote_report(
    *,
    remote_url: str,
    revision: str,
    time_range: str,
    contributors: list[dict[str, Any]],
    errors: dict[str, str],
) -> str:
    """Render a human-readable report for all contributors."""

    lines = [
        "Git AI 全量贡献者覆盖率统计",
        "=" * 32,
        f"远程仓库: {remote_url}",
        f"统计范围: {revision}",
        f"时间范围: {time_range}",
        "",
        "排序规则: 按提交入库总行数(committed_additions)降序",
        "",
        f"{'贡献者':40} {'提交数':>8} {'总行数':>10} {'AI行数':>10} {'AI覆盖率':>12} {'直接接受AI':>12}",
        "-" * 100,
    ]

    for item in contributors:
        label = item["contributor"]["label"]
        if len(label) > 40:
            label = label[:37] + "..."
        summary = item["summary"]
        lines.append(
            f"{label:40} "
            f"{summary['commits']:>8} "
            f"{format_number(summary['committed_additions']):>10} "
            f"{format_number(summary['ai_additions']):>10} "
            f"{format_pct(summary['ai_coverage_pct']):>12} "
            f"{format_pct(summary['accepted_ai_coverage_pct']):>12}"
        )

    if errors:
        lines.extend(
            [
                "",
                f"警告: 有 {len(errors)} 个 commit 无法读取 git-ai 数据。",
            ]
        )
        for commit, message in list(errors.items())[:10]:
            lines.append(f"  - {commit}: {message}")
        if len(errors) > 10:
            lines.append("  - ...")

    return "\n".join(lines)


def slugify_remote(remote_url: str) -> str:
    """Create a stable directory name for a remote url."""

    parsed = urlparse(remote_url)
    if parsed.scheme and parsed.netloc:
        base = f"{parsed.netloc}{parsed.path}"
    else:
        base = remote_url
    return "".join(char if char.isalnum() else "-" for char in base).strip("-") or "repo"


def prepare_remote_repository(
    remote_url: str,
    *,
    branch: str | None,
    clone_dir: str | None,
) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    """Clone or refresh a remote repository and return its local path."""

    if clone_dir:
        repo_path = Path(clone_dir).expanduser().resolve()
        temp_dir = None
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="git-ai-coverage-")
        repo_path = Path(temp_dir.name) / slugify_remote(remote_url)

    if repo_path.exists():
        if not (repo_path / ".git").exists():
            raise ScriptError(f"目标目录已存在但不是 Git 仓库: {repo_path}")
        current_origin = run_command(["git", "remote", "get-url", "origin"], cwd=repo_path).stdout.strip()
        if current_origin != remote_url:
            raise ScriptError(
                f"clone 目录对应的 origin 与传入 remote-url 不一致。\n"
                f"目录: {repo_path}\n当前 origin: {current_origin}\n目标 remote: {remote_url}"
            )
        run_command(["git", "fetch", "origin", "--prune"], cwd=repo_path)
    else:
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        run_command(
            ["git", "clone", "--filter=blob:none", "--quiet", remote_url, str(repo_path)],
            cwd=repo_path.parent,
        )

    if branch:
        run_command(["git", "checkout", branch], cwd=repo_path)
        run_command(["git", "pull", "origin", branch], cwd=repo_path)
    else:
        current_branch = run_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
        ).stdout.strip()
        if current_branch and current_branch != "HEAD":
            run_command(["git", "pull", "--ff-only", "origin", current_branch], cwd=repo_path)

    ensure_git_repository(repo_path)
    return repo_path, temp_dir


def build_contributor_commit_map(
    repo: Path,
    revision: str,
    *,
    no_merges: bool,
    since: str | None,
    until: str | None,
) -> dict[Contributor, list[str]]:
    """Return contributor -> commit list within the given revision."""

    pairs = parse_git_log(repo, revision, no_merges, since=since, until=until)
    mapping: dict[Contributor, list[str]] = {}
    for commit, contributor in pairs:
        mapping.setdefault(contributor, []).append(commit)
    return mapping


def serialize_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Convert internal summary to JSON-safe output."""

    safe: dict[str, Any] = {}
    for key, value in summary.items():
        if isinstance(value, dict):
            safe[key] = value
        elif isinstance(value, (int, float)):
            safe[key] = value
        else:
            safe[key] = value
    return safe


def write_json_output(path: str | None, payload: dict[str, Any]) -> None:
    """Write JSON to stdout or file."""

    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if path:
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content + "\n", encoding="utf-8")
        return
    print(content)


def emit_json(payload: dict[str, Any], path: str | None, *, also_stdout: bool) -> None:
    """Write JSON to file and optionally stdout."""

    if path:
        write_json_output(path, payload)
        if also_stdout:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    write_json_output(None, payload)


def handle_local(args: argparse.Namespace) -> int:
    """Handle the local subcommand."""

    repo = Path(args.repo).expanduser().resolve()
    ensure_git_repository(repo)
    time_range = format_time_filter_label(since=args.since, until=args.until)

    author_name = args.author_name or git_config_get(repo, "user.name")
    author_email = args.author_email or git_config_get(repo, "user.email")
    commit_map = build_contributor_commit_map(
        repo,
        args.revision,
        no_merges=args.no_merges,
        since=args.since,
        until=args.until,
    )
    target_contributor = select_local_contributor(
        list(commit_map.keys()),
        author_name=author_name,
        author_email=author_email,
    )

    commits = commit_map.get(target_contributor, [])
    if not commits:
        raise ScriptError(f"在范围 {args.revision} 内未找到 {target_contributor.label} 的提交。")

    stats_by_commit, errors = load_commit_stats(
        repo,
        commits,
        workers=args.workers,
        progress=not args.quiet and not args.json,
    )
    summary = aggregate_stats(list(stats_by_commit.values()))

    payload = {
        "mode": "local",
        "repo": str(repo),
        "revision": args.revision,
        "time_filter": {
            "since": args.since,
            "until": args.until,
            "label": time_range,
        },
        "contributor": {
            "name": target_contributor.name,
            "email": target_contributor.email,
            "label": target_contributor.label,
        },
        "summary": serialize_summary(summary),
        "commit_count_in_scope": len(commits),
        "successful_commit_count": len(stats_by_commit),
        "failed_commits": errors,
    }

    if args.json:
        emit_json(payload, args.json_output, also_stdout=True)
    else:
        report = render_local_report(
            repo=repo,
            revision=args.revision,
            time_range=time_range,
            contributor=target_contributor,
            summary=summary,
            errors=errors,
        )
        if args.json_output:
            write_json_output(args.json_output, payload)
            print(report)
        else:
            print(report)
    return 0


def handle_remote_all(args: argparse.Namespace) -> int:
    """Handle the remote-all subcommand."""

    repo, temp_dir = prepare_remote_repository(
        args.remote_url,
        branch=args.branch,
        clone_dir=args.clone_dir,
    )
    try:
        time_range = format_time_filter_label(since=args.since, until=args.until)
        commit_map = build_contributor_commit_map(
            repo,
            args.revision,
            no_merges=args.no_merges,
            since=args.since,
            until=args.until,
        )
        all_commits = [commit for commits in commit_map.values() for commit in commits]

        if not all_commits:
            raise ScriptError(f"在范围 {args.revision} 内未找到任何提交。")

        stats_by_commit, errors = load_commit_stats(
            repo,
            all_commits,
            workers=args.workers,
            progress=not args.quiet and not args.json,
        )

        contributors_payload: list[dict[str, Any]] = []
        for contributor, commits in commit_map.items():
            contributor_stats = [stats_by_commit[commit] for commit in commits if commit in stats_by_commit]
            summary = aggregate_stats(contributor_stats)
            contributors_payload.append(
                {
                    "contributor": {
                        "name": contributor.name,
                        "email": contributor.email,
                        "label": contributor.label,
                    },
                    "scope_commit_count": len(commits),
                    "successful_commit_count": len(contributor_stats),
                    "summary": serialize_summary(summary),
                }
            )

        contributors_payload.sort(
            key=lambda item: (
                -item["summary"]["committed_additions"],
                -item["summary"]["ai_coverage_pct"],
                item["contributor"]["label"].lower(),
            )
        )

        overall_summary = aggregate_stats(list(stats_by_commit.values()))
        payload = {
            "mode": "remote-all",
            "remote_url": args.remote_url,
            "local_repo": str(repo),
            "revision": args.revision,
            "time_filter": {
                "since": args.since,
                "until": args.until,
                "label": time_range,
            },
            "overall_summary": serialize_summary(overall_summary),
            "contributors": contributors_payload,
            "successful_commit_count": len(stats_by_commit),
            "failed_commits": errors,
        }

        if args.json:
            emit_json(payload, args.json_output, also_stdout=True)
        else:
            report = render_remote_report(
                remote_url=args.remote_url,
                revision=args.revision,
                time_range=time_range,
                contributors=contributors_payload,
                errors=errors,
            )
            if args.json_output:
                write_json_output(args.json_output, payload)
                print(report)
            else:
                print(report)
        return 0
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(
        description="使用 git-ai 统计本地个人或远程仓库所有贡献者的 AI 代码覆盖率。",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "示例:\n"
            "  python3 scripts/git_ai_coverage.py local\n"
            "  python3 scripts/git_ai_coverage.py local --since 2026-03-01 --until 2026-03-31\n"
            "  python3 scripts/git_ai_coverage.py local --author-email you@example.com --json\n"
            "  python3 scripts/git_ai_coverage.py remote-all --remote-url https://github.com/org/repo.git\n"
            "  python3 scripts/git_ai_coverage.py remote-all --remote-url https://github.com/org/repo.git --since 2026-03-01 --until 2026-03-31\n"
            "  python3 scripts/git_ai_coverage.py remote-all --remote-url git@github.com:org/repo.git --clone-dir .cache/repo --json-output result.json"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_options(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--revision",
            default="HEAD",
            help="统计范围，默认 HEAD；也支持 main、v1.0.0、abc123..def456 等 git revision 语法。",
        )
        subparser.add_argument(
            "--since",
            help="仅统计该时间之后（含）的提交，使用 Git 支持的时间格式，如 2026-03-01、'2026-03-01 00:00:00'、2.weeks.ago。",
        )
        subparser.add_argument(
            "--until",
            help="仅统计该时间之前（含）的提交，使用 Git 支持的时间格式，如 2026-03-31、'2026-03-31 23:59:59'、yesterday。",
        )
        subparser.add_argument(
            "--workers",
            type=int,
            default=max(1, min((os.cpu_count() or 4), 8)),
            help="并发读取 git-ai stats 的 worker 数，默认 1~8 之间自动选择。",
        )
        subparser.add_argument(
            "--no-merges",
            action="store_true",
            help="忽略 merge commit。",
        )
        subparser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出到 stdout（若同时指定 --json-output，则写入文件）。",
        )
        subparser.add_argument(
            "--json-output",
            help="将 JSON 结果写入指定文件。",
        )
        subparser.add_argument(
            "--quiet",
            action="store_true",
            help="关闭进度信息。",
        )

    local_parser = subparsers.add_parser("local", help="统计当前仓库中我个人的 AI 代码覆盖率。")
    add_common_options(local_parser)
    local_parser.add_argument(
        "--repo",
        default=".",
        help="本地仓库路径，默认当前目录。",
    )
    local_parser.add_argument(
        "--author-name",
        help="指定作者名；默认读取 git config user.name。",
    )
    local_parser.add_argument(
        "--author-email",
        help="指定作者邮箱；默认读取 git config user.email。",
    )
    local_parser.set_defaults(func=handle_local)

    remote_parser = subparsers.add_parser(
        "remote-all",
        help="克隆/更新远程仓库后，统计所有贡献者的 AI 代码覆盖率。",
    )
    add_common_options(remote_parser)
    remote_parser.add_argument(
        "--remote-url",
        required=True,
        help="远程仓库地址，如 https://github.com/org/repo.git 或 git@github.com:org/repo.git。",
    )
    remote_parser.add_argument(
        "--branch",
        help="可选，指定统计前 checkout/pull 的分支。",
    )
    remote_parser.add_argument(
        "--clone-dir",
        help="可选，复用本地克隆目录；未指定时使用临时目录。",
    )
    remote_parser.set_defaults(func=handle_remote_all)

    return parser


def main() -> int:
    """CLI entrypoint."""

    parser = build_parser()
    args = parser.parse_args()

    try:
        ensure_command_exists(
            "git",
            "请先安装 Git。",
        )
        ensure_command_exists(
            "git-ai",
            "请先安装 Git AI，例如：\n"
            "  curl -sSL https://usegitai.com/install.sh | bash\n"
            "安装完成后可用 `git-ai install-hooks` 配置编辑器/代理 hooks。",
        )
        return args.func(args)
    except ScriptError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
