---
name: zhouyi-xianting-video
description: Use when generating or revising AI video prompts for the 周易/易经 hexagram series in this project — triggered by 视频/动画/仙庭动画/Seedance/MiniMax H3/Hailuo/一镜到底/分镜, by a hexagram name or number (乾、屯、未濟、第 3 卦), or by requests to turn a hexagram still into a motion clip, regenerate the video prompt set, or re-aspect it.
---

# 周易仙庭 · 卦象转译为视频

## Overview

本 skill 是静态图集 `zhouyi-xianting` 的**视频扩展层**。它把一卦转译为图生视频提示词：**首帧 = 该卦静态图**，视频层只加时间维度——六爻六幕的动作弧、镜头运动、三旋钮的时间演化、音频声景。

两种结构都出：**一镜到底 15s**（六爻为六个连续阶段）与**六镜头分镜**（每爻一镜）。两个目标模型：**Seedance 2.5**（制作笔记风格）与 **MiniMax H3 / Hailuo**（三字段 schema）。

核心原则与静态层一致：**画面结构就是卦的结构，时间结构就是爻的结构。**

## 数据来源

| 需要什么 | 去哪拿 |
|---|---|
| 八境定义、签名色、英文译名、全局锚点 | `data/realms.json` |
| 卦辞、爻辞、三旋钮、灵禽、色板 | `data/hexagrams.json`（含 `yaoci`） |
| 六幕表、镜头、时间弧 | `data/video.json` |
| 已生成的成品视频提示词 | `video-prompts/`（Seedance）与 `video-prompts-h3/`（H3） |

改动数据后重跑生成器，不手改成品：

```bash
python3 scripts/gen_video_prompts.py && python3 scripts/validate.py
```

## 六爻六幕（叙事引擎）

六条爻辞 = 六幕，五爻（君位）为高潮帧。幕的动作必须能由爻辞意象辩护：

| 幕 | 爻 | 叙事位 |
|---|---|---|
| 1 | 初爻 | 起势（潜/始） |
| 2 | 二爻 | 显现 |
| 3 | 三爻 | 行动/转折 |
| 4 | 四爻 | 过渡/试探 |
| 5 | 五爻 | **高潮**（盛） |
| 6 | 上爻 | 收束（亢/止） |

乾/坤另有第 7 幕（用九/用六）作收束。`video.json` 的 `beats[].reason` 引用爻辞原文——**没有理由的幕就是随手编的**。

## 镜头由卦德驱动

上卦主导运镜（画面主体在上），下卦影响机位微调（下卦为坎/兑时贴水面平视）。机位基线：平视远眺、地平线在画面中下部、不用低机位仰视。

| 经卦 | 德性 | 运镜 |
|---|---|---|
| 乾 | 健 | 上升 Crane / 极缓推近 |
| 坤 | 顺 | 缓慢横移 Truck |
| 震 | 动 | 快速推镜 + 轻微震动 |
| 巽 | 入 | 纵深穿廊 Dolly |
| 坎 | 陷 | 缓降 Pedestal down |
| 離 | 丽 | 环绕 Arc（灯光明灭） |
| 艮 | 止 | 静止 Static + 极慢 Zoom |
| 兌 | 悦 | 轻摇 Pan（涟漪扩散） |

卦义要求时可以覆盖（如泰上卦坤却取纵向缓推贯通两境），理由写入 `camera.reason`。

## 三旋钮 → 时间弧

- **光时**：多数卦恒定（15s 内不演化防变色）；剥、離、豐等少数卦允许演化，见 `time_arc`。
- **天候**：静止态缓动（云流/雾漫/雨落/雪飘/风卷），非完美事件由此取材。
- **水势**：静 → 上涨 → 奔涌 → 干涸 即水的运动弧，直接写进对应幕的动作。

## 音频

