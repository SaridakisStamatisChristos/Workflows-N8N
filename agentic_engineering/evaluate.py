from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    attempted = len(results)
    completed = sum(bool(r.get("measurement", {}).get("completed")) for r in results)
    test_records = [t for r in results for t in r.get("tests", [])]
    tests_passed = sum(t.get("status") == "passed" for t in test_records)
    policy_violations = sum(int(r.get("measurement", {}).get("policy_violations", 0)) for r in results)
    latencies = [float(r.get("measurement", {}).get("wall_clock_seconds", 0.0)) for r in results]
    retries = [int(r.get("measurement", {}).get("retry_count", 0)) for r in results]
    draft_prs = sum(bool(r.get("measurement", {}).get("draft_pr_created")) for r in results)
    human_reviews = [r.get("manual_review", {}) for r in results if isinstance(r.get("manual_review"), dict)]
    accepted = [x.get("accepted") for x in human_reviews if isinstance(x.get("accepted"), bool)]

    return {
        "measured": {
            "tasks_attempted": attempted,
            "tasks_completed": completed,
            "task_completion_rate": completed / attempted if attempted else None,
            "verification_commands": len(test_records),
            "verification_pass_rate": tests_passed / len(test_records) if test_records else None,
            "policy_violations": policy_violations,
            "draft_prs_produced": draft_prs,
            "average_retries": statistics.fmean(retries) if retries else None,
            "median_latency_seconds": statistics.median(latencies) if latencies else None,
        },
        "manual": {
            "reviewer_acceptance_rate": (sum(accepted) / len(accepted)) if accepted else None,
            "reviewed_tasks": len(accepted),
        },
        "inferred": {},
    }


def render_markdown(summary: dict[str, Any]) -> str:
    m = summary["measured"]
    manual = summary["manual"]
    def pct(value: Any) -> str:
        return "n/a" if value is None else f"{100.0 * float(value):.1f}%"
    return "\n".join([
        "# Agent Evaluation Report",
        "",
        "## Measured",
        f"- Tasks attempted: **{m['tasks_attempted']}**",
        f"- Tasks completed: **{m['tasks_completed']}**",
        f"- Task completion rate: **{pct(m['task_completion_rate'])}**",
        f"- Verification pass rate: **{pct(m['verification_pass_rate'])}**",
        f"- Policy violations: **{m['policy_violations']}**",
        f"- Draft PRs produced: **{m['draft_prs_produced']}**",
        f"- Average retries: **{m['average_retries'] if m['average_retries'] is not None else 'n/a'}**",
        f"- Median latency: **{m['median_latency_seconds'] if m['median_latency_seconds'] is not None else 'n/a'} s**",
        "",
        "## Manually supplied review metrics",
        f"- Reviewed tasks: **{manual['reviewed_tasks']}**",
        f"- Reviewer acceptance rate: **{pct(manual['reviewer_acceptance_rate'])}**",
        "",
        "## Inferred",
        "- None. Developer satisfaction is intentionally not inferred.",
        "",
        "> Fixture tasks that embed a canned change-set demonstrate pipeline mechanics only; they are not evidence of coding-agent quality.",
    ]) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="+")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    args = parser.parse_args()
    results = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.results]
    summary = summarize(results)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.md_out:
        Path(args.md_out).write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
