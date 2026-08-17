# -*- coding: utf-8 -*-
"""把验收标准变成可执行检查(数据完整性版)。

skill 转型后提示词由 agent 现场撰写,不再有可扫描的成品文件;本脚本守护
skill 所依赖的全部数据:上下卦分解五条独立验证 + realms/hexagrams/video/
en-phrases 的结构完整性。任何一项不过就是回归。

提示词层面的验收已转为 skill 内的 agent 自检清单
(.claude/skills/zhouyi-xianting/references/dialects.md 第 4 节)。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hexagram_checks import verify_decomposition
from fetch_yaoci import ORDER as LINE_ORDER, label_gt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(BASE, '.claude', 'skills', 'zhouyi-xianting', 'references')

fails = []
H = json.load(open(f'{REF}/hexagrams.json', encoding='utf-8'))['hexagrams']
RJ = json.load(open(f'{REF}/realms.json', encoding='utf-8'))
V = json.load(open(f'{REF}/video.json', encoding='utf-8'))['hexagrams']
EP = json.load(open(f'{REF}/en-phrases.json', encoding='utf-8'))

LIGHTS = {'拂晓', '正午', '薄暮', '夜'}
WEATHERS = {'晴', '薄雾', '浓雾', '雨', '雪', '罡风'}
TERRAINS = {'静', '上涨', '奔涌', '干涸'}
TRIGRAMS = set('乾坤震巽坎離艮兌')


# ---------------------------------------------------------------- 分解五条
decomp_fails = verify_decomposition(H)
fails.extend(f'[分解] {f}' for f in decomp_fails)


# ---------------------------------------------------------------- realms
R = {r['trigram']: r for r in RJ['realms']}
if set(R) != TRIGRAMS:
    fails.append(f'[realms] 经卦集合不符: {sorted(set(R) ^ TRIGRAMS)}')
en_names = [r['realm_en'] for r in RJ['realms']]
if len(set(en_names)) != len(en_names):
    fails.append('[realms] realm_en 有重复')
for r in RJ['realms']:
    tag = f"[realms] {r.get('trigram', '?')}{r.get('realm', '?')}"
    for k in ('element', 'nature', 'realm', 'realm_en', 'elements_zh', 'elements_en',
              'palette_zh', 'palette_en', 'short_zh', 'short_en',
              'ornament_zh', 'ornament_en'):
        if not str(r.get(k, '')).strip():
            fails.append(f'{tag} 缺字段 {k}')
    if len(r.get('palette_zh', [])) != 2 or len(r.get('palette_en', [])) != 2:
        fails.append(f'{tag} 签名色应为中英各 2 色')
if set(RJ.get('accent_by_light', {})) != LIGHTS:
    fails.append('[realms] accent_by_light 须覆盖四种光时')
for k in ('aspect', 'render_zh', 'render_en', 'camera', 'creature', 'text',
          'exposure_zh', 'exposure_en', 'scale_zh', 'scale_en',
          'negative_space_zh', 'negative_space_en', 'vista_zh', 'vista_en',
          'float_zh', 'float_en', 'foreground_zh', 'foreground_en',
          'figures_zh', 'figures_en'):
    if not str(RJ.get('global_anchors', {}).get(k, '')).strip():
        fails.append(f'[realms] global_anchors 缺 {k}')


# ---------------------------------------------------------------- hexagrams
for h in H:
    tag = f"[数据] 第{h['no']}卦{h.get('name', '?')}"
    for k in ('no', 'name', 'symbol', 'upper', 'lower', 'lines',
              'upper_realm', 'upper_realm_en', 'lower_realm', 'lower_realm_en',
              'guaci', 'tuan', 'daxiang', 'yaoci', 'dials', 'creature',
              'palette_zh', 'palette_en', 'source'):
        if k not in h:
            fails.append(f'{tag} 缺字段 {k}')
            break
    d = h.get('dials', {})
    if d.get('light') not in LIGHTS:
        fails.append(f'{tag} 光时取值非法: {d.get("light")}')
    if d.get('weather_base') not in WEATHERS:
        fails.append(f'{tag} 天候基型非法: {d.get("weather_base")}')
    if d.get('terrain') not in TERRAINS:
        fails.append(f'{tag} 水势取值非法: {d.get("terrain")}')
    for k in ('light', 'weather', 'terrain'):
        if not str(d.get(k, '')).strip():
            fails.append(f'{tag} 旋钮 {k} 为空')
    for k in ('light_reason', 'weather_reason', 'terrain_reason'):
        if not d.get(k, '').strip():
            fails.append(f'{tag} 旋钮 {k} 无依据')
    if len(h.get('palette_zh', [])) != 3 or len(h.get('palette_en', [])) != 3:
        fails.append(f'{tag} 色板应为中英各 3 色(两主一辅)')
    cr = h.get('creature', {})
    for k in ('kind', 'count', 'state'):
        if not str(cr.get(k, '')).strip():
            fails.append(f'{tag} 灵禽缺 {k}')
    yaoci = h.get('yaoci', [])
    if len(yaoci) not in (6, 7):
        fails.append(f'{tag} 爻辞 {len(yaoci)} 条,应为 6(乾坤可 7)')
    labels = [y['line'] for y in yaoci]
    for y in yaoci:
        if not y.get('text', '').strip():
            fails.append(f'{tag} {y.get("line", "?")} 爻辞为空')
    for a, b in zip(labels, labels[1:]):
        if not label_gt(b, a):
            fails.append(f'{tag} 爻标签非递增: {a}->{b}')
    if labels and labels[0] not in ('初九', '初六'):
        fails.append(f'{tag} 首爻标签非法: {labels[0]}')
    if not str(h.get('guaci', '')).strip() or not str(h.get('daxiang', '')).strip():
        fails.append(f'{tag} 卦辞或大象为空')
    if not str(h.get('source', '')).startswith('https://ctext.org/'):
        fails.append(f'{tag} source 非 ctext URL')
if sorted(x['no'] for x in H) != list(range(1, 65)):
    fails.append('[数据] 卦序须为 1–64 连续')


# ---------------------------------------------------------------- video
if sorted(int(k) for k in V) != list(range(1, 65)):
    fails.append('[video] 键须为 1–64 连续')
by_no = {h['no']: h for h in H}
for n, v in V.items():
    h = by_no[int(n)]
    tag = f"[video] 第{n}卦{h['name']}"
    cam = v.get('camera', {})
    for k in ('shot', 'move', 'reason'):
        if not str(cam.get(k, '')).strip():
            fails.append(f'{tag} camera 缺 {k}')
    ta = v.get('time_arc', {})
    for k in ('note', 'reason'):
        if not str(ta.get(k, '')).strip():
            fails.append(f'{tag} time_arc 缺 {k}')
    beats = v.get('beats', [])
    if len(beats) != len(h['yaoci']):
        fails.append(f'{tag} 幕数 {len(beats)} 与爻数 {len(h["yaoci"])} 不符')
        continue
    for b, y in zip(beats, h['yaoci']):
        if b.get('line') != y['line']:
            fails.append(f'{tag} 幕 {b.get("line", "?")} 与爻 {y["line"]} 错位')
        for k in ('title', 'shot', 'action', 'reason'):
            if not str(b.get(k, '')).strip():
                fails.append(f'{tag} {y["line"]} 幕缺 {k}')


# ---------------------------------------------------------------- en-phrases
if set(EP.get('LIGHT', {})) != LIGHTS:
    fails.append('[en] LIGHT 须覆盖四种光时')
for key in ('FOREGROUND', 'FARFADE'):
    if set(EP.get(key, {})) != TRIGRAMS:
        fails.append(f'[en] {key} 须覆盖八经卦')
for tbl in ('LIGHT', 'FOREGROUND', 'FARFADE'):
    for k, v in EP.get(tbl, {}).items():
        if not v.get('zh', '').strip() or not v.get('en', '').strip():
            fails.append(f'[en] {tbl}[{k}] 缺中/英短语')
en_tab = EP.get('EN', {})
missing = [h['no'] for h in H if str(h['no']) not in en_tab]
if missing:
    fails.append(f'[en] EN 缺卦: {missing}')
for h in H:
    e = en_tab.get(str(h['no']), {})
    for k in ('creature', 'weather', 'terrain'):
        if not e.get(k, '').strip():
            fails.append(f"[en] 第{h['no']}卦{h['name']} 缺 {k}")


# ---------------------------------------------------------------- 汇总
n_checks = 5 + 4  # 分解五条 + 四份结构检查
print(f'检查 skill 数据:64 卦 + 8 境 + 64 幕表 + 英文短语库(分解五条验证 + {n_checks - 5} 组结构检查)')
print('=' * 62)
print(f'不通过 {len(fails)} 项')
print('=' * 62)
for f in fails[:30]:
    print('  ✗', f)
if len(fails) > 30:
    print(f'  … 另有 {len(fails) - 30} 项')
if not fails:
    print('  ✓ 全部验收项通过')
sys.exit(1 if fails else 0)
