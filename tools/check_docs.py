#!/usr/bin/env python3
"""Offline consistency checks for DroidLayer's planning documents."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
ERRORS: list[str] = []


def prose(text: str) -> str:
    """Remove fenced examples so hypothetical commands are not document links."""
    return re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", text, flags=re.M | re.S)


def anchors(text: str) -> set[str]:
    found = set(re.findall(r'<a\s+id="([^"]+)"', text))
    seen: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+)$", prose(text), re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        found.add(f"{slug}-{count}" if count else slug)
    return found


texts = {path: path.read_text(encoding="utf-8") for path in FILES}
for path, text in texts.items():
    if len(re.findall(r"^```", text, re.M)) % 2:
        ERRORS.append(f"{path.relative_to(ROOT)}: unbalanced code fences")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", prose(text)):
        parts = urlsplit(target.strip("<>"))
        if parts.scheme or parts.netloc:
            continue
        resolved = (path.parent / unquote(parts.path)).resolve() if parts.path else path
        if not resolved.is_relative_to(ROOT):
            ERRORS.append(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
        elif not resolved.exists():
            ERRORS.append(f"{path.relative_to(ROOT)}: missing link target: {target}")
        elif parts.fragment and resolved.suffix == ".md":
            if unquote(parts.fragment) not in anchors(resolved.read_text(encoding="utf-8")):
                ERRORS.append(f"{path.relative_to(ROOT)}: missing fragment: {target}")

plan = texts[ROOT / "docs/IMPLEMENTATION_PLAN.md"]
tasks = re.findall(r"^- \[([ x])\] (M\d+\.\d+) —", plan, re.M)
task_ids = {task for _, task in tasks}
if len(tasks) != len(task_ids):
    ERRORS.append("IMPLEMENTATION_PLAN.md: duplicate task IDs")
for state, task in tasks:
    # Planning snapshot guard: update deliberately with evidence when coding begins.
    if state == "x" and task not in {"M0.1", "M0.2"}:
        ERRORS.append(f"{task}: runtime work checked in a planning-only snapshot")

for path, text in texts.items():
    for task in re.findall(r"\bM\d+\.\d+\b", prose(text)):
        if task not in task_ids:
            ERRORS.append(f"{path.relative_to(ROOT)}: unknown task {task}")
    for spike in re.findall(r"\bSPIKE-\d{3}\b", prose(text)):
        if f"## {spike}" not in texts[ROOT / "docs/SPIKES.md"]:
            ERRORS.append(f"{path.relative_to(ROOT)}: unknown spike {spike}")
    for adr in re.findall(r"\bADR-(\d{4})\b", prose(text)):
        if not any((ROOT / "docs/adr").glob(f"{adr}-*.md")):
            ERRORS.append(f"{path.relative_to(ROOT)}: unknown ADR-{adr}")

milestones = re.findall(r"^## M(\d+) —[^\n]*\n(.*?)(?=^## |\Z)", plan, re.M | re.S)
for number, body in milestones:
    for field in ("Objective", "Dependencies", "Deliverable", "Acceptance criteria",
                  "Test strategy", "Known risks"):
        if f"**{field}:**" not in body:
            ERRORS.append(f"M{number}: missing {field}")
if {int(number) for number, _ in milestones} != set(range(18)):
    ERRORS.append("Expected milestone definitions M0 through M17")

if ERRORS:
    print("\n".join(sorted(set(ERRORS))), file=sys.stderr)
    sys.exit(1)
print(f"Validated {len(FILES)} Markdown files, {len(tasks)} tasks, "
      f"{len(milestones)} milestones, local links and planning references.")
