# Transitional-Justice-CN

开源中国转型正义法律体系：预先编写"新系统的源代码"，缩短政权更迭后的阵痛期。

Open-source constitutional framework for a democratic China.

## 为什么要做这个项目

每一次民主转型都面临同样的瓶颈：在极端的时间压力下从零开始起草一套新法律体系。本项目通过**提前准备**一套模块化、可配置的宪法框架来消除这个瓶颈。

两个好处：
1. **降低转型阵痛** — 现成的法律框架可以防止权力真空、保护私有财产、维持公共服务运转。
2. **降低变革的心理门槛** — 当人们看到一个可信的替代方案已经存在，对混乱的恐惧就不再能为现状背书。

## 项目结构

```
constitution/
├── core/           # 核心权利（不可删改）
│   ├── human-dignity.md         人格尊严
│   ├── freedom-of-speech.md     言论自由
│   ├── freedom-of-press.md      新闻自由
│   └── ... 共 14 项
├── modules/        # 可选模块（各方立场并列，制宪会议时再选）
│   ├── death-penalty/     死刑存废 (废除 | 限制 | 暂缓)
│   ├── gun-rights/        枪支管制 (入宪 | 许可证 | 禁枪)
│   ├── abortion/          堕胎权   (宪法保障 | 阶段制 | 严格限制)
│   ├── state-structure/   国家结构 (联邦制 | 分权单一制 | 集权单一制)
│   ├── land-ownership/    土地制度 (完全私有 | 混合制 | 永久使用权)
│   ├── electoral-system/  选举制度 (单选区制 | 排序复选 | 比例代表 | 混合制)
│   ├── marriage-equality/ 婚姻平权 (完全平权 | 民事结合 | 传统定义)
│   ├── drug-policy/       毒品政策 (去罪化 | 大麻合法 | 严格禁毒)
│   └── ...
├── transition/     # 过渡法（Day 0 应急操作规程）
│   ├── government-continuity.md  政权交接
│   ├── property-protection.md    财产保护
│   ├── military-nationalization.md 军队国家化
│   ├── transitional-justice.md   转型正义
│   └── ... 共 9 项
references/         # 参考宪法
├── roc-1946-constitution.md       中华民国宪法
├── germany-basic-law.md           德国基本法
├── japan-constitution.md          日本国宪法
├── south-korea-constitution.md    大韩民国宪法
├── south-africa-constitution.md   南非共和国宪法
└── us-constitution.md             美利坚合众国宪法
profiles/           # 预设配置（非约束性示例）
├── liberal.yaml       自由主义倾向
├── moderate.yaml      温和中间路线
└── conservative.yaml  保守稳健路线
schema/             # 数据结构定义（YAML Schema）
```

## 设计原则

- **核心条款**不可删改 — 言论自由、新闻自由、司法独立等。任何模块选择或配置都不能覆盖它们。
- **可选模块**代表合理分歧的政策领域。每个模块提供 2-3 个互斥选项，最终选择权留给未来的制宪会议。
- **过渡法**是 Day 0 的应急操作规程 — 在转型期间维持社会运转、防止混乱。
- **预设配置**是非约束性的示例，展示模块化系统如何组合使用。

## 数据格式

所有法律文本以 **Markdown + YAML frontmatter** 存储。机器可解析、人类可阅读、Git 友好。

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

## 参与贡献

本项目欢迎法学学者、政治学者和公民参与。

- **核心条款**：通过 Issue 提议修改，需要广泛共识。
- **可选模块**：通过 PR 提交新选项或改进现有选项。
- **过渡法**：优先级最高的部分，特别需要实务经验。
- **参考资料**：帮助收集各国宪法和法律文本。
- **随意 Fork**：如果你不同意核心设计决策，Fork 一份构建你自己的"发行版"。

## 治理

- 受认可的流亡法律专业人士担任核心维护者（公开贡献，无隐私顾虑）。
- Issue 向所有人开放，欢迎匿名贡献。
- AI Agent 辅助法律团队进行研究、一致性检查和 GitHub 操作。

## 许可证

[CC0 1.0 通用](LICENSE) — 这套法律框架不属于任何人，属于所有人。
