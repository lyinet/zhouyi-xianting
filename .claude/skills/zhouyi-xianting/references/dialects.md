# 提示词方言模板(六套)+ 锚点 + 自检清单

提示词由 agent 现场撰写,但**骨架与固定串照抄本文件,槽位值照抄数据文件**——自由发挥只允许在连接词层面。`〈…〉` 是槽位,下文「槽位速查」给出每个槽的数据出处。

## 0. 槽位速查

| 槽 | 出处 |
|---|---|
| 〈上境〉〈下境〉(中文名/elements/ornament/short/签名色/译名) | `realms.json` 按该卦 `upper`/`lower` 查 |
| 〈卦辞〉〈大象〉〈爻辞〉〈旋钮三值+理由〉〈远景人物 figure〉〈色板中/英〉 | `hexagrams.json` 该卦条目 |
| 〈光时EN〉〈前景框EN〉〈远景消隐EN/中〉 | `en-phrases.json` 的 `LIGHT` / `FOREGROUND` / `FARFADE`(按光时/经卦) |
| 〈人物EN〉〈天候EN〉〈水势EN〉 | `en-phrases.json` 的 `EN`(按卦序字符串键) |
| 〈六幕〉〈镜头〉〈时间弧〉 | `video.json` 该卦条目 |
| 全局锚点中英对照 | `realms.json` 的 `global_anchors` |
| 〈抖音标题句式〉〈话题池〉〈禁用词〉〈封面排字建议〉 | `douyin.json` |

**远景人物串**(按卦构造,取代旧的固定三人影与灵禽两套装置):
- 英文条:`〈en-phrases.EN[卦序].figure〉, seen from behind at a great distance, robes in 〈figure.robe_en〉, far too small for any facial feature`
- 中文条:`〈figure.count〉位古风女子的背影,〈figure.pose〉,衣作〈figure.robe_zh〉,远景小点,看不见面容`
- 人数与姿态编码卦义(1 孤 / 2 合 / 3 群),照抄 `hexagrams.json` 的 `figure`,不自创。
- **只此一处出现人物**:不再另写灵禽,也不再写固定三人影。不露脸、不写容貌年龄。
受光词:夜卦前景一律 **moonlit**,其余光时用 **sunlit**——单光源规则,夜卦条内不得出现 sunlit / daylight。

**上下境主语构造**(英文条):
- 非纯卦:上境主语 = `〈realm_en〉, 〈elements_en〉`;下境主语 = `〈realm_en〉`(裸名)。
- 八纯卦:上境同上;下境主语 = `a lower tier of the same realm`。
- "a second …" 之后要剥冠词:`the Celestial Gate` → `Celestial Gate`。

## 1. 静态四方言

### 1.0 画幅框架(先二选一)

**3:4 竖版**(默认,发布用):

| 方言 | 框架句 |
|---|---|
| MJ | `eye level, horizon low` |
| GPT/Nano | `a vertical 3:4 frame, camera at eye level with the horizon set low. The grandeur here is vertical — great height above, a long drop below` |
| Seedream | `3:4 竖构图,平视,地平线压在画面下部。宏大靠垂直落差:上有极高,下有深坠` |

叠合句(两境位置):
- MJ:`〈上境 short_en〉 floating free past the top edge, the viewer standing on a terrace far below`
- GPT/Nano:`High above, 〈上境主语〉, floating free with no ground beneath it, so large it continues past the top edge. The camera stands far below on 〈下境主语〉, itself a platform floating in open air`
- Seedream:`〈上境名〉,〈上境 elements_zh〉,整座悬空不着地,高踞画面上部并冲出顶端;镜头站在远低处的〈下境〉上,那也是一座浮在空中的平台`(纯卦下境作"同一〈境名〉的下一层平台")

**16:9 横版**(封面用):

| 方言 | 框架句 |
|---|---|
| MJ | `eye level, horizon just below centre` |
| GPT/Nano | `an ultrawide 16:9 frame, camera at eye level with the horizon just below centre. The grandeur here is lateral — width, and distance measured sideways` |
| Seedream | `16:9 超宽横构图,平视,地平线略低于画面中线。宏大靠横向:云海一路铺到极远的地平线` |

