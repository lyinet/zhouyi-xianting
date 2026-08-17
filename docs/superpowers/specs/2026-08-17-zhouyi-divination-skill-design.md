# 周易仙庭 · 起卦 Skill 转型设计

- 日期:2026-08-17
- 状态:已实施
- 前身:`2026-08-09-zhouyi-xianting-design.md`(静态图集)与 `2026-08-15-zhouyi-xianting-video-design.md`(视频扩展)

## 1. 动机:交付形态与需求错位

前身两期把项目建成了「批处理提示词工厂」:数据 → 生成脚本 → 1024 条预生成提示词(静态 512 + 视频 512)+ CI 验收。质量体系是好的,但用户真正想要的是一个**可安装的 skill**:在装好 skill 的 agent 里输入一个条件(如「给今天算一卦,8月17号」),由 skill 算出符合该条件的卦象,再生成提示词。

差距有三:

1. 旧 skill 不能自包含运行——SKILL.md 全部指向仓库内相对路径,拷出仓库即失效;
2. 参数化入口是命令行脚本与批处理,不是对话;
3. 主产品是静态库,而需求是按需生成。

更根本的缺口:**项目没有「条件 → 卦象」这一环**。起卦(占卜算法)从未实现过。

## 2. 已锁定的决策(用户拍板)

| # | 决策 | 取值 |
|---|---|---|
| 1 | skill 定位 | 周易是底层条件:输入条件 → 起卦 → 解卦 → 提示词 |
| 2 | 生成方式 | 纯 agent 现场撰写,不内置生成脚本 |
| 3 | 预生成库 | 1024 条全部删除(git 历史可找回) |

## 3. 起卦法选型

需求示例「给今天算一卦,8月17号」指向时间起卦,即梅花易数的年月日时法。传统算法用**农历**,但 agent 在无工具链时无法可靠完成公历→农历换算,这是必须绕开的失败模式。选型:

- **公历变体**:年支序 = (公元年−4) mod 12 + 1(即干支年序,2026 → 午 7),月、日取公历数,时支序取提问时辰。上卦=(年+月+日) mod 8,下卦=再加时 mod 8,动爻=四数之和 mod 6(余 0 取 8/6)。全部整数运算,agent 可复算、读者可复核。
- 用户明确给农历,则各数直接按农历取,输出注明。
- 另支持数字卦(两数定上下卦,和+时支定动爻;一数按位拆半)、字数卦(所问语句前后半字数定上下卦)、直给卦(卦名/卦序)。

**防错机制**:演算必须逐步展示;起卦者须自算卦画(下卦三位+上卦三位,自下而上)并与 `hexagrams.json` 的 `lines` 核对,不符即演算有错——这是 `hexagram_checks.py` 第 2 条的人工版。动爻翻转得之卦,解卦时引其卦辞一句。

动爻的视觉作用保持克制:静态画面不变(避免双解),视频六幕中动爻对应幕标注「动爻强调」、运镜加重一级。

## 4. 一致性从脚本搬到规则

纯 agent 撰写意味着失去「同一数据 → 逐字相同输出」的保证。对策是把脚本的确定性拆成三类约束,全部固化在 skill 包内:

| 脚本时代的机制 | skill 时代的对应物 |
|---|---|
| 模板 f-string | `references/dialects.md` 六套填空模板(骨架与固定串照抄,自由只留给连接词) |
| en_phrases.py 译名/短语库 | `references/en-phrases.json`(唯一来源,照抄不另译) |
| validate.py 成品扫描 | `references/dialects.md` 第 4 节交付前自检清单(锚点词、参数、禁用词、同源性逐项打勾) |

接受的事实:同一卦两次生成的提示词非逐字相同,但同源与达标由上述机制保证。

## 5. 架构变化

```
删除:prompts/ prompts-wide/ video-prompts/ video-prompts-h3/(约2.5MB)
     scripts/gen_prompts.py gen_video_prompts.py en_phrases.py
     .claude/skills/zhouyi-xianting-video/(并入统一 skill)
迁移:data/{realms,hexagrams,video}.json → .claude/skills/zhouyi-xianting/references/
     en_phrases.py → references/en-phrases.json
新增:SKILL.md 重写(起卦+解卦+转译+输出契约)
     references/dialects.md(模板+锚点+自检清单)
改向:build_hexagrams.py 读写 references/;validate.py 改为数据完整性验收
     (分解五条 + realms/hexagrams/video/en-phrases 结构检查);selftest.py 同步瘦身
```

数据刷新链保持单一事实来源:ctext → `fetch_yaoci.py` → `data/hexagram_texts.json` → `build_hexagrams.py` → `references/hexagrams.json`。CI 继续强制 selftest + validate。

## 6. 风险

| 风险 | 应对 |
|---|---|
| agent 起卦算错 | 演算强制逐步展示;卦画与 lines 核对;selftest 的变异测试保证核对器本身有效 |
| 提示词漂移 | 固定模板骨架 + 固定译名 + 自检清单;用户发现漂移时可对照数据表核对槽位 |
| skill 体积(references 约 500KB) | agent 按需读取单卦条目,SKILL.md 本体保持精简,重内容全部下放 references |
| 公历变体与传统梅花不同结果 | 输出注明取法;给农历按农历,保留传统路径 |
