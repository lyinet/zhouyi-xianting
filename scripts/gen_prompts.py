# -*- coding: utf-8 -*-
"""由 data/hexagrams.json + realms.json + en_phrases.py 生成两套提示词。

  prompts/       3:4 竖版，小红书发布用
  prompts-wide/  16:9 横版，封面与视觉冲击用

提示词是派生产物 —— 改画幅、换模型、扩到爻图都重跑此脚本，不重写内容。

宏大感的来源是**留白**，不是把画面填满：建筑约占三成，天空与云海占七成。
首版把上下两境铺满整幅，空间感被挤没了，这是第二轮返工的根因。
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

FIGURES_EN = ('three tiny robed figures at the balustrade, one in orange, '
              'far too small for any facial feature')
FIGURES_ZH = '三个极小的袍服人影立在栏边，其中一人着橙红衣袍，此尺寸下五官不成像'


def halves(s, sep):
    parts = [p for p in s.split(sep) if p]
    mid = (len(parts) + 1) // 2
    return sep.join(parts[:mid]), sep.join(parts[mid:]) or sep.join(parts[:mid])


def cap(s):
    return s[0].upper() + s[1:] if s else s


def bare(s):
    """去掉境名的定冠词 —— 用在 a second ... 之后时冠词会叠。"""
    return s[4:] if s.startswith("the ") else s


def first(s):
    return s.split(',')[0]


def build(h, aspect):
    """aspect: '3:4' 竖版走垂直落差，'16:9' 横版走地平线远眺。"""
    up, lo = R[h['upper']], R[h['lower']]
    pure = h['upper'] == h['lower']
    lz, le = LIGHT[h['dials']['light']]
    dz, de = FARFADE[h['upper']]
    c_en, w_en, t_en = EN[h['no']]
    pz, pe = h['palette_zh'], h['palette_en']
    cr = h['creature']
    c_zh = f"{cr['count']}只{cr['kind']}，{cr['state']}"
    t_zh = h['dials']['terrain_reason']

    # 上境远看其形（elements），下境是脚下的台地、近看其雕（ornament）。
    # 这既符合摄影逻辑，也彻底消除了下境在「远低处」与「前景」两处重复描述的问题。
    if pure:
        up_zh = f"{up['realm']}，{up['elements_zh']}"
        lo_zh = f"同一{lo['realm']}的下一层平台"
        up_en = f"{up['realm_en']}, {up['elements_en']}"
        lo_en = f"a lower tier of the same realm"
    else:
        up_zh, lo_zh = f"{up['realm']}，{up['elements_zh']}", lo['realm']
        up_en, lo_en = f"{up['realm_en']}, {up['elements_en']}", lo['realm_en']

    if aspect == '3:4':
        mj_frame = 'eye level, horizon low'
        mj_stack = (f"{up['short_en']} floating free past the top edge, "
                    f"the viewer standing on a terrace far below")
        gpt_frame = ('a vertical 3:4 frame, camera at eye level with the horizon set low. '
                     'The grandeur here is vertical — great height above, a long drop below')
        gpt_stack = (f"High above, {up_en}, floating free "
                     f"with no ground beneath it, so large it continues past the top edge. The "
                     f"camera stands far below on {lo_en}, itself a platform floating in open air")
        zh_frame = '3:4 竖构图，平视，地平线压在画面下部。宏大靠垂直落差：上有极高，下有深坠'
        zh_stack = (f"{up_zh}，整座悬空不着地，高踞画面上部并冲出顶端；"
                    f"镜头站在远低处的{lo_zh}上，那也是一座浮在空中的平台")
        par = '--ar 3:4'
    else:
        mj_frame = 'eye level, horizon just below centre'
        mj_stack = (f"{up['short_en']} floating in the upper third to one side, "
                    f"the viewer standing on a terrace across the cloud sea")
        gpt_frame = ('an ultrawide 16:9 frame, camera at eye level with the horizon just below '
                     'centre. The grandeur here is lateral — width, and distance measured '
                     'sideways')
        gpt_stack = (f"In the upper third and set to one side, {up_en}, floating free with no "
                     f"ground beneath it. The camera stands across the cloud sea on {lo_en}, "
                     f"itself a platform floating in open air")
        zh_frame = '16:9 超宽横构图，平视，地平线略低于画面中线。宏大靠横向：云海一路铺到极远的地平线'
        zh_stack = (f"{up_zh}，悬空不着地，位于画面上三分之一并偏向一侧；"
                    f"镜头站在云海另一端的{lo_zh}上，那也是一座浮在空中的平台")
        par = '--ar 16:9'

    # MJ 靠密集名词短语工作，超 100 词后新增词几乎不起作用，故只保留最强的
    # 几个装置：留白、地平线、前景浮雕、巨瀑、人影尺度。远景第二座建筑与
    # 地平线带细节留给 GPT/Nano 两条，它们不受词数约束。
    mj = (f"{mj_frame}, {mj_stack}, vast empty sky between, cloud sea to a far horizon, {lo['ornament_en'].split(', ')[0]} sunlit razor-sharp foreground, "
          f"a colossal waterfall falling into cloud, three tiny robed figures for scale, {le}, {first(w_en)}, {pe[0]} and {pe[1]} with {pe[2]} accents, "
          f"photoreal cinematic still, immense scale, glowing air "
          f"{par} --v 8.2 --style raw --stylize 250 --chaos 5 "
          f"--no text, watermark, crowds, close-up faces, modern objects, crushed blacks")

    gpt = (f"A photoreal cinematic still in {gpt_frame}.\n\n"
           f"{gpt_stack}.\n\n"
           f"**Most of this picture is empty.** Open sky and an unbroken cloud sea running to a "
           f"distant horizon should occupy roughly two thirds of the frame; the architecture "
           f"occupies about a third. That emptiness is what makes the scene vast — do not fill it.\n\n"
           f"In the near foreground, sunlit and rendered in razor-sharp high relief: "
           f"{lo['ornament_en']}. This is the densest detail in the picture — never a dark "
           f"silhouette. A colossal waterfall pours off the platform edge and falls into cloud "
           f"with no visible bottom.\n\n"
           f"For scale, place {FIGURES_EN}, and near the horizon a second, far smaller "
           f"{bare(up['realm_en'])}, tiny with distance. Along the horizon band, {de}.\n\n"
           f"The directional light is {le}. {cap(w_en)}. {cap(t_en)}. Keep the exposure bright "
           f"and luminous, the air glowing, shadows open and full of detail rather than crushed.\n\n"
           f"Also present, small and far off: {c_en}.\n\n"
           f"Palette: {pe[0]} and {pe[1]}, with {pe[2]} only as an accent.\n\n"
           f"Leave the top strip relatively empty for a later title. Do not render text or "
           f"calligraphy. No crowds, no close-up faces, no watermark, no modern objects.")

    nano = (f"Photograph this in {gpt_frame}.\n\n"
            f"{gpt_stack}.\n\n"
            f"Give most of the picture away to nothing — open sky and a cloud sea running "
            f"unbroken to a far horizon should take about two thirds of the frame. The buildings "
            f"take the remaining third. It is the emptiness that makes this feel enormous, so "
            f"resist filling it.\n\n"
            f"Right at the front, in full light and cut sharp enough to count the tool marks: "
            f"{lo['ornament_en']}. This is where the detail lives. Off the edge of the platform "
            f"a vast waterfall drops away and is swallowed by cloud before it ever lands.\n\n"
            f"Put {FIGURES_EN} — they are there to tell you how big everything else is. Near the "
            f"horizon, a second {bare(up['realm_en'])}, so far away it is almost a speck. Along the horizon, {de}.\n\n"
            f"{cap(le)} gives the scene its direction. {cap(w_en)}. {cap(t_en)}. Expose bright, "
            f"let the air glow, keep the shadows open. Somewhere far off, {c_en}.\n\n"
            f"Hold the colour to {pe[0]} and {pe[1]}, with {pe[2]} only as an accent. "
            f"No text, no crowds, no close-up faces.")

    seed = (f"{zh_frame}。{zh_stack}。"
            f"两者之间是一整片开阔的天空，云海一路铺展到极远的地平线——"
            f"天空与云海约占画面三分之二，建筑只占三分之一，留白正是宏大的来源，切勿填满。"
            f"近景是受光的精细浮雕，锐利到能看清凿痕：{lo['ornament_zh']}，这是全画细节最密处，不是黑剪影。"
            f"一道巨瀑自平台边缘倾泻而下，落入云中不见底。"
            f"{FIGURES_ZH}，用来对照建筑之巨；地平线附近另有一座极小的{up['realm']}，远得几乎成点；"
            f"地平线一带是{dz}。"
            f"{lz}，为画面的主光方向。{h['dials']['weather']}。{t_zh}。"
            f"整体明亮通透，空气发光，暗部开放有细节，不压死黑。"
            f"另有{c_zh}，在远处很小。"
            f"色调以{pz[0]}与{pz[1]}为主，仅以{pz[2]}点缀。"
            f"照相写实电影剧照质感，体量极大，纵深宏阔，细腻微观细节，轻微胶片颗粒，4K 超清。"
            f"顶部留白供后期排字。画面中不出现任何文字、人群与近景面孔。")

    return mj, gpt, nano, seed


def emit(aspect, outdir):
    os.makedirs(f'{BASE}/{outdir}', exist_ok=True)
    total, lens = 0, []
    for tri in ORDER:
        rows = sorted([h for h in H if h['upper'] == tri], key=lambda x: x['no'])
        realm = R[tri]
        out = [f"# 上卦 {tri}（{realm['symbol']} {realm['element']}）· {realm['realm']} "
               f"{realm['realm_en']} — {aspect}\n",
               f"本组 {len(rows)} 卦共享同一上境。发布顺序按序卦，非本文件顺序。\n"]
        for h in rows:
            mj, gpt, nano, seed = build(h, aspect)
            lens.append(len(mj.split('--')[0].split()))
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
        open(f'{BASE}/{outdir}/upper-{PY[tri]}.md', 'w', encoding='utf-8').write('\n'.join(out))
    return total, lens


for aspect, outdir in (('3:4', 'prompts'), ('16:9', 'prompts-wide')):
    n, lens = emit(aspect, outdir)
    print(f'{outdir}/  {aspect}  {n} 卦 × 4 模型 = {n*4} 条   '
          f'MJ 词数 min={min(lens)} max={max(lens)} avg={sum(lens)//len(lens)}')
