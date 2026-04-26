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


def copy_md(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(strip_frontmatter(src.read_text()))


def main():
    if SRC_DIR.exists():
        shutil.rmtree(SRC_DIR)
    SRC_DIR.mkdir(parents=True)

    lines = []

    # Introduction
    copy_md(ROOT / "README.md", SRC_DIR / "introduction.md")
    lines.append("[简介](introduction.md)\n")

    # Core provisions
    lines.append("\n# 第一编 核心条款\n\n")
    core_index = yaml.safe_load((ROOT / "constitution/core/_index.yaml").read_text())
    (SRC_DIR / "core").mkdir()
    for p in core_index["provisions"]:
        src = ROOT / "constitution/core" / p["file"]
        fm = read_frontmatter(src)
        title = fm.get("title", p["id"])
        copy_md(src, SRC_DIR / "core" / p["file"])
        lines.append(f"- [{title}](core/{p['file']})\n")

    # Modules
    lines.append("\n# 第二编 可选模块\n\n")
    mod_index = yaml.safe_load((ROOT / "constitution/modules/_index.yaml").read_text())

    module_data = {}
    for m in mod_index["modules"]:
        mod_dir = ROOT / "constitution/modules" / m["id"]
        mod_yaml = yaml.safe_load((mod_dir / "module.yaml").read_text())
        module_data[m["id"]] = {
            "title": mod_yaml.get("title", m["id"]),
            "options": {opt["id"]: opt.get("title", opt["id"]) for opt in mod_yaml.get("options", [])},
        }

        mod_src = SRC_DIR / "modules" / m["id"]
        mod_src.mkdir(parents=True)

        desc = mod_yaml.get("description", "").strip()
        refs = mod_yaml.get("references", [])
        ref_section = ""
        if refs:
            ref_section = "\n\n## 各国参考\n\n"
            for r in refs:
                ref_section += f"- **{r.get('country', '')}**：{r.get('note', '')}\n"

        (mod_src / "index.md").write_text(f"# {mod_yaml['title']}\n\n{desc}{ref_section}\n")

        lines.append(f"- [{m['title']}](modules/{m['id']}/index.md)\n")
        for opt in mod_yaml.get("options", []):
            opt_src = mod_dir / opt["file"]
            opt_name = Path(opt["file"]).name
            copy_md(opt_src, mod_src / opt_name)
            opt_fm = read_frontmatter(opt_src)
            opt_title = opt_fm.get("title", opt.get("title", opt["id"]))
            lines.append(f"  - [{opt_title}](modules/{m['id']}/{opt_name})\n")

    # Transition protocols
    lines.append("\n# 第三编 过渡法\n\n")
    trans_index = yaml.safe_load((ROOT / "constitution/transition/_index.yaml").read_text())
    (SRC_DIR / "transition").mkdir()
    priority_badge = {"critical": "\U0001f534", "high": "\U0001f7e1", "medium": "\U0001f7e2"}
    for t in trans_index["protocols"]:
        src = ROOT / "constitution/transition" / t["file"]
        fm = read_frontmatter(src)
        title = fm.get("title", t["id"])
        badge = priority_badge.get(t.get("priority", ""), "")
        copy_md(src, SRC_DIR / "transition" / t["file"])
        lines.append(f"- [{badge} {title}](transition/{t['file']})\n")

    # Profiles
    lines.append("\n# 附录一 预设配置\n\n")
    (SRC_DIR / "profiles").mkdir()
    for profile_file in sorted((ROOT / "profiles").glob("*.yaml")):
        p = yaml.safe_load(profile_file.read_text())
        content = f"# {p['name']}\n\n{p.get('description', '').strip()}\n\n"
        content += "| 模块 | 选项 |\n|------|------|\n"
        for mod_id, opt_id in p.get("selections", {}).items():
            mod_info = module_data.get(mod_id, {})
            mod_title = mod_info.get("title", mod_id)
            opt_title = mod_info.get("options", {}).get(opt_id, opt_id)
            content += f"| {mod_title} | {opt_title} |\n"
        md_name = profile_file.stem + ".md"
        (SRC_DIR / "profiles" / md_name).write_text(content)
        lines.append(f"- [{p['name']}](profiles/{md_name})\n")

    # References
    lines.append("\n# 附录二 参考宪法\n\n")
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