叠合句:
- MJ:`〈上境 short_en〉 floating in the upper third to one side, the viewer standing on a terrace across the cloud sea`
- GPT/Nano:`In the upper third and set to one side, 〈上境主语〉, floating free with no ground beneath it. The camera stands across the cloud sea on 〈下境主语〉, itself a platform floating in open air`
- Seedream:`〈上境名〉,〈上境 elements_zh〉,悬空不着地,位于画面上三分之一并偏向一侧;镜头站在云海另一端的〈下境〉上,那也是一座浮在空中的平台`

### 1.1 Midjourney 8.2(密集名词短语)

```text
〈框架句MJ〉, 〈叠合句MJ〉, vast empty sky between, cloud sea to a far horizon, 〈下境 ornament_en 第一项〉 〈sunlit|moonlit 按光时〉 razor-sharp foreground, a colossal waterfall falling into cloud, 〈人物EN·首子句〉 seen from behind, tiny for scale, 〈光时EN〉, 〈天候EN 第一子句〉, 〈色0EN〉 and 〈色1EN〉 with 〈色2EN〉 accents, photoreal cinematic still, immense scale, glowing air --ar 〈3:4|16:9〉 --v 8.2 --style raw --stylize 250 --chaos 5 --no text, watermark, crowds, close-up faces, modern objects, crushed blacks
```

硬规则:正文 ≤110 词(`--` 前);正文禁 no/without/avoid(否定只进 `--no`);**不用自造专名**——不用 realm_en,上境用 `short_en` 紧凑描述;只保留最强装置,不堆全景细节(第二座同境、地平线带细节留给 GPT/Nano)。

### 1.2 GPT-Image-2(自然散文,可长)

```text
A photoreal cinematic still in 〈框架句GPT〉.

〈叠合句GPT〉.

**Most of this picture is empty.** Open sky and an unbroken cloud sea running to a distant horizon should occupy roughly two thirds of the frame; the architecture occupies about a third. That emptiness is what makes the scene vast — do not fill it.

In the near foreground, 〈sunlit|moonlit 按光时〉 and rendered in razor-sharp high relief: 〈下境 ornament_en 全串〉. This is the densest detail in the picture — never a dark silhouette. A colossal waterfall pours off the platform edge and falls into cloud with no visible bottom.

For scale, place 〈人物EN〉, and near the horizon a second, far smaller 〈上境名EN·剥冠词〉, tiny with distance. Along the horizon band, 〈远景消隐EN〉.

The directional light is 〈光时EN〉. 〈天候EN·首字母大写〉. 〈水势EN·首字母大写〉. Keep the exposure bright and luminous, the air glowing, shadows open and full of detail rather than crushed.

Palette: 〈色0EN〉 and 〈色1EN〉, with 〈色2EN〉 only as an accent.

Leave the top strip relatively empty for a later title. Do not render text or calligraphy. No crowds, no close-up faces, no watermark, no modern objects.
```

### 1.3 Nano Banana Pro(命令式祈使)

```text
Photograph this in 〈框架句GPT〉.

〈叠合句GPT〉.

Give most of this picture away to nothing — open sky and a cloud sea running unbroken to a far horizon should take about two thirds of the frame. The buildings take the remaining third. It is the emptiness that makes this feel enormous, so resist filling it.

Right at the front, in full light and cut sharp enough to count the tool marks: 〈下境 ornament_en 全串〉. This is where the detail lives. Off the edge of the platform a vast waterfall drops away and is swallowed by cloud before it ever lands.

Put 〈人物EN〉 — they are there to tell you how big everything else is. Near the horizon, a second 〈上境名EN·剥冠词〉, so far away it is almost a speck. Along the horizon, 〈远景消隐EN〉.

〈光时EN·首字母大写〉 gives the scene its direction. 〈天候EN·首字母大写〉. 〈水势EN·首字母大写〉. Expose bright, let the air glow, keep the shadows open.

Hold the colour to 〈色0EN〉 and 〈色1EN〉, with 〈色2EN〉 only as an accent. No text, no crowds, no close-up faces.
```