- `ambience`：风、水、檐铃、经幡、鹤鸣——与画面元素一一对应（有鹤即有鹤鸣）。
- `music`：编钟、古琴、铜磬（中式仙庭音色），光时定调性：拂晓清亮 / 正午庄严 / 薄暮沉缓 / 夜幽静。
- 无对白、无歌词、无字幕。H3 条中配乐只写进 `non_diegetic_music`，`overall_soundscape` 只含环境声。

## 去 AI 味（审美支点）

**素材来源身份 = 高预算中式奇幻电影，35mm 胶片摄影机实拍。** 由此推导：

| AI 默认行为（要关掉） | 负面约束 |
|---|---|
| 平滑万向节运镜 | 无 gimbal-smooth 运动，运镜有机、有呼吸感 |
| 现代商业调色（青橙） | 自然胶片色彩，无商业分级 |
| 塑料感材质 | 真实材质：夯土颗粒、白玉温润、鎏金金属反射、青铜绿锈、朱漆旧痕 |
| 无重力飘浮 | 物理正确：云有惯性、水有重力、鹤有翅振、雾有密度 |
| 过度锐化 | 微胶片颗粒，无锐化光晕 |

**非完美事件**（仙庭版）：风动经幡、云影掠过、光柱中尘埃浮动、水瀑摆动、鹤变换队形、镜头轻微呼吸。每幕至多一个。

**禁用抽象夸赞词**：高级、电影感、炸裂、唯美、震撼、史诗、惊艳、epic、stunning、masterpiece——写具体可观察的物理现象，不写评价。

## 两模型方言

### Seedance 2.5（制作笔记风格，中文）

段落顺序固定：格式（含首帧锚定）→ 首帧 → 主体与场景 → 镜头 → 光 → 氛围 → 动作弧/分镜 → 质感 → 音频 → 目标 → 负面。时长/画幅是外部参数写在格式行，不进正文。

### MiniMax H3（三字段 schema）

```text
I2VA: For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description:
[Shot 1] 3:4 竖构图，平视远眺，……。初幕〈幕名〉——〈动作〉。……（首镜无时间戳）
At 00:02.500, 连续长镜头内，〈幕名〉——〈动作〉。   ← 一镜到底
[Shot 2] At 00:02.500, the camera cuts to 中景。〈幕名〉——〈动作〉。  ← 六镜头分镜

overall_soundscape: 环境声。无对白、无歌词。

non_diegetic_music: 配乐。无对白。
```

- 时间戳严格递增（15s 六幕 = 0 / 2.5 / 5.0 / 7.5 / 10.0 / 12.5；七幕 = 0 / 2.1 / 4.3 / 6.4 / 8.6 / 10.7 / 12.9）。
- 一镜到底只用单一 `[Shot 1]` + 时间标记，不出现剪辑语；六镜头分镜每幕一镜、显式 cuts。
- 运镜用规范词表：push/pull, zoom, pan, truck, tilt, pedestal, arc, tracking, static, shake, POV, roll + 幅度/速度。

## 输出契约

每卦一个代码块：Seedance 一条（制作笔记）、H3 一条（三字段）。两模型必须同源——六幕、运镜、色板、画幅、光时一致。画幅 3:4 竖版（发布）与 16:9 横版（封面）各出一套。

## Red flags

| 症状 | 说明 |
|---|---|
| 初爻幕从提示词里消失 | [Shot 1] 必须包含初幕动作，时间标记从第二幕开始 |
| H3 的 soundscape 里写进配乐 | 配乐只进 non_diegetic_music，两字段不得重复 |
| 一镜到底出现 "the camera cuts to" | 一镜到底无剪辑；剪辑语只属于六镜头分镜 |
| 运镜与卦德无关 | 上卦定运镜，覆盖必须写理由 |
| 出现"高级/电影感/唯美" | 抽象夸赞词全库禁用，改写真实现象 |
| 幕的动作与爻辞对不上 | 每幕 reason 必须能引用爻辞辩护 |
| 顶部没有留白 | 延续静态体系，顶部 1/5 留白供后期排字 |
