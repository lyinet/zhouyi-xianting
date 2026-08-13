# -*- coding: utf-8 -*-
"""把 spec 第 7 节的验收标准变成可执行检查。任何一项不过就是回归。

检查两套输出：prompts/（3:4）与 prompts-wide/（16:9）。
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = json.load(open(f'{BASE}/data/hexagrams.json', encoding='utf-8'))['hexagrams']
RJ = json.load(open(f'{BASE}/data/realms.json', encoding='utf-8'))
R = {r['trigram']: r for r in RJ['realms']}

BANNED = ['masterpiece', 'best quality', '8k', 'ultra detailed', 'highly detailed',
          'award winning', 'trending on artstation', 'hyper realistic', 'super detailed']
MODELS = ['Midjourney 8.2', 'GPT-Image-2', 'Nano Banana Pro', 'Seedream 5.0 Pro']
VARIANTS = [('prompts', '3:4'), ('prompts-wide', '16:9')]

STOP = {'the','a','an','of','in','on','at','and','with','into','from','its','it','is',
        'as','by','to','for','that','this','their','own','every','all','no','not','so',
        'only','small','far','near','up','down','out','back','but','be','are','then',
        'one','two','three','both','each','half','upper','lower','frame','picture','there',
        'across','beneath','above','below','over','under','itself','them','they','you','here'}

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


# 结构不变量：远景消隐物不得与本境中景招牌物件同名。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en_phrases import FARFADE
for tri, r in R.items():
    mid = set(re.findall(r"[a-z']+", r['short_en'].lower()))
    far = set(re.findall(r"[a-z']+", FARFADE[tri][1].lower()))
    overlap = {w for w in mid & far if len(w) > 3}
    if overlap:
        fails.append(f'{r["realm"]} 远景与中景招牌物件同名: {sorted(overlap)}')

by_no = {h['no']: h for h in H}
grand = 0

for outdir, aspect in VARIANTS:
    allp = {}
    for f in sorted(os.listdir(f'{BASE}/{outdir}')):
        allp.update(blocks(open(f'{BASE}/{outdir}/{f}', encoding='utf-8').read()))
    if len(allp) != 64:
        fails.append(f'[{aspect}] 仅解析到 {len(allp)} 卦，应为 64')
    grand += len(allp) * len(MODELS)

    for n, dd in sorted(allp.items()):
        h = by_no[n]
        up, lo = R[h['upper']], R[h['lower']]
        missing = [m for m in MODELS if m not in dd]
        if missing:
            fails.append(f'[{aspect}] 第{n}卦缺模型: {missing}')
            continue
        mj, gpt, nano, seed = (dd[m] for m in MODELS)
        tag = f'[{aspect}] 第{n}卦{h["name"]}'

        for p, nm in ((mj, 'MJ'), (gpt, 'GPT'), (nano, 'Nano')):
            low = p.lower()
            for b in BANNED:
                if b in low:
                    fails.append(f'{tag} {nm} 含禁用词「{b}」')
            # 明度锚点
            if 'glow' not in low:
                fails.append(f'{tag} {nm} 缺明度锚点')
            # 尺度锚点：极小人影 + 巨瀑
            if 'figures' not in low:
                fails.append(f'{tag} {nm} 缺人影尺度锤')
            if 'waterfall' not in low:
                fails.append(f'{tag} {nm} 缺巨瀑尺度装置')
            # 留白锚点 —— 宏大的真正来源
            if 'empty' not in low and 'emptiness' not in low:
                fails.append(f'{tag} {nm} 缺留白锚点')
            # 地平线与悬空
            if 'horizon' not in low:
                fails.append(f'{tag} {nm} 缺地平线')
            if 'float' not in low:
                fails.append(f'{tag} {nm} 缺悬空')
            # 重复短语：只看实词占多数的三元组，虚词组合是噪声。
            # 上境名会故意重复一次（远处还有一座同样的境），予以放行。
            w = re.findall(r"[a-z']+", low)
            grams = [' '.join(w[i:i+3]) for i in range(len(w) - 2)]
            realm_words = set(re.findall(r"[a-z']+", up['realm_en'].lower())) | \
                          set(re.findall(r"[a-z']+", lo['realm_en'].lower()))
            dup = set()
            for g in grams:
                if grams.count(g) < 2:
                    continue
                gw = g.split()
                if sum(1 for x in gw if x not in STOP) < 2:
                    continue                      # 虚词为主，噪声
                if all(x in realm_words | STOP for x in gw):
                    continue                      # 境名重复，设计使然
                dup.add(g)
            if dup:
                fails.append(f'{tag} {nm} 重复短语 {sorted(dup)[:3]}')
            if 'moonlight' in low and ('daylight' in low or 'sun ' in low):
                fails.append(f'{tag} {nm} 同时出现月光与日光，违反单光源规则')

        # MJ 参数与词数
        if f'--ar {aspect}' not in mj:
            fails.append(f'{tag} MJ 缺 --ar {aspect}')
        if '--style raw' not in mj:
            fails.append(f'{tag} MJ 缺 --style raw')
        body = mj.split('--')[0]
        for neg in (' no ', 'without ', 'avoid '):
            if neg in body.lower():
                fails.append(f'{tag} MJ 正文出现否定词，应移入 --no')
        wc = len(body.split())
        if wc > 110:
            warns.append(f'{tag} MJ 正文 {wc} 词')

        # 上境译名与叠合方向
        for p, nm in ((gpt, 'GPT'), (nano, 'Nano')):
            if up['realm_en'] not in p:
                fails.append(f'{tag} {nm} 未出现上境译名 {up["realm_en"]}')
            if h['upper'] != h['lower'] and lo['realm_en'] not in p:
                fails.append(f'{tag} {nm} 未出现下境译名 {lo["realm_en"]}')

        # 色板两主一辅
        for c in h['palette_en'][:3]:
            for p, nm in ((mj, 'MJ'), (gpt, 'GPT'), (nano, 'Nano')):
                if c not in p:
                    fails.append(f'{tag} {nm} 缺色板成分「{c}」')
        for c in h['palette_zh'][:3]:
            if c not in seed:
                fails.append(f'{tag} Seedream 缺色板成分「{c}」')

        # 禁令
        for p, nm in ((gpt, 'GPT'), (nano, 'Nano')):
            if 'close-up faces' not in p.lower():
                fails.append(f'{tag} {nm} 未禁止近景面孔')
        for kw in ('不出现任何文字、人群与近景面孔', '留白正是宏大的来源',
                   '悬空不着地', '地平线', '巨瀑', '受光的精细浮雕', '空气发光'):
            if kw not in seed:
                fails.append(f'{tag} Seedream 缺「{kw}」')
        if aspect not in seed:
            fails.append(f'{tag} Seedream 未声明 {aspect} 画幅')

        # 中文提示词不得混入英文（4K 除外）
        stray = re.findall(r'[A-Za-z]{2,}', seed.replace('4K', ''))
        if stray:
            fails.append(f'{tag} Seedream 混入英文: {set(stray)}')
        for bad in ('，、', '、，', '。。', '，，', '  '):
            if bad in seed:
                fails.append(f'{tag} Seedream 拼接残留「{bad}」')

        # 旋钮依据与卦辞
        for k in ('light_reason', 'weather_reason', 'terrain_reason'):
            if not h['dials'].get(k, '').strip():
                fails.append(f'{tag} 旋钮 {k} 无依据')
        if not h['guaci'].strip():
            fails.append(f'{tag} 卦辞为空')

print('=' * 62)
print(f'检查 {len(VARIANTS)} 套画幅 × 64 卦 × {len(MODELS)} 模型 = {grand} 条提示词')
print(f'不通过 {len(fails)} 项，警告 {len(warns)} 项')
print('=' * 62)
for f in fails[:30]:
    print('  ✗', f)
if len(fails) > 30:
    print(f'  … 另有 {len(fails)-30} 项')
for w in warns[:8]:
    print('  !', w)
if len(warns) > 8:
    print(f'  … 另有 {len(warns)-8} 项警告')
if not fails:
    print('  ✓ 全部验收项通过')
sys.exit(1 if fails else 0)
