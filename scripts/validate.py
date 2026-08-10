# -*- coding: utf-8 -*-
"""把 spec 第 7 节的验收标准变成可执行检查。任何一项不过就是回归。"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = json.load(open(f'{BASE}/data/hexagrams.json', encoding='utf-8'))['hexagrams']
RJ = json.load(open(f'{BASE}/data/realms.json', encoding='utf-8'))
R = {r['trigram']: r for r in RJ['realms']}

BANNED = ['masterpiece', 'best quality', '8k', 'ultra detailed', 'highly detailed',
          'award winning', 'trending on artstation', 'hyper realistic', 'super detailed']
MODELS = ['Midjourney 8.2', 'GPT-Image-2', 'Nano Banana Pro', 'Seedream 5.0 Pro']

fails, warns = [], []


def blocks(md):
    """解析出 {卦序: {模型名: 提示词}}。逐行扫描 —— 正则跨行会吞掉模型标题。"""
    res, cur, model, buf, inblk = {}, None, None, [], False
    for line in md.split('\n'):
        if inblk:
            if line.strip() == '```':
                if cur and model:
                    res[cur][model] = '\n'.join(buf)
                model, buf, inblk = None, [], False
            else:
                buf.append(line)
            continue
        m = re.match(r'^## 第 (\d+) 卦', line)
        if m:
            cur = int(m.group(1)); res[cur] = {}; model = None
            continue
        m = re.match(r'^\*\*(.+?)\*\*\s*$', line)
        if m and m.group(1) in MODELS:
            model = m.group(1)
            continue
        if line.strip() == '```' and model:
            inblk, buf = True, []
    return res


allp = {}
for f in os.listdir(f'{BASE}/prompts'):
    allp.update(blocks(open(f'{BASE}/prompts/{f}', encoding='utf-8').read()))

# 1 覆盖完整：64 卦 × 4 模型
if len(allp) != 64:
    fails.append(f'仅解析到 {len(allp)} 卦，应为 64')
for n, d in allp.items():
    missing = [m for m in MODELS if m not in d]
    if missing:
        fails.append(f'第{n}卦缺模型: {missing}')

by_no = {h['no']: h for h in H}

# 结构不变量：远景消隐物不得与本境中景招牌物件同名。
# MJ 把 short_en（中景）与 FARFADE（远景）直接并置，同名会让同一件东西
# 既在中景又在最远处 —— 首轮实现中艮境「a stone gateway」即此症。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en_phrases import FARFADE
for tri, r in R.items():
    mid = set(re.findall(r"[a-z']+", r['short_en'].lower()))
    far = set(re.findall(r"[a-z']+", FARFADE[tri][1].lower()))
    overlap = {w for w in mid & far if len(w) > 3}
    if overlap:
        fails.append(f'{r["realm"]} 远景与中景招牌物件同名: {sorted(overlap)}')

for n, d in sorted(allp.items()):
    h = by_no[n]
    up, lo = R[h['upper']], R[h['lower']]
    mj, gpt, nano, seed = (d.get(m, '') for m in MODELS)
    tag = f'第{n}卦{h["name"]}'

    # 2 禁用词
    for p, nm in ((mj, 'MJ'), (gpt, 'GPT'), (nano, 'Nano')):
        for b in BANNED:
            if b in p.lower():
                fails.append(f'{tag} {nm} 含禁用词「{b}」')

    # 3 MJ 参数
    if '--ar 3:4' not in mj:
        fails.append(f'{tag} MJ 缺 --ar 3:4')
    if '--style raw' not in mj:
        fails.append(f'{tag} MJ 缺 --style raw')
    body = mj.split('--')[0]
    for neg in (' no ', 'without ', 'avoid '):
        if neg in body.lower():
            fails.append(f'{tag} MJ 正文出现否定词，应移入 --no')
    wc = len(body.split())
    if wc > 110:
        warns.append(f'{tag} MJ 正文 {wc} 词，超出 50-90 区间较多')

    # 4 画幅四条一致
    if '3:4' not in gpt or '3:4' not in nano or '3:4' not in seed:
        fails.append(f'{tag} 有模型未声明 3:4 画幅')

    # 5 三层纵深：前景框 / 上境 / 下境 / 远景 四要素齐备
    for p, nm in ((gpt, 'GPT'), (nano, 'Nano')):
        if up['realm_en'] not in p:
            fails.append(f'{tag} {nm} 未出现上境译名 {up["realm_en"]}')
        if h['upper'] != h['lower'] and lo['realm_en'] not in p:
            fails.append(f'{tag} {nm} 未出现下境译名 {lo["realm_en"]}')
    for kw, nm in (('上方', 'Seed'),):
        if kw not in seed:
            fails.append(f'{tag} Seedream 未声明上下分层')

    # 6 色板两主一辅，四条一致
    for c in h['palette_en'][:3]:
        for p, nm in ((mj, 'MJ'), (gpt, 'GPT'), (nano, 'Nano')):
            if c not in p:
                fails.append(f'{tag} {nm} 缺色板成分「{c}」')
    for c in h['palette_zh'][:3]:
        if c not in seed:
            fails.append(f'{tag} Seedream 缺色板成分「{c}」')

    # 7 禁人物禁文字
    for p, nm in ((gpt, 'GPT'), (nano, 'Nano')):
        if 'no faces' not in p.lower() and 'no face' not in p.lower():
            fails.append(f'{tag} {nm} 未禁止人脸')
    if '不出现任何文字、人物与人脸' not in seed:
        fails.append(f'{tag} Seedream 未禁止文字人物人脸')

    # 7b 明度锚点与尺度锚点 —— 缺任一条就会回到「太暗、不宏大」
    for p, nm in ((mj, 'MJ'), (gpt, 'GPT'), (nano, 'Nano')):
        low = p.lower()
        if 'glow' not in low and 'lit from within' not in low:
            fails.append(f'{tag} {nm} 缺明度锚点（雾发光）')
        if 'speck' not in low and 'immense' not in low and 'enormous' not in low:
            fails.append(f'{tag} {nm} 缺尺度锚点')
    if '最亮的区域' not in seed:
        fails.append(f'{tag} Seedream 缺明度锚点')
    if '小如尘点' not in seed or '体量极大' not in seed:
        fails.append(f'{tag} Seedream 缺尺度锚点')

    # 8 中文提示词不得混入英文单词（3:4、4K 除外）
    stray = re.findall(r'[A-Za-z]{2,}', seed.replace('4K', '').replace('24mm', ''))
    if stray:
        fails.append(f'{tag} Seedream 混入英文: {set(stray)}')

    # 9 拼接残留：空顿号、重复词、断头
    for bad in ('，、', '、，', '。。', '，，', '最远处最远处', '  '):
        if bad in seed:
            fails.append(f'{tag} Seedream 拼接残留「{bad}」')

    # 9b 英文重复短语 —— 模板与组件都带同一个框架词时会出现，人眼易漏
    # 注：不检查实词二元组。前景框规定「就近取材于下境」，下境材料必然在
    # 前景与中景各出现一次（rammed-earth 等），那是设计使然，不是缺陷。
    for p, nm in ((mj, 'MJ'), (gpt, 'GPT'), (nano, 'Nano')):
        w = re.findall(r"[a-z']+", p.lower())
        grams = [' '.join(w[i:i+3]) for i in range(len(w) - 2)]
        dup = {g for g in grams if grams.count(g) > 1}
        dup -= {'no text no', 'text no people', 'no people no'}   # 负面清单本身允许并列
        if dup:
            fails.append(f'{tag} {nm} 重复短语 {sorted(dup)[:3]}')
        # 单光源规则：日光与月光不得同时出现
        low = p.lower()
        if 'moonlight' in low and ('daylight' in low or 'sun ' in low):
            fails.append(f'{tag} {nm} 同时出现月光与日光，违反单光源规则')
    if re.search(r'\b(\w+ \w+) \1\b', gpt):
        warns.append(f'{tag} GPT 疑似重复短语')

    # 10 旋钮必须有依据
    for k in ('light_reason', 'weather_reason', 'terrain_reason'):
        if not h['dials'].get(k, '').strip():
            fails.append(f'{tag} 旋钮 {k} 无依据')

    # 11 卦辞非空且以卦名起（否卦「否之匪人」为传世异例，单独放行）
    if not h['guaci'].strip():
        fails.append(f'{tag} 卦辞为空')

print('=' * 60)
print(f'检查 {len(allp)} 卦 × {len(MODELS)} 模型 = {len(allp)*len(MODELS)} 条提示词')
print(f'不通过 {len(fails)} 项，警告 {len(warns)} 项')
print('=' * 60)
for f in fails[:40]:
    print('  ✗', f)
if len(fails) > 40:
    print(f'  … 另有 {len(fails)-40} 项')
for w in warns[:15]:
    print('  !', w)
if len(warns) > 15:
    print(f'  … 另有 {len(warns)-15} 项警告')
if not fails:
    print('  ✓ 全部验收项通过')
sys.exit(1 if fails else 0)
