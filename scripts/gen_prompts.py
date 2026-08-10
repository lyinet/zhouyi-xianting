# -*- coding: utf-8 -*-
"""由 data/hexagrams.json + realms.json + en_phrases.py 生成 prompts/upper-*.md。

提示词是派生产物，不是手写散件 —— 改画幅、换模型、扩到爻图都重跑此脚本，
不重写内容。四条提示词同源：主体、光源方向、三层纵深、色板、画幅一致。

组件词库存裸短语，框架词（唯一光源／最远处／近景）只在此处添加一次。
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en_phrases import LIGHT, FOREGROUND, FARFADE, EN

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = json.load(open(f'{BASE}/data/hexagrams.json', encoding='utf-8'))['hexagrams']
RJ = json.load(open(f'{BASE}/data/realms.json', encoding='utf-8'))
R = {r['trigram']: r for r in RJ['realms']}

PY = {'乾':'qian','坤':'kun','震':'zhen','巽':'xun','坎':'kan','離':'li','艮':'gen','兌':'dui'}
ORDER = ['乾', '兌', '離', '震', '巽', '坎', '艮', '坤']      # 先天八卦序


def halves(s, sep):
    """把要素串对半分：纯卦时上境用前半、下境用后半，避免同一句重复两遍。"""
    parts = [p for p in s.split(sep) if p]
    mid = (len(parts) + 1) // 2
    return sep.join(parts[:mid]), sep.join(parts[mid:]) or sep.join(parts[:mid])


def cap(s):
    return s[0].upper() + s[1:] if s else s


def realm_phrases(h):
    """返回 (上境中, 下境中, 上境英, 下境英)，纯卦走双重叠加分支。"""
    up, lo = R[h['upper']], R[h['lower']]
    if h['upper'] == h['lower']:
        zh_a, zh_b = halves(up['elements_zh'], '、')
        en_a, en_b = halves(up['elements_en'], ', ')
        return (f"{up['realm']}层层向上叠加，{zh_a}",
                f"同一{lo['realm']}向下层层延伸，{zh_b}",
                f"{up['realm_en']} stacked tier upon tier, {en_a}",
                f"the same realm continuing downward, {en_b}")
    return (f"{up['realm']}，{up['elements_zh']}",
            f"{lo['realm']}，{lo['elements_zh']}",
            f"{up['realm_en']}, {up['elements_en']}",
            f"{lo['realm_en']}, {lo['elements_en']}")


def short(s, sep, n=2):
    return sep.join([p for p in s.split(sep) if p][:n])


def build(h):
    up, lo = R[h['upper']], R[h['lower']]
    up_zh, lo_zh, up_en, lo_en = realm_phrases(h)
    lz, le = LIGHT[h['dials']['light']]
    fz, fe = FOREGROUND[h['lower']]
    dz, de = FARFADE[h['upper']]
    c_en, w_en, t_en = EN[h['no']]
    pz, pe = h['palette_zh'], h['palette_en']
    cr = h['creature']
    c_zh = f"{cr['count']}只{cr['kind']}，{cr['state']}"
    d = h['dials']
    # 水势在提示词里用描述句（terrain_reason），裸标签只作分类用
    t_zh = d['terrain_reason']

    # MJ 不用「天阙」这类自造专名 —— 图像模型不认识它，只白占词数。
    # 专名的作用是人读与系列一致性，那由 GPT/Nano 两条承担。
    if h['upper'] == h['lower']:
        mj_up = f"{up['short_en']}, tier upon tier"
        mj_lo = "the same realm continuing"
    else:
        mj_up, mj_lo = up['short_en'], lo['short_en']
    first = lambda s: s.split(',')[0]

    mj = (f"vertical low-angle composition, {mj_up} in the upper half, {mj_lo} in the lower half, "
          f"{fe} in dark silhouette across the near edge, {de} fading out at the far distance, "
          f"{le}, {first(w_en)}, {first(t_en)}, {first(c_en)}, small and distant, "
          f"{pe[0]} and {pe[1]} with {pe[2]} accents, photoreal cinematic still, "
          f"atmospheric perspective, fine micro-detail, subtle grain "
          f"--ar 3:4 --v 8.2 --style raw --stylize 250 --chaos 5 "
          f"--no text, watermark, people, faces, modern objects")

    gpt = (f"A photoreal cinematic still in a vertical 3:4 frame, shot from a low angle.\n\n"
           f"Three depth layers. Upper half: {up_en}. Lower half, directly beneath it: {lo_en}. "
           f"Near foreground: {fe} crossing the near edge, almost black, framing the composition. "
           f"Far distance: nothing but {de}, dissolving into the air.\n\n"
           f"The only light source is {le}. {cap(w_en)}. {cap(t_en)}.\n\n"
           f"Place {c_en} — small in the frame and far from the camera.\n\n"
           f"Palette: {pe[0]} and {pe[1]}, with {pe[2]} only as an accent.\n\n"
           f"Leave the top fifth of the frame relatively empty for a later title. "
           f"Do not render text or calligraphy. No human figures, no faces, no watermark, "
           f"no modern objects.")

    nano = (f"Photograph this from a low angle in a vertical 3:4 frame.\n\n"
            f"Closest to the camera, {fe} crosses the near edge, almost black, framing everything "
            f"behind it. Above, the top half of the picture is {up_en}. Beneath it, the bottom half "
            f"is {lo_en}. Furthest back, nothing remains but {de}, dissolving into the air.\n\n"
            f"{cap(le)} is the only thing lighting the scene. {cap(w_en)}. {cap(t_en)}. "
            f"Somewhere small and far off, {c_en}.\n\n"
            f"Hold the colour to {pe[0]} and {pe[1]}, letting {pe[2]} appear only as an accent. "
            f"Deep atmospheric perspective, fine micro-detail, a little grain. "
            f"No text, no people, no faces.")

    seed = (f"{up_zh}，占据画面上方；{lo_zh}，占据画面下方。"
            f"近景{fz}，几乎全黑，压住画面下缘；最远处{dz}几乎完全消融在天光里。"
            f"{lz}，为画面唯一光源。{d['weather']}。{t_zh}。"
            f"远景有{c_zh}，在画面中很小。"
            f"色调以{pz[0]}与{pz[1]}为主，仅以{pz[2]}点缀。"
            f"照相写实电影剧照质感，强烈大气透视，细腻微观细节，轻微胶片颗粒。"
            f"3:4 竖构图，顶部约五分之一留白，4K 超清。画面中不出现任何文字、人物与人脸。")

    return mj, gpt, nano, seed


os.makedirs(f'{BASE}/prompts', exist_ok=True)
total = 0
mj_lens = []
for tri in ORDER:
    rows = sorted([h for h in H if h['upper'] == tri], key=lambda x: x['no'])
    realm = R[tri]
    out = [f"# 上卦 {tri}（{realm['symbol']} {realm['element']}）· {realm['realm']} {realm['realm_en']}\n",
           f"本组 {len(rows)} 卦共享同一上境，{realm['realm']} 的渲染描述批内复用。\n",
           f"发布顺序按序卦，非本文件顺序。\n"]
    for h in rows:
        mj, gpt, nano, seed = build(h)
        mj_lens.append(len(mj.split('--')[0].split()))
        d = h['dials']
        out.append(f"\n---\n\n## 第 {h['no']} 卦 · {h['symbol']} {h['name']}"
                   f"（{h['upper']}上{h['lower']}下 · {h['upper_realm']}在上，{h['lower_realm']}在下）\n")
        out.append(f"> **卦辞** {h['guaci']}  \n> **大象** {h['daxiang']}\n")
        out.append(f"**旋钮** 光时 {d['light']}（{d['light_reason']}）· "
                   f"天候 {d['weather']}（{d['weather_reason']}）· "
                   f"水势 {d['terrain']}（{d['terrain_reason']}）  \n"
                   f"**色板** {' + '.join(h['palette_zh'])}　**灵禽** {h['creature']['count']}只"
                   f"{h['creature']['kind']}，{h['creature']['state']}\n")
        for label, body in (('Midjourney 8.2', mj), ('GPT-Image-2', gpt),
                            ('Nano Banana Pro', nano), ('Seedream 5.0 Pro', seed)):
            out.append(f"\n**{label}**\n\n```\n{body}\n```\n")
        total += 1
    open(f'{BASE}/prompts/upper-{PY[tri]}.md', 'w', encoding='utf-8').write('\n'.join(out))
    print(f'  prompts/upper-{PY[tri]}.md  {len(rows)} 卦')
print(f'共 {total} 卦 × 4 模型 = {total*4} 条提示词')
print(f'MJ 正文词数 min={min(mj_lens)} max={max(mj_lens)} avg={sum(mj_lens)//len(mj_lens)}')
