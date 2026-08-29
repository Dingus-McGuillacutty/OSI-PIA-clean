#!/usr/bin/env python3
"""Validate the repository's reproducible governance invariants.

artifact_id: software-governance-validator-001
domain: implementation
layer: software
authority: canonical
status: active
version: 1.0.0
owner: repository-governance
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


COMMON_HEADER = (
    "Artifact ID",
    "Name",
    "Domain",
    "Layer",
    "Authority",
    "Status",
    "Owner",
    "Version",
    "Canonical Location",
    "Depends On",
)

ALLOWED_DOMAINS = {"shared", "osi", "pia", "implementation", "test"}
ALLOWED_AUTHORITIES = {"canonical", "supporting", "working", "historical"}
ALLOWED_STATUSES = {
    "active",
    "proposed",
    "review-required",
    "deprecated",
    "superseded",
    "retired",
}
ALLOWED_REVIEW_CYCLES = {
    "annual",
    "semiannual",
    "quarterly",
    "milestone",
    "event-driven",
}
ALLOWED_LIFECYCLE_STATES = {
    "observation",
    "exploration",
    "formulation",
    "congruence",
    "validation",
    "promotion",
    "stewardship",
}

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
NAMESPACED_ID_RE = re.compile(r"^(shared|osi|pia|implementation):[a-z0-9][a-z0-9_]*$")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CANONICAL_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class RegistryRow:
    source: Path
    values: dict[str, str]

    @property
    def artifact_id(self) -> str:
        return clean_cell(self.values["Artifact ID"])


def clean_cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip()


def split_table_row(line: str) -> tuple[str, ...]:
    return tuple(cell.strip() for cell in line.strip().strip("|").split("|"))


def is_separator_row(cells: tuple[str, ...]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_registry_rows(path: Path) -> list[RegistryRow]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[RegistryRow] = []
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        cells = split_table_row(line)
        if cells != COMMON_HEADER:
            continue
        for row_line in lines[index + 1 :]:
            if not row_line.lstrip().startswith("|"):
                break
            row_cells = split_table_row(row_line)
            if is_separator_row(row_cells):
                continue
            if len(row_cells) != len(COMMON_HEADER):
                continue
            rows.append(RegistryRow(path, dict(zip(COMMON_HEADER, row_cells))))
        break
    return rows


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return result
        match = re.match(r"^([a-z_]+):\s*(.*?)\s*$", line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip("\"'")
    return {}


def strip_fenced_code(text: str) -> str:
    kept: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


def resolve_markdown_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split(maxsplit=1)[0]
    if (
        not target
        or target.startswith("#")
        or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE)
    ):
        return None
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target:
        return None
    return (source.parent / target).resolve()


def dependency_ids(cell: str) -> list[str]:
    if clean_cell(cell) in {"—", "â€”", "-"}:
        return []
    return re.findall(r"`([a-z0-9][a-z0-9-]*)`", cell)


class GovernanceValidator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.errors: list[str] = []
        self.counts = {
            "registry_rows": 0,
            "metadata_artifacts": 0,
            "markdown_links": 0,
            "ontology_ids": 0,
            "tracked_paths": 0,
            "privacy_signatures": 0,
        }

    def relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def markdown_files(self) -> list[Path]:
        generated_directories = {
            ".agents",
            ".git",
            ".next",
            ".wrangler",
            "dist",
            "node_modules",
            "sources",
        }
        return sorted(
            path
            for path in self.root.rglob("*.md")
            if not any(part in generated_directories for part in path.parts)
        )

    def validate_metadata(
        self, markdown_files: list[Path]
    ) -> dict[str, tuple[Path, dict[str, str]]]:
        artifacts: dict[str, tuple[Path, dict[str, str]]] = {}
        required = {
            "artifact_id",
            "domain",
            "layer",
            "authority",
            "status",
            "version",
            "owner",
        }
        for path in markdown_files:
            metadata = parse_frontmatter(path)
            if not metadata:
                continue
            self.counts["metadata_artifacts"] += 1
            missing = sorted(required - metadata.keys())
            if missing:
                self.error(
                    f"{self.relative(path)}: missing metadata fields {', '.join(missing)}"
                )
                continue
            artifact_id = metadata["artifact_id"]
            if not ID_RE.fullmatch(artifact_id):
                self.error(f"{self.relative(path)}: invalid artifact_id {artifact_id!r}")
            if artifact_id in artifacts:
                prior = self.relative(artifacts[artifact_id][0])
                self.error(
                    f"{self.relative(path)}: duplicate artifact_id {artifact_id!r}; "
                    f"already declared by {prior}"
                )
            else:
                artifacts[artifact_id] = (path, metadata)
            if metadata["domain"] not in ALLOWED_DOMAINS:
                self.error(
                    f"{self.relative(path)}: invalid domain {metadata['domain']!r}"
                )
            if metadata["authority"] not in ALLOWED_AUTHORITIES:
                self.error(
                    f"{self.relative(path)}: invalid authority "
                    f"{metadata['authority']!r}"
                )
            if metadata["status"] not in ALLOWED_STATUSES:
                self.error(
                    f"{self.relative(path)}: invalid status {metadata['status']!r}"
                )
            lifecycle = metadata.get("lifecycle_state")
            if lifecycle and lifecycle not in ALLOWED_LIFECYCLE_STATES:
                self.error(
                    f"{self.relative(path)}: invalid lifecycle_state {lifecycle!r}"
                )
            cycle = metadata.get("review_cycle")
            last_reviewed = metadata.get("last_reviewed")
            if cycle:
                if cycle not in ALLOWED_REVIEW_CYCLES:
                    self.error(
                        f"{self.relative(path)}: invalid review_cycle {cycle!r}"
                    )
                if not last_reviewed:
                    self.error(
                        f"{self.relative(path)}: review_cycle requires last_reviewed"
                    )
            if last_reviewed:
                try:
                    dt.date.fromisoformat(last_reviewed)
                except ValueError:
                    self.error(
                        f"{self.relative(path)}: invalid last_reviewed "
                        f"{last_reviewed!r}"
                    )
        return artifacts

    def validate_registries(
        self, artifacts: dict[str, tuple[Path, dict[str, str]]]
    ) -> dict[str, RegistryRow]:
        registry_dir = self.root / "governance" / "registries"
        sources = sorted(registry_dir.glob("*_REGISTRY.md"))
        sources.append(registry_dir / "README.md")
        rows: dict[str, RegistryRow] = {}
        for source in sources:
            parsed = parse_registry_rows(source)
            if not parsed:
                self.error(f"{self.relative(source)}: no common registry table found")
            for row in parsed:
                self.counts["registry_rows"] += 1
                artifact_id = row.artifact_id
                if not ID_RE.fullmatch(artifact_id):
                    self.error(
                        f"{self.relative(source)}: invalid registry artifact ID "
                        f"{artifact_id!r}"
                    )
                if artifact_id in rows:
                    self.error(
                        f"{self.relative(source)}: duplicate primary registry ID "
                        f"{artifact_id!r}; first seen in "
                        f"{self.relative(rows[artifact_id].source)}"
                    )
                    continue
                rows[artifact_id] = row

                domain = clean_cell(row.values["Domain"])
                authority = clean_cell(row.values["Authority"])
                status = clean_cell(row.values["Status"])
                if domain not in ALLOWED_DOMAINS:
                    self.error(
                        f"{self.relative(source)}: {artifact_id} has invalid domain "
                        f"{domain!r}"
                    )
                if authority not in ALLOWED_AUTHORITIES:
                    self.error(
                        f"{self.relative(source)}: {artifact_id} has invalid authority "
                        f"{authority!r}"
                    )
                if status not in ALLOWED_STATUSES:
                    self.error(
                        f"{self.relative(source)}: {artifact_id} has invalid status "
                        f"{status!r}"
                    )

                link_match = CANONICAL_LINK_RE.fullmatch(
                    row.values["Canonical Location"].strip()
                )
                if not link_match:
                    self.error(
                        f"{self.relative(source)}: {artifact_id} lacks one relative "
                        f"canonical Markdown link"
                    )
                    continue
                target = resolve_markdown_target(source, link_match.group(1))
                if target is None or not target.exists():
                    rendered = link_match.group(1)
                    self.error(
                        f"{self.relative(source)}: {artifact_id} canonical location "
                        f"does not resolve: {rendered}"
                    )
                    continue
                if target.is_file() and target.suffix.lower() == ".md":
                    metadata = parse_frontmatter(target)
                    if metadata:
                        comparisons = {
                            "artifact_id": artifact_id,
                            "domain": domain,
                            "layer": clean_cell(row.values["Layer"]),
                            "authority": authority,
                            "status": status,
                            "owner": clean_cell(row.values["Owner"]),
                            "version": clean_cell(row.values["Version"]),
                        }
                        for key, expected in comparisons.items():
                            actual = metadata.get(key)
                            if actual != expected:
                                self.error(
                                    f"{self.relative(source)}: {artifact_id} {key} "
                                    f"{expected!r} disagrees with "
                                    f"{self.relative(target)} value {actual!r}"
                                )

        known_ids = set(rows)
        for artifact_id, row in rows.items():
            for dependency in dependency_ids(row.values["Depends On"]):
                if dependency not in known_ids:
                    self.error(
                        f"{self.relative(row.source)}: {artifact_id} depends on "
                        f"unregistered ID {dependency!r}"
                    )

        for artifact_id, (path, _) in artifacts.items():
            if artifact_id not in known_ids:
                self.error(
                    f"{self.relative(path)}: metadata artifact {artifact_id!r} "
                    f"is not in a primary registry"
                )

        self.validate_dependency_cycles(rows)
        return rows

    def validate_dependency_cycles(self, rows: dict[str, RegistryRow]) -> None:
        graph = {
            artifact_id: dependency_ids(row.values["Depends On"])
            for artifact_id, row in rows.items()
        }
        visited: set[str] = set()
        active: list[str] = []
        active_set: set[str] = set()
        reported: set[tuple[str, ...]] = set()

        def visit(node: str) -> None:
            if node in active_set:
                start = active.index(node)
                cycle = tuple(active[start:] + [node])
                if cycle not in reported:
                    reported.add(cycle)
                    self.error(f"registry dependency cycle: {' -> '.join(cycle)}")
                return
            if node in visited:
                return
            active.append(node)
            active_set.add(node)
            for dependency in graph.get(node, []):
                if dependency in graph:
                    visit(dependency)
            active.pop()
            active_set.remove(node)
            visited.add(node)

        for artifact_id in graph:
            visit(artifact_id)

    def validate_markdown_links(self, markdown_files: list[Path]) -> None:
        for path in markdown_files:
            text = strip_fenced_code(path.read_text(encoding="utf-8"))
            for match in MARKDOWN_LINK_RE.finditer(text):
                target = resolve_markdown_target(path, match.group(1))
                if target is None:
                    continue
                self.counts["markdown_links"] += 1
                # GitHub Pages/Jekyll emits HTML routes from Markdown sources;
                # accept the route when its source file is present locally.
                generated_route = (
                    target.suffix.lower() == ".html"
                    and target.with_suffix(".md").exists()
                )
                if not target.exists() and not generated_route:
                    self.error(
                        f"{self.relative(path)}: unresolved Markdown link "
                        f"{match.group(1)!r}"
                    )

    def validate_ontology_ids(self) -> None:
        path = self.root / "governance" / "registries" / "ONTOLOGY_REGISTRY.md"
        text = path.read_text(encoding="utf-8")
        seen: set[str] = set()
        for match in re.finditer(r"^\|\s*`([^`]+:[^`]+)`\s*\|", text, re.MULTILINE):
            ontology_id = match.group(1)
            self.counts["ontology_ids"] += 1
            if not NAMESPACED_ID_RE.fullmatch(ontology_id):
                self.error(
                    f"{self.relative(path)}: invalid namespaced ontology ID "
                    f"{ontology_id!r}"
                )
            if ontology_id in seen:
                self.error(
                    f"{self.relative(path)}: duplicate namespaced ontology ID "
                    f"{ontology_id!r}"
                )
            seen.add(ontology_id)

    def validate_review_required(self, rows: dict[str, RegistryRow]) -> None:
        migration_path = self.root / "governance" / "Repository_Migration_Plan.md"
        migration_text = migration_path.read_text(encoding="utf-8")
        for artifact_id, row in rows.items():
            if clean_cell(row.values["Status"]) != "review-required":
                continue
            if artifact_id not in migration_text:
                self.error(
                    f"{self.relative(row.source)}: review-required {artifact_id} "
                    f"is absent from {self.relative(migration_path)}"
                )

    def validate_participant_data_boundary(self) -> None:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=self.root,
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            self.error("git ls-files failed while checking participant-data boundary")
            return
        tracked = [
            item.decode("utf-8", errors="replace").replace("\\", "/")
            for item in result.stdout.split(b"\0")
            if item
        ]
        self.counts["tracked_paths"] = len(tracked)
        forbidden = [
            path
            for path in tracked
            if path.startswith("data/PIA-participants/")
            or re.match(r"^graph/imports/PIA/PIA-\d+/", path, re.IGNORECASE)
            or re.search(
                r"^docs/publications/.*/PIA-\d+[^/]*\.(md|pdf)$",
                path,
                re.IGNORECASE,
            )
            or re.match(r"^analysis/PIA/pia_.*\.csv$", path, re.IGNORECASE)
        ]
        for path in forbidden:
            self.error(f"participant-specific data remains tracked: {path}")

        text_suffixes = {
            ".csv",
            ".cypher",
            ".json",
            ".md",
            ".py",
            ".txt",
            ".yaml",
            ".yml",
        }
        restricted_signatures = (
            re.compile(r"(?<!ADR-)\bPIA-(?!9\d{3}\b)\d{3,}\b"),
            re.compile(r"\bParticipant 00[12]\b", re.IGNORECASE),
        )
        for relative_path in tracked:
            path = self.root / relative_path
            if path.suffix.lower() not in text_suffixes or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for signature in restricted_signatures:
                if signature.search(text):
                    self.counts["privacy_signatures"] += 1
                    self.error(
                        f"{relative_path}: restricted development participant "
                        f"identifier remains in tracked content"
                    )
                    break

        ignore_path = self.root / ".gitignore"
        ignore_lines = {
            line.strip()
            for line in ignore_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        if "/data/PIA-participants/" not in ignore_lines:
            self.error(".gitignore must exclude /data/PIA-participants/")

    def run(self) -> list[str]:
        markdown_files = self.markdown_files()
        artifacts = self.validate_metadata(markdown_files)
        rows = self.validate_registries(artifacts)
        self.validate_markdown_links(markdown_files)
        self.validate_ontology_ids()
        self.validate_review_required(rows)
        self.validate_participant_data_boundary()
        return sorted(set(self.errors))


def validate_repository(root: Path) -> tuple[list[str], dict[str, int]]:
    validator = GovernanceValidator(root)
    return validator.run(), validator.counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate OSI-PIA repository governance invariants."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root (defaults to the root containing software/).",
    )
    args = parser.parse_args()

    errors, counts = validate_repository(args.root)
    if errors:
        print(f"Governance validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Governance validation passed: "
        f"{counts['registry_rows']} registry rows, "
        f"{counts['metadata_artifacts']} metadata artifacts, "
        f"{counts['markdown_links']} repository links, "
        f"{counts['ontology_ids']} ontology IDs, and "
        f"{counts['tracked_paths']} tracked paths checked; "
        f"{counts['privacy_signatures']} restricted participant signatures."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
