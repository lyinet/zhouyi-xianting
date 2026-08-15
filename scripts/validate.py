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

# ==============================================================
# 视频提示词验收（specs/2026-08-15-zhouyi-xianting-video-design.md 第 6 节）
# ==============================================================
import collections as _collections

VIDEO = json.load(open(f'{BASE}/data/video.json', encoding='utf-8'))['hexagrams']
VIDEO_COMBOS = [  # (aspect, structure, outdir)
    ('3:4', 'take', 'video-prompts/vertical-take'),
    ('3:4', 'shots', 'video-prompts/vertical-shots'),
    ('16:9', 'take', 'video-prompts/wide-take'),
    ('16:9', 'shots', 'video-prompts/wide-shots'),
    ('3:4', 'take', 'video-prompts-h3/vertical-take'),
    ('3:4', 'shots', 'video-prompts-h3/vertical-shots'),
    ('16:9', 'take', 'video-prompts-h3/wide-take'),
    ('16:9', 'shots', 'video-prompts-h3/wide-shots'),
]
VBANNED_ZH = ['高级', '电影感', '炸裂', '唯美', '震撼', '史诗', '惊艳', '大片',
              '超清', '极致', '顶级']
VBANNED_EN = ['epic', 'stunning', 'breathtaking', 'masterpiece']
VNEG_ZH = ['万向节', '商业调色', '塑料质感', '过度锐化', '近景人物']
VNEG_EN = ['gimbal-smooth', 'commercial colour grading', 'plastic', 'over-sharpening',
           'close-up faces']


def vblocks(md):
    """解析出 {卦序: {模型+结构标签: 提示词}}。"""
    res, cur, label, inblk, buf = {}, None, None, False, []
    for line in md.split('\n'):
        if inblk:
            if line.strip() == '```':
                if cur and label:
                    res[cur][label] = '\n'.join(buf)
                label, buf, inblk = None, [], False
            else:
                buf.append(line)
            continue
        m = re.match(r'^## 第 (\d+) 卦', line)
        if m:
            cur = int(m.group(1)); res[cur] = {}
            continue
        m = re.match(r'^\*\*(Seedance 2\.5|MiniMax H3) · (一镜到底|六镜头分镜)\*\*\s*$', line)
        if m:
            label = f'{m.group(1)}|{m.group(2)}'
            continue
        if line.strip() == '```' and label:
            inblk, buf = True, []
    return res


def _check_seedance(p, n, h, v, structure, tag, aspect):
    for sec in ('格式：', '首帧：', '主体与场景：', '镜头：', '光：', '氛围：',
                '动作弧' if structure == 'take' else '镜头1（', '质感：', '音频：', '负面：'):
        if sec not in p:
            fails.append(f'{tag} Seedance 缺段落「{sec}」')
    low = p.lower()
    for w in VBANNED_ZH:
        if w in p:
            fails.append(f'{tag} 含抽象夸赞词「{w}」')
    for kw in VNEG_ZH:
        if kw not in p:
            fails.append(f'{tag} 缺负面约束「{kw}」')
    for kw in ('顶部', '留白', '胶片颗粒', '无对白', '文字'):
        if kw not in p:
            fails.append(f'{tag} 缺「{kw}」')
    if structure == 'shots':
        for i in range(1, len(v['beats']) + 1):
            if f'镜头{i}（' not in p:
                fails.append(f'{tag} 分镜缺镜头{i}')
    else:
        if '一镜内连续演化' not in p:
            fails.append(f'{tag} 一镜到底缺连续演化声明')


def _check_h3(p, n, h, v, structure, tag, aspect):
    for field in ('I2VA:', 'integrated_multimodal_description:', 'overall_soundscape:', 'non_diegetic_music:'):
        if field not in p:
            fails.append(f'{tag} H3 缺字段「{field}」')
    low = p.lower()
    for w in VBANNED_ZH + VBANNED_EN:
        if w in p.lower():
            fails.append(f'{tag} 含抽象夸赞词「{w}」')
    for kw in VNEG_EN:
        if kw not in low:
            fails.append(f'{tag} 缺负面约束「{kw}」')
    # 时间戳严格递增；[Shot 1] 无时间戳
    stamps = re.findall(r'At 00:(\d{2})\.(\d{3})', p)
    prev = -1.0
    for mm, ss in stamps:
        t = int(mm) + int(ss) / 1000.0
        if t <= prev:
            fails.append(f'{tag} 时间戳未递增: {t}')
        prev = t
    if re.search(r'\[Shot 1\]\s*At ', p):
        fails.append(f'{tag} [Shot 1] 不应带时间戳')
    if structure == 'shots':
        if 'the camera cuts to' not in low:
            fails.append(f'{tag} 分镜缺剪辑语')
        if '一镜到底' in p:
            fails.append(f'{tag} 分镜误写一镜到底')
    else:
        if 'the camera cuts to' in low:
            fails.append(f'{tag} 一镜到底不应出现剪辑语')
    if '顶部留白' not in p:
        fails.append(f'{tag} 缺顶部留白')


vgrand = 0
for aspect, structure, outdir in VIDEO_COMBOS:
    d = f'{BASE}/{outdir}'
    if not os.path.isdir(d):
        fails.append(f'[视频] 缺目录 {outdir}')
        continue
    allp = {}
    for f in sorted(os.listdir(d)):
        allp.update(vblocks(open(f'{d}/{f}', encoding='utf-8').read()))
    if len(allp) != 64:
        fails.append(f'[视频 {aspect} {structure}] 仅解析到 {len(allp)} 卦，应为 64')
    vgrand += len(allp)
    for n, dd in sorted(allp.items()):
        h = by_no[n]
        v = VIDEO[str(n)]
        model = 'H3' if outdir.startswith('video-prompts-h3') else 'Seedance'
        tag = f'[视频 {model} {aspect} {structure}] 第{n}卦{h["name"]}'
        if not dd:
            fails.append(f'{tag} 无提示词')
            continue
        p = list(dd.values())[0]
        if outdir.startswith('video-prompts-h3'):
            _check_h3(p, n, h, v, structure, tag, aspect)
        else:
            _check_seedance(p, n, h, v, structure, tag, aspect)
        # 两模型同源：六幕标题都应出现
        for b in v['beats']:
            if b['title'] not in p:
                fails.append(f'{tag} 缺六幕「{b["title"]}」')


print(f'检查视频 {vgrand} 条（64 卦 × 2 模型 × 2 结构 × 2 画幅）')
print('=' * 62)
print(f'检查 {len(VARIANTS)} 套画幅 × 64 卦 × {len(MODELS)} 模型 = {grand} 条提示词 + 视频 {vgrand} 条')
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
