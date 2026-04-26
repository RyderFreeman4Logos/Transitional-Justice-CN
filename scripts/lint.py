#!/usr/bin/env python3
"""Validate constitutional framework content against schemas."""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []
WARNINGS: list[str] = []


def error(msg: str):
    ERRORS.append(msg)


def warn(msg: str):
    WARNINGS.append(msg)


def read_frontmatter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---"):
        error(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        error(f"{path.relative_to(ROOT)}: unclosed YAML frontmatter")
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError as e:
        error(f"{path.relative_to(ROOT)}: invalid YAML frontmatter: {e}")
        return {}


def check_required(fm: dict, required: list[str], path: Path):
    rel = path.relative_to(ROOT)
    for key in required:
        if key not in fm:
            error(f"{rel}: missing required field '{key}'")


def check_enum(fm: dict, field: str, allowed: list[str], path: Path):
    val = fm.get(field)
    if val and val not in allowed:
        error(f"{path.relative_to(ROOT)}: '{field}' is '{val}', must be one of {allowed}")


def lint_core():
    core_dir = ROOT / "constitution/core"
    index = yaml.safe_load((core_dir / "_index.yaml").read_text())
    provision_ids = set()

    categories = ["fundamental-rights", "political-rights", "governance-structure", "judicial", "rule-of-law"]

    indexed_files = set()
    for p in index["provisions"]:
        indexed_files.add(p["file"])
        fpath = core_dir / p["file"]
        if not fpath.exists():
            error(f"core/_index.yaml references '{p['file']}' but file does not exist")
            continue

        fm = read_frontmatter(fpath)
        if not fm:
            continue
        provision_ids.add(fm.get("id", ""))
        check_required(fm, ["id", "title", "title_en", "tier", "category"], fpath)
        check_enum(fm, "tier", ["core"], fpath)
        check_enum(fm, "category", categories, fpath)

        if fm.get("id") and fm["id"] != p["id"]:
            error(f"{fpath.relative_to(ROOT)}: id '{fm['id']}' does not match index id '{p['id']}'")

    for md in core_dir.glob("*.md"):
        if md.name not in indexed_files:
            warn(f"core/{md.name} exists but is not listed in _index.yaml")

    return provision_ids


def lint_modules():
    mod_dir = ROOT / "constitution/modules"
    index = yaml.safe_load((mod_dir / "_index.yaml").read_text())
    module_ids = set()
    module_options: dict[str, set[str]] = {}

    categories = ["civil-rights", "criminal-justice", "economic", "social", "governance", "environmental"]
    statuses = ["stub", "draft", "review", "ready"]

    indexed_ids = set()
    for m in index["modules"]:
        mid = m["id"]
        indexed_ids.add(mid)
        module_ids.add(mid)
        mdir = mod_dir / mid
        myaml = mdir / "module.yaml"

        if not myaml.exists():
            error(f"modules/_index.yaml references '{mid}' but {mid}/module.yaml does not exist")
            continue

        data = yaml.safe_load(myaml.read_text())
        check_required(data, ["id", "title", "title_en", "category", "status", "options"], myaml)
        check_enum(data, "category", categories, myaml)
        check_enum(data, "status", statuses, myaml)

        if data.get("id") and data["id"] != mid:
            error(f"{myaml.relative_to(ROOT)}: id '{data['id']}' does not match directory name '{mid}'")

        options = data.get("options", [])
        if len(options) < 2:
            error(f"{myaml.relative_to(ROOT)}: must have >= 2 options, has {len(options)}")

        opt_ids = set()
        for opt in options:
            for key in ["id", "title", "summary", "file"]:
                if key not in opt:
                    error(f"{myaml.relative_to(ROOT)}: option missing '{key}'")
            opt_ids.add(opt.get("id", ""))
            opt_file = mdir / opt.get("file", "")
            if opt.get("file") and not opt_file.exists():
                error(f"{myaml.relative_to(ROOT)}: option file '{opt['file']}' does not exist")
        module_options[mid] = opt_ids

    for d in mod_dir.iterdir():
        if d.is_dir() and d.name not in indexed_ids:
            warn(f"modules/{d.name}/ exists but is not listed in _index.yaml")

    return module_ids, module_options


def lint_transition():
    trans_dir = ROOT / "constitution/transition"
    index = yaml.safe_load((trans_dir / "_index.yaml").read_text())

    categories = ["governance", "security", "economic", "justice", "civil-service", "international"]
    priorities = ["critical", "high", "medium"]

    indexed_files = set()
    for t in index["protocols"]:
        indexed_files.add(t["file"])
        fpath = trans_dir / t["file"]
        if not fpath.exists():
            error(f"transition/_index.yaml references '{t['file']}' but file does not exist")
            continue

        fm = read_frontmatter(fpath)
        if not fm:
            continue
        check_required(fm, ["id", "title", "title_en", "category", "priority"], fpath)
        check_enum(fm, "category", categories, fpath)
        check_enum(fm, "priority", priorities, fpath)

    for md in trans_dir.glob("*.md"):
        if md.name not in indexed_files:
            warn(f"transition/{md.name} exists but is not listed in _index.yaml")


def lint_profiles(module_ids: set[str], module_options: dict[str, set[str]]):
    for pf in sorted((ROOT / "profiles").glob("*.yaml")):
        data = yaml.safe_load(pf.read_text())
        rel = pf.relative_to(ROOT)
        check_required(data, ["name", "name_en", "description", "selections"], pf)

        selections = data.get("selections", {})
        for mid, oid in selections.items():
            if mid not in module_ids:
                error(f"{rel}: selection references unknown module '{mid}'")
            elif oid not in module_options.get(mid, set()):
                error(f"{rel}: module '{mid}' has no option '{oid}'")

        for mid in module_ids:
            if mid not in selections:
                warn(f"{rel}: no selection for module '{mid}'")


def lint_cross_references(provision_ids: set[str], module_ids: set[str]):
    core_dir = ROOT / "constitution/core"
    for md in core_dir.glob("*.md"):
        fm = read_frontmatter(md)
        for ref_id in fm.get("related_provisions", []):
            if ref_id not in provision_ids:
                error(f"{md.relative_to(ROOT)}: related_provision '{ref_id}' does not exist")

    mod_dir = ROOT / "constitution/modules"
    for mdir in mod_dir.iterdir():
        if not mdir.is_dir():
            continue
        myaml = mdir / "module.yaml"
        if not myaml.exists():
            continue
        data = yaml.safe_load(myaml.read_text())
        for dep in data.get("dependencies", []):
            if dep not in module_ids:
                error(f"{myaml.relative_to(ROOT)}: dependency '{dep}' does not exist")


def main():
    provision_ids = lint_core()
    module_ids, module_options = lint_modules()
    lint_transition()
    lint_profiles(module_ids, module_options)
    lint_cross_references(provision_ids, module_ids)

    for w in WARNINGS:
        print(f"WARN: {w}")
    for e in ERRORS:
        print(f"ERROR: {e}")

    if ERRORS:
        print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        sys.exit(1)
    elif WARNINGS:
        print(f"\n0 errors, {len(WARNINGS)} warning(s)")
    else:
        print("All checks passed.")


if __name__ == "__main__":
    main()
