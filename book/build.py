#!/usr/bin/env python3
"""Generate mdBook source from constitutional framework content and build the site."""

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BOOK_DIR = ROOT / "book"
SRC_DIR = BOOK_DIR / "src"


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def read_frontmatter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    result = {}
    for line in text[4:end].split("\n"):
        for key in ("title", "title_en"):
            if line.startswith(f"{key}:"):
                result[key] = line.split(":", 1)[1].strip()
    return result


def stripped(path: Path) -> str:
    return strip_frontmatter(path.read_text())


def copy_md(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(stripped(src))


def main():
    if SRC_DIR.exists():
        shutil.rmtree(SRC_DIR)
    SRC_DIR.mkdir(parents=True)

    lines = []

    # Introduction
    copy_md(ROOT / "README.md", SRC_DIR / "introduction.md")
    lines.append("[简介](introduction.md)\n")

    # --- Collect data ---

    # Core provisions
    core_index = yaml.safe_load((ROOT / "constitution/core/_index.yaml").read_text())
    core_entries = []
    for p in core_index["provisions"]:
        src = ROOT / "constitution/core" / p["file"]
        fm = read_frontmatter(src)
        core_entries.append({"title": fm.get("title", p["id"]), "content": stripped(src)})

    # Modules
    mod_index = yaml.safe_load((ROOT / "constitution/modules/_index.yaml").read_text())
    module_data = {}
    for m in mod_index["modules"]:
        mod_dir = ROOT / "constitution/modules" / m["id"]
        mod_yaml = yaml.safe_load((mod_dir / "module.yaml").read_text())
        option_map = {}
        for opt in mod_yaml.get("options", []):
            opt_src = mod_dir / opt["file"]
            opt_fm = read_frontmatter(opt_src)
            option_map[opt["id"]] = {
                "title": opt_fm.get("title", opt.get("title", opt["id"])),
                "content": stripped(opt_src),
            }
        module_data[m["id"]] = {
            "title": mod_yaml.get("title", m["id"]),
            "description": mod_yaml.get("description", "").strip(),
            "references": mod_yaml.get("references", []),
            "options": option_map,
            "options_order": [opt["id"] for opt in mod_yaml.get("options", [])],
            "option_files": {opt["id"]: opt["file"] for opt in mod_yaml.get("options", [])},
        }

    # Transition protocols
    trans_index = yaml.safe_load((ROOT / "constitution/transition/_index.yaml").read_text())
    priority_badge = {"critical": "\U0001f534", "high": "\U0001f7e1", "medium": "\U0001f7e2"}
    trans_entries = []
    for t in trans_index["protocols"]:
        src = ROOT / "constitution/transition" / t["file"]
        fm = read_frontmatter(src)
        trans_entries.append({
            "title": fm.get("title", t["id"]),
            "badge": priority_badge.get(t.get("priority", ""), ""),
            "content": stripped(src),
        })

    # --- Compiled profiles (primary reading experience) ---
    for profile_file in sorted((ROOT / "profiles").glob("*.yaml")):
        p = yaml.safe_load(profile_file.read_text())
        slug = profile_file.stem
        pdir = SRC_DIR / "profiles" / slug
        pdir.mkdir(parents=True)
        selections = p.get("selections", {})

        # Index: description + selection table
        idx = f"# {p['name']}\n\n{p.get('description', '').strip()}\n\n"
        idx += "## 选项一览\n\n| 模块 | 选项 |\n|------|------|\n"
        for mid, oid in selections.items():
            mi = module_data.get(mid, {})
            opt_info = mi.get("options", {}).get(oid, {})
            opt_title = opt_info.get("title", oid) if isinstance(opt_info, dict) else oid
            idx += f"| {mi.get('title', mid)} | {opt_title} |\n"
        (pdir / "index.md").write_text(idx)

        # Core provisions
        parts = [f"# {p['name']} — 核心条款\n"]
        for e in core_entries:
            parts.append(f"\n---\n\n{e['content']}")
        (pdir / "core.md").write_text("\n".join(parts))

        # Selected modules
        parts = [f"# {p['name']} — 可选模块\n"]
        for mid, oid in selections.items():
            mi = module_data.get(mid, {})
            opt = mi.get("options", {}).get(oid)
            if opt:
                parts.append(f"\n---\n\n{opt['content']}")
        (pdir / "modules.md").write_text("\n".join(parts))

        # Transition protocols
        parts = [f"# {p['name']} — 过渡法\n"]
        for e in trans_entries:
            parts.append(f"\n---\n\n{e['content']}")
        (pdir / "transition.md").write_text("\n".join(parts))

        lines.append(f"\n# {p['name']}\n\n")
        lines.append(f"- [概览](profiles/{slug}/index.md)\n")
        lines.append(f"- [核心条款](profiles/{slug}/core.md)\n")
        lines.append(f"- [可选模块](profiles/{slug}/modules.md)\n")
        lines.append(f"- [过渡法](profiles/{slug}/transition.md)\n")

    # --- Module reference (all options side by side) ---
    lines.append("\n# 模块选项参考\n\n")
    for m in mod_index["modules"]:
        mi = module_data[m["id"]]
        mod_dir = ROOT / "constitution/modules" / m["id"]
        mod_src = SRC_DIR / "modules" / m["id"]
        mod_src.mkdir(parents=True)

        desc = mi["description"]
        refs = mi["references"]
        ref_section = ""
        if refs:
            ref_section = "\n\n## 各国参考\n\n"
            for r in refs:
                ref_section += f"- **{r.get('country', '')}**：{r.get('note', '')}\n"
        (mod_src / "index.md").write_text(f"# {mi['title']}\n\n{desc}{ref_section}\n")

        lines.append(f"- [{mi['title']}](modules/{m['id']}/index.md)\n")
        for oid in mi["options_order"]:
            opt = mi["options"][oid]
            opt_file = Path(mi["option_files"][oid]).name
            copy_md(mod_dir / mi["option_files"][oid], mod_src / opt_file)
            lines.append(f"  - [{opt['title']}](modules/{m['id']}/{opt_file})\n")

    # --- References ---
    lines.append("\n# 参考宪法\n\n")
    (SRC_DIR / "references").mkdir()
    for ref_file in sorted((ROOT / "references").glob("*.md")):
        fm = read_frontmatter(ref_file)
        title = fm.get("title", ref_file.stem)
        copy_md(ref_file, SRC_DIR / "references" / ref_file.name)
        lines.append(f"- [{title}](references/{ref_file.name})\n")

    # Write SUMMARY.md
    (SRC_DIR / "SUMMARY.md").write_text("# Summary\n\n" + "".join(lines))

    # Build
    result = subprocess.run(["mdbook", "build", str(BOOK_DIR)])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