### 1.4 Seedream 5.0 Pro(中文散文)

```text
〈框架句中文〉。〈叠合句中文〉。两者之间是一整片开阔的天空,云海一路铺展到极远的地平线——天空与云海约占画面三分之二,建筑只占三分之一,留白正是宏大的来源,切勿填满。近景是受光的精细浮雕,锐利到能看清凿痕:〈下境 ornament_zh〉,这是全画细节最密处,不是黑剪影。一道巨瀑自平台边缘倾泻而下,落入云中不见底。〈人物ZH〉,用来对照建筑之巨;地平线附近另有一座极小的〈上境名〉,远得几乎成点;地平线一带是〈远景消隐ZH〉。〈光时ZH〉,为画面的主光方向。〈天候(数据 weather 全句)〉。〈水势(数据 terrain_reason)〉。整体明亮通透,空气发光,暗部开放有细节,不压死黑。色调以〈色0ZH〉与〈色1ZH〉为主,仅以〈色2ZH〉点缀。照相写实电影剧照质感,体量极大,纵深宏阔,细腻微观细节,轻微胶片颗粒,4K 超清。顶部留白供后期排字。画面中不出现任何文字、人群与近景面孔。
```

中文条禁混入英文单词(4K 除外)。

## 2. 视频两方言

### 2.0 共用推导规则

**场景句**(Seedance 与 H3 共用):
- 非纯卦:`上方〈上境名〉——〈上境 elements_zh〉;下方〈下境名〉——〈下境 elements_zh〉;两境之间云海贯通`
- 纯卦:`同一座〈境名〉的上下两层——〈elements_zh〉,下层平台亦是〈境名〉,整座悬空于云海之上`

**光句**:`〈光时〉光时,〈点缀色ZH〉点缀色;〈weather 全句〉;雾气本身被光点亮、是画面最亮区;整体明亮通透,暗部开放不压死黑`(点缀色查 `realms.json` 的 `accent_by_light`)

**画幅句**:3:4 → `3:4 竖构图,平视远眺,地平线在画面中下部,宏大靠垂直落差:上有极高,下有深坠。顶部约五分之一留白供后期排卦名与卦辞,保持空旷`;16:9 → `16:9 超宽横构图,平视远眺,地平线略低于中线,宏大靠横向云海。顶部留白供后期排字,保持空旷`

**环境声** = 天候声(下表按 `weather_base`)`；` 水势声(下表按 `terrain`)`；` 人声:

| 天候 | 声 | 水势 | 声 |
|---|---|---|---|
| 晴 | 高空风声清朗,檐铃偶响 | 静 | 水面偶有涟漪轻响 |
| 薄雾 | 风声透过薄雾传来,檐铃隐约 | 上涨 | 水声渐起,缓缓漫过石阶 |
| 浓雾 | 声音被浓雾压低,檐铃几乎不闻 | 奔涌 | 激流轰鸣,浪头相撞 |
| 雨 | 雨声连绵,檐滴成线 | 干涸 | 泽底龟裂,唯余滴水回响 |
| 雪 | 万籁俱寂,落雪无声,偶有冰棱轻响 | | |
| 罡风 | 风声呼啸,经幡猎猎,檐铃急响 | | |

人声(按 `figure.count`,极远处,不成语句):1 →`极远处一声环佩,随即归于静`;2 →`两串环佩轻响,一前一后`;3 →`远处衣袂与环佩细碎交叠,听不出人语`。**不得出现对白、人语、歌声。**

**配乐**(按光时):拂晓→`一支清亮的编钟与古琴短句,疏朗初明`;正午→`编钟与古琴双声部,庄严恢宏,低音铺底`;薄暮→`古琴沉缓,音色带余晖之温`;夜→`古琴幽静低回,偶闻一声铜磬长鸣`。

