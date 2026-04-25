# Transitional-Justice-CN

Open-source legal framework for a democratic China — prepared in advance so the transition costs less time, less chaos, and less suffering.

开源中国转型正义法律体系：预先编写"新系统的源代码"，缩短政权更迭后的阵痛期。

## Why

Every democratic transition faces the same bottleneck: drafting a new legal system from scratch under extreme time pressure. This project eliminates that bottleneck by preparing a modular, configurable constitutional framework *before* it is needed.

Two benefits:
1. **Reduce transition pain** — a ready-made legal framework prevents power vacuums, protects property, and keeps public services running.
2. **Lower the perceived risk** — when people can see that a credible alternative exists, the fear of chaos no longer props up the status quo.

## Architecture

```
constitution/
├── core/           # Non-negotiable rights (immutable)
│   ├── human-dignity.md
│   ├── freedom-of-speech.md
│   ├── freedom-of-press.md
│   └── ...14 provisions
├── modules/        # Contested topics (pick-and-choose)
│   ├── death-penalty/    (abolished | restricted | moratorium)
│   ├── gun-rights/       (right-to-bear-arms | licensed | prohibited)
│   ├── abortion/         (protected-right | trimester | restricted)
│   ├── state-structure/  (federal | unitary-decentralized | unitary-centralized)
│   ├── land-ownership/   (full-private | mixed | leasehold)
│   ├── marriage-equality/(full-equality | civil-union | traditional)
│   ├── drug-policy/      (decriminalized | cannabis-legal | strict-prohibition)
│   └── ...
├── transition/     # Day-0 operating procedures
│   ├── government-continuity.md
│   ├── property-protection.md
│   ├── military-nationalization.md
│   ├── transitional-justice.md
│   └── ...9 protocols
references/         # Source constitutions for comparison
├── roc-1946-constitution.md    # 中华民国宪法
├── germany-basic-law.md        # 德国基本法
├── japan-constitution.md       # 日本国宪法
├── south-korea-constitution.md # 大韩民国宪法
└── south-africa-constitution.md# 南非共和国宪法
profiles/           # Preset configurations (non-binding examples)
├── liberal.yaml
├── moderate.yaml
└── conservative.yaml
schema/             # Data structure definitions (YAML Schema)
```

### Design Principles

- **Core provisions** are immutable — freedom of speech, press freedom, judicial independence, etc. These cannot be removed or overridden.
- **Modules** represent genuinely contested policy areas where reasonable people disagree. Each module provides 2-3 mutually exclusive options. The final selection is deferred to a future constitutional convention.
- **Transition protocols** are essential Day-0 operating procedures — they keep the lights on and prevent chaos during the transition period.
- **Profiles** are non-binding example configurations that demonstrate how the modular system works.

### Data Format

All legal text is stored as Markdown with YAML frontmatter. Machine-parseable, human-readable, Git-friendly.

```yaml
---
id: freedom-of-speech
title: 言论自由
tier: core
category: fundamental-rights
references:
  - constitution: roc-1946
    articles: [11]
---
# 言论自由
人民有言论、讲学、著作之自由。
...
```

## Contributing

This project welcomes contributions from legal scholars, political scientists, and citizens.

- **Core provisions**: Submit issues to propose changes. These require broad consensus.
- **Modules**: Submit PRs with new options or improvements to existing ones.
- **Transition protocols**: These are the highest-priority items. Real-world expertise is especially valued.
- **References**: Help us collect and translate constitutions and legal texts.
- **Fork freely**: If you disagree with core design decisions, fork and build your own "distribution."

## Governance

- Recognized exiled legal professionals serve as core maintainers (public contributors, no privacy concerns).
- Issues are open to everyone — anonymous contributions welcome.
- AI agents assist the legal team with research, consistency checking, and GitHub operations.

## License

[CC0 1.0 Universal](LICENSE) — This legal framework belongs to no one and everyone.
