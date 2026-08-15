---
name: cinematic-image-prompt
description: Base skill for writing cinematic AI image prompts across multiple models — Midjourney 8.2, GPT-Image-2, Nano Banana Pro, Seedream 5.0 Pro. Use when generating or revising any cinematic still prompt, translating an 8-slot blueprint into model dialects, or when a specialized skill (e.g. zhouyi-xianting) hands off slot content for dialect translation. Triggers: 图像提示词/剧照/电影感构图/MJ 参数/两主一辅/画幅.
---

# Cinematic Image Prompt · 8 槽蓝图 × 四模型方言

## Overview

把一段画面构思填进 **8 槽蓝图**，再翻译成四种模型方言。槽位内容决定"画什么"，方言层决定"怎么用该模型的语法说"。特化 skill（如 `zhouyi-xianting`）负责填槽，本 skill 负责方言，**不重复实现特化规则**。

## 8 槽蓝图

| # | 槽 | 内容 |
|---|---|---|
| 1 | 画幅/机位 | 3:4 / 16:9、平视/仰视/贴水面、地平线位置 |
| 2 | 主体 | 画面中占主导的**一个**核心建筑/对象 |
| 3 | 环境 | 场景的视觉要素（主体之外的构成） |
| 4 | 三层纵深 | 暗前景框 / 中景 / 远景消隐，最远层没入光里 |
| 5 | 光 | 光时（拂晓/正午/薄暮/夜）+ 主光源方向，只给一个光源 |
| 6 | 氛围 | 天候 + 水势/地势，决定空气与情绪 |
| 7 | 色板 | **两主一辅**：主色两个 + 点缀色一个，三色上限 |
| 8 | 质感 | 渲染语言：照相写实 / 胶片 / CG 剧照等 |

**两主一辅是硬规则。** 三个以上主色会让模型调出浑浊的灰。

## 四模型方言

### Midjourney 8.2（密集名词短语）

- 靠密集名词短语工作，**超 100 词后新增词几乎不起作用**——只保留最强装置。
- 参数挂行末：`--ar 3:4 --v 8.2 --style raw --stylize 250 --chaos 5`。
- 否定词只出现在 `--no`，正文不得出现 no / without / avoid。
- `--v 8.2` 若账号不接受，去掉该参数即可。
- 模型不认识自造专名（如"天阙"），改用紧凑描述（"a white jade terrace above a sea of clouds"）。

### GPT-Image-2（自然散文，可长）

- 自然语言段落，允许解释性句子（"Most of this picture is empty…"）。
- 可用加粗强调关键要求；可写"Leave the top strip empty for a later title"这类后期说明。

### Nano Banana Pro（命令式祈使）

- 以 "Photograph this in …" 开头的命令式口吻，其余与 GPT 接近，句法更直接。
- 适合逐句下达视觉指令。

### Seedream 5.0 Pro（中文散文）

- 中文自然段落，保留画幅、机位、留白、细节、禁令等全部要点。
- 不得混入英文（4K 除外）。

## 通用要求

- **明度**：雾气本身被光点亮、是画面最亮区域；整体明亮通透，暗部开放不压死黑。
- **尺度**：建筑体量极大、向画顶外延伸；极小的人物/鸟作尺度锤；纵深不少于四层。
- **留白**：建筑约占三成，天空与云海占七成——留白即宏大，填满杀死空间感。
- **禁令**：无文字渲染（顶部留白后期排版）、无近景面孔、无水印、无现代物件。
- **禁用词**：masterpiece / best quality / 8k / ultra detailed / trending on artstation 等质量词一律不写。

## 输出契约

每个模型一行标题 + 一个只含提示词的代码块。多条提示词必须**同源**：主体、光源方向、三层纵深元素、色板、画幅在各条中一致。

## Red flags

| 症状 | 说明 |
|---|---|
| 色板超三色 | 模型调出浑浊的灰，砍到两主一辅 |
| 多个主光源/月光与日光并存 | 违反单光源规则，只留一个 |
| 画面被填满 | 天空云海占七成，留白是宏大来源 |
| 暗部压死黑 | 破坏明度锚点，暗部开放保留细节 |
| 专名直译给英文模型 | 图像模型不认识自造专名，用紧凑描述 |
| MJ 正文出现否定词 | 否定词移入 --no |
| 远景与中景同名物件 | 远景消隐物与中景招牌物件不得同名 |

## 参考

- 方言细则可扩展为 `references/model-dialects.md`（如各模型版本号、参数演变）。
- 特化层示例：`~/.claude/skills/zhouyi-xianting/` 用八境 + 三旋钮填满本 skill 的 8 槽。