**时间戳**:第 i 幕(0 起)起于 i×15000/n 毫秒,四舍五入取整。六幕:`At 00:00.000`(不写)/ `At 00:02.500` / `At 00:05.000` / `At 00:07.500` / `At 00:10.000` / `At 00:12.500`;乾坤七幕:`0 / 2143 / 4286 / 6429 / 8571 / 10714 / 12857` 毫秒。格式 `At 00:SS.mmm`。

**动爻强调**:动爻对应的幕,在该幕动作后加 `(动爻强调,运镜幅度加重一级)`,H3 条同位置加注。

### 2.1 Seedance 2.5(制作笔记风格,中文,段落序固定)

```text
格式:图生视频,首帧为该卦静态图,〈单镜头一镜到底|分镜N镜头〉,15秒,〈3:4|16:9〉画幅。
首帧:严格保留首帧的全部构成——上下两境的叠合方向、构图、色板、顶部留白,上下位置不得对调。
主体与场景:〈场景句〉。远景人物:〈figure.count〉位古风女子的背影,〈figure.pose〉,衣作〈figure.robe_zh〉,极小,不露脸。
镜头:〈video.json camera.shot〉,〈camera.move〉(〈camera.reason〉)。〈画幅句〉
光:〈光句〉。
氛围:〈weather 全句〉;〈terrain_reason〉。
动作弧(六爻六阶段,一镜内连续演化):〈幕1题〉——〈幕1动作〉;〈幕2题〉——〈幕2动作〉;……。   ← 一镜到底
镜头1(0–2.5秒,〈shot〉):〈题〉——〈动作〉。……   ← 六镜头分镜(时间按 2.0 节,逐镜列)
质感:35mm 胶片拍摄的高预算中式奇幻电影剧照质感,微胶片颗粒,真实材质——夯土粗糙颗粒、白玉温润、鎏金真实金属反射、青铜绿锈、朱漆旧痕;大气透视,纵深不少于四层;运动符合物理:云有惯性、水有重力、衣袂受风、雾有密度。
音频:〈环境声〉。配乐:〈配乐〉。无对白、无歌词、无字幕。
目标:捕捉「〈卦名〉」卦此景(〈time_arc.note〉)的一瞬,仿佛一段高预算中式奇幻电影的实拍素材,以胶片颗粒、真实材质、物理运动、克制运镜、留白收尾。
负面:不要万向节式的平滑运镜,运镜要有机、有呼吸感;不要现代商业调色;不要塑料质感;不要过度锐化;不要文字、字幕、水印;不要近景人物与人脸。
```

### 2.2 MiniMax H3(三字段 schema)

```text
I2VA: For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description:
[Shot 1] 〈3:4 竖构图|16:9 超宽横构图〉,平视远眺,〈地平线与宏大句〉。〈场景句〉。〈数量+种+状态〉。初幕〈幕1题〉——〈幕1动作〉。〈光句〉。35mm film look from a high-budget Chinese fantasy film, subtle grain, real material texture, atmospheric perspective, physically correct motion。no gimbal-smooth camera moves, organic breathing camera; no commercial colour grading, natural filmic colour; no plastic materials, real material texture; no over-sharpening, subtle film grain; no text, captions, watermarks; no close-up faces。顶部留白供后期排字,保持空旷。
At 00:02.500, 连续长镜头内,〈幕2题〉——〈幕2动作〉。   ← 一镜到底:每幕一行,无剪辑语
[Shot 2] At 00:02.500, the camera cuts to 〈幕2.shot〉。〈幕2题〉——〈幕2动作〉。   ← 六镜头分镜:每幕一镜,显式 cuts

overall_soundscape: 〈环境声〉。无对白、无歌词。
non_diegetic_music: 〈配乐〉。无对白。
```

规则:[Shot 1] 不带时间戳,且必须包含初幕;时间戳严格递增;一镜到底禁 `the camera cuts to`,分镜必须有;配乐只进 `non_diegetic_music`,`overall_soundscape` 只含环境声。

## 3. 禁用词表(全库)

静态质量词:`masterpiece / best quality / 8k / ultra detailed / highly detailed / award winning / trending on artstation / hyper realistic / super detailed`。
视频夸赞词(中英):`高级 / 电影感 / 炸裂 / 唯美 / 震撼 / 史诗 / 惊艳 / 大片 / 超清 / 极致 / 顶级 / epic / stunning / breathtaking / masterpiece`。
替代法:写具体可观察的物理现象,不写评价。

## 3.5 抖音发布文案(国风美学向)

素材全部来自已有字段,不新增事实来源。抖音只有一个「作品描述」框,话题写在描述里,故按**实际粘贴顺序**产出:

```text
〈标题行〉

〈简介第一句·画面〉〈简介第二句·卦义〉〈简介第三句·引导〉

〈话题1〉 〈话题2〉 〈话题3〉 〈话题4〉 〈话题5〉 #周易仙庭
```

- **标题行**:从 `douyin.json` 的 `title_patterns` 选一式,按 `use_when` 判断该卦适用哪式。≤20 字。
- **简介**:三句,依 `intro_structure`。第一句写八境+光时+天候的具象名词;第二句引卦辞或大象传关键词作观照;第三句开放式提问。总长 ≤120 字。
- **话题**:恰好 6 个 = `broad` 取 3(逐期轮换,不要每期全同)+ `vertical` 取 2(按内容)+ `series` 固定。
- **封面排字**:另给一行建议,取 `douyin.json` 的 `cover_text`。图上不渲染文字,这是给后期排版用的。

红线:`douyin.json` 的 `banned` 三类词一个都不许出现;不断吉凶,不给医疗/投资/法律建议 —— 与解卦段同一原则。

## 4. 交付前自检清单

**起卦**:演算已逐步展示 □ 时辰来源已注明 □ 自算卦画与 `lines` 核对一致 □ 之卦已查 □

**静态四条同源**:色板三色四条一致 □ 画幅一致 □ 光源方向一致 □ 上境译名出现在 GPT/Nano □ 非纯卦下境译名也出现 □

**MJ**:`--ar` 与画幅对应 □ `--style raw` 在 □ 正文无 no/without/avoid □ 正文 ≤110 词 □ 无禁用词 □ 未用自造专名 □

**英文条锚点词**(MJ/GPT/Nano 各自):`glow` □ `figures`或`women` □ `waterfall` □ `empty` 或 `emptiness` □ `horizon` □ `float` □;无月光与日光并存 □;无实词为主的重复三元词组(境名重复除外) □

**人物**:人数与姿态照抄 `figure` □ 服色=该卦色板点缀色 □ 只出现一处人物(无灵禽、无固定三人影) □ 未写容貌年龄 □ 背影不露脸 □

**中文条(Seedream)**:`留白正是宏大的来源` □ `悬空不着地` □ `地平线` □ `巨瀑` □ `受光的精细浮雕` □ `空气发光` □ 顶部留白 □ 画幅声明 □ 无英文混入(4K 除外) □ 无 `，，/。。/、，` 拼接残留 □

**视频条**:段落/字段齐(Seedance 十一段、H3 四字段) □ 负面约束齐全 □ 无夸赞词 □ 六幕标题与 `video.json` 一致 □ 时间戳严格递增且在 15s 内 □ [Shot 1] 无时间戳且含初幕 □ 一镜/分镜的剪辑语正确 □ 动爻强调已标注(有动爻时) □ 顶部留白 □ 无对白/歌词/字幕 □ 每幕至多一个非完美事件 □

**抖音文案**:标题行 ≤20 字 □ 句式取自 `title_patterns` □ 简介三句齐且 ≤120 字 □ 话题恰 6 个 □ `#周易仙庭` 在内 □ 无 `banned` 三类词 □ 无吉凶断言 □ 封面排字建议已给 □

机械清单查不出语病与自相矛盾——通读一遍再交付。
