# -*- coding: utf-8 -*-
"""由 data/hexagrams.json + data/video.json + data/realms.json 生成视频提示词。

  video-prompts/     Seedance 2.5（制作笔记风格，中文）
  video-prompts-h3/  MiniMax H3（三字段 schema）

每个模型 × 2 种结构（一镜到底 / 六镜头分镜）× 2 种画幅（3:4 竖版 / 16:9 横版）
= 64 卦 × 2 模型 × 2 结构 × 2 画幅 = 512 条。提示词是派生产物，改数据重跑不重写。

去 AI 味三原则（详见 specs/2026-08-15-zhouyi-xianting-video-design.md）：
  1. 素材来源身份 = 高预算中式奇幻电影 35mm 胶片实拍
  2. 负面约束关闭 AI 默认审美（平滑运镜/商业调色/塑料材质/过度锐化）
  3. 每幕至多一个非完美事件；禁用抽象夸赞词（高级/电影感/唯美等）
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = json.load(open(f'{BASE}/data/hexagrams.json', encoding='utf-8'))['hexagrams']
V = json.load(open(f'{BASE}/data/video.json', encoding='utf-8'))['hexagrams']
RJ = json.load(open(f'{BASE}/data/realms.json', encoding='utf-8'))
R = {r['trigram']: r for r in RJ['realms']}
ACCENT = RJ['accent_by_light']

PY = {'乾': 'qian', '坤': 'kun', '震': 'zhen', '巽': 'xun', '坎': 'kan', '離': 'li', '艮': 'gen', '兌': 'dui'}
ORDER = ['乾', '兌', '離', '震', '巽', '坎', '艮', '坤']      # 先天八卦序
DURATION = 15  # 秒

# ---------------------------------------------------------------- 规则表

# 天候 → 环境声（与画面元素一一对应）
WEATHER_SOUND = {
    '晴': '高空风声清朗，檐铃偶响',
    '薄雾': '风声透过薄雾传来，檐铃隐约',
    '浓雾': '声音被浓雾压低，檐铃几乎不闻',
    '雨': '雨声连绵，檐滴成线',
    '雪': '万籁俱寂，落雪无声，偶有冰棱轻响',
    '罡风': '风声呼啸，经幡猎猎，檐铃急响',
}

# 水势地势 → 水声（即水的运动弧）
TERRAIN_SOUND = {
    '静': '水面偶有涟漪轻响',
    '上涨': '水声渐起，缓缓漫过石阶',
    '奔涌': '激流轰鸣，浪头相撞',
    '干涸': '泽底龟裂，唯余滴水回响',
}

# 光时 → 配乐基调（编钟/古琴/铜磬，中式仙庭音色）
LIGHT_MUSIC = {
    '拂晓': '一支清亮的编钟与古琴短句，疏朗初明',
    '正午': '编钟与古琴双声部，庄严恢宏，低音铺底',
    '薄暮': '古琴沉缓，音色带余晖之温',
    '夜': '古琴幽静低回，偶闻一声铜磬长鸣',
}

# 灵禽 → 鸣声
def creature_sound(h):
    cr = h['creature']
    if cr['kind'] == '白鹿':
        return '偶有鹿鸣，低沉悠远'
    n = cr['count']
    if n == 1:
        return '一声孤鹤鸣，清越而远'
    if n == 2:
        return '两鹤相和而鸣'
    if '惊' in cr['state'] or '四散' in cr['state']:
        return '鹤群惊鸣，此起彼伏'
    return '鹤群低鸣，声如潮涌'

# 负面约束（去 AI 味核心，写入每一条）
NEG_ZH = ('不要万向节式的平滑运镜，运镜要有机、有呼吸感；不要现代商业调色；'
          '不要塑料质感；不要过度锐化；不要文字、字幕、水印；不要近景人物与人脸')
NEG_H3 = ('no gimbal-smooth camera moves, organic breathing camera; '
          'no commercial colour grading, natural filmic colour; '
          'no plastic materials, real material texture; '
          'no over-sharpening, subtle film grain; no text, captions, watermarks; '
          'no close-up faces')

# 质感锚点（素材来源身份 = 35mm 奇幻电影实拍）
TEXTURE_ZH = ('35mm 胶片拍摄的高预算中式奇幻电影剧照质感，微胶片颗粒，'
              '真实材质——夯土粗糙颗粒、白玉温润、鎏金真实金属反射、青铜绿锈、朱漆旧痕；'
              '大气透视，纵深不少于四层；运动符合物理：云有惯性、水有重力、鹤有翅振、雾有密度')
TEXTURE_H3 = ('35mm film look from a high-budget Chinese fantasy film, subtle grain, '
              'real material texture, atmospheric perspective, physically correct motion')

# 抽象夸赞词黑名单（validate 使用）
BANNED_WORDS = ['高级', '电影感', '炸裂', '唯美', '震撼', '史诗', '惊艳', '大片',
                'epic', 'stunning', 'breathtaking', 'cinematic masterpiece']


# ---------------------------------------------------------------- 推导

def beat_time(i, n):
    """第 i 幕（0 起）在 n 幕中的起止秒数（用于 Seedance 分镜的秒数显示）。"""
    step = DURATION / n
    return round(i * step, 1), round((i + 1) * step, 1)


def beat_ms(i, n):
    """第 i 幕（0 起）起始时刻的整数毫秒（15s / n 幕，无浮点误差）。"""
    return round(i * DURATION * 1000 / n)


def fmt_ts(ms):
    """毫秒 → H3 时间戳 '00:SS.mmm'。"""
    return f'At 00:{ms // 1000:02d}.{ms % 1000:03d}'


def ambient_zh(h):
    return WEATHER_SOUND[h['dials']['weather_base']] + '；' + TERRAIN_SOUND[h['dials']['terrain']] + '；' + creature_sound(h)


def music_zh(h):
    return LIGHT_MUSIC[h['dials']['light']] + '。无对白、无歌词、无字幕'


def realm_line(h, realm_key):
    r = R[h[realm_key]]
    if h['upper'] == h['lower']:
        return f"{r['realm']}，{r['elements_zh']}"
    return r['realm']


def scene_zh(h):
    up, lo = R[h['upper']], R[h['lower']]
    if h['upper'] == h['lower']:
        return (f"同一座{up['realm']}的上下两层——{up['elements_zh']}，"
                f"下层平台亦是{lo['realm']}，整座悬空于云海之上")
    return (f"上方{up['realm']}——{up['elements_zh']}；"
            f"下方{lo['realm']}——{lo['elements_zh']}；两境之间云海贯通")


def frame_zh(aspect):
    if aspect == '3:4':
        return ('3:4 竖构图，平视远眺，地平线在画面中下部，宏大靠垂直落差：上有极高，下有深坠。'
                '顶部约五分之一留白供后期排卦名与卦辞，保持空旷')
    return ('16:9 超宽横构图，平视远眺，地平线略低于画面中线，宏大靠横向：云海一路铺到极远的地平线。'
            '顶部留白供后期排字，保持空旷')


def light_zh(h):
    d = h['dials']
    return (f"{d['light']}光时，{ACCENT[d['light']]['zh']}点缀色；{d['weather']}；"
            f"雾气本身被光点亮、是画面最亮区；整体明亮通透，暗部开放不压死黑")


def creature_zh(h):
    cr = h['creature']
    return f"{cr['count']}只{cr['kind']}，{cr['state']}"


# ---------------------------------------------------------------- Seedance 条

def seedance_prompt(h, v, aspect, structure):
    beats = v['beats']
    n = len(beats)
    cr = h['creature']
    lines = []
    lines.append('格式：图生视频，首帧为该卦静态图，' +
                 ('单镜头一镜到底' if structure == 'take' else f'分镜{len(beats)}镜头') +
                 f'，{DURATION}秒，{aspect}画幅。')
    lines.append('首帧：严格保留首帧的全部构成——上下两境的叠合方向、构图、色板、顶部留白，上下位置不得对调。')
    lines.append('主体与场景：' + scene_zh(h) + '。' + f"灵禽：{creature_zh(h)}。")
    lines.append(f"镜头：{v['camera']['shot']}，{v['camera']['move']}（{v['camera']['reason']}）。{frame_zh(aspect)}")
    lines.append(f"光：{light_zh(h)}。")
    lines.append(f"氛围：{h['dials']['weather']}；{h['dials']['terrain_reason']}。")
    if structure == 'take':
        seg = '；'.join(f"{b['title']}——{b['action']}" for b in beats)
        lines.append(f"动作弧（六爻六阶段，一镜内连续演化）：{seg}。")
    else:
        for i, b in enumerate(beats):
            t0, t1 = beat_time(i, n)
            lines.append(f"镜头{i + 1}（{t0:g}–{t1:g}秒，{b['shot']}）：{b['title']}——{b['action']}。")
    lines.append(f"质感：{TEXTURE_ZH}。")
    lines.append(f"音频：{ambient_zh(h)}。配乐：{music_zh(h)}。")
    lines.append(f"目标：捕捉「{h['name']}」卦此景（{v['time_arc']['note']}）的一瞬，仿佛一段高预算中式奇幻电影的实拍素材，以胶片颗粒、真实材质、物理运动、克制运镜、留白收尾。")
    lines.append(f"负面：{NEG_ZH}。")
    return '\n'.join(lines)


# ---------------------------------------------------------------- MiniMax H3 条

def h3_prompt(h, v, aspect, structure):
    beats = v['beats']
    n = len(beats)
    cr = h['creature']
    frame = '3:4 竖构图' if aspect == '3:4' else '16:9 超宽横构图'
    horizon = '地平线在画面中下部，宏大靠垂直落差' if aspect == '3:4' else '地平线略低于中线，宏大靠横向云海'
    scene = scene_zh(h)
    b0 = beats[0]
    shot1 = (f"[Shot 1] {frame}，平视远眺，{horizon}。{scene}。"
             f"{cr['count']}只{cr['kind']}，{cr['state']}。初幕{b0['title']}——{b0['action']}。{light_zh(h)}。"
             f"{TEXTURE_H3}。{NEG_H3}。顶部留白供后期排字，保持空旷。")
    if structure == 'take':
        # 一镜到底：单一 [Shot 1]，时间线用 At 00:xx.xxx 标记阶段，无剪辑语
        segs = [shot1]
        for i, b in enumerate(beats):
            if i == 0:
                continue
            segs.append(f"{fmt_ts(beat_ms(i, n))}, 连续长镜头内，{b['title']}——{b['action']}。")
        desc = '\n'.join(segs)
    else:
        # 六镜头分镜：每幕一镜，镜头间剪辑
        segs = [shot1]
        for i, b in enumerate(beats):
            if i == 0:
                continue
            segs.append(f"[Shot {i + 1}] {fmt_ts(beat_ms(i, n))}, the camera cuts to "
                        f"{b['shot']}。{b['title']}——{b['action']}。")
        desc = '\n'.join(segs)
    sound = f"overall_soundscape: {ambient_zh(h)}。无对白、无歌词。"
    music = f"non_diegetic_music: {LIGHT_MUSIC[h['dials']['light']]}。无对白。"
    return (f"I2VA: For the target video, at 0.00 seconds into the target video, "
            f"<Picture 1> (from [Shot 1]) is fully referenced.\n\n"
            f"integrated_multimodal_description:\n{desc}\n\n{sound}\n{music}")


# ---------------------------------------------------------------- 输出

def emit(aspect, outdir, model_fn, label):
    os.makedirs(f'{BASE}/{outdir}', exist_ok=True)
    total = 0
    for tri in ORDER:
        rows = sorted([h for h in H if h['upper'] == tri], key=lambda x: x['no'])
        realm = R[tri]
        out = [f"# 上卦 {tri}（{realm['symbol']} {realm['element']}）· {realm['realm']} — 视频提示词（{label}，{aspect}）\n",
               f"本组 {len(rows)} 卦共享同一上境。发布顺序按序卦，非本文件顺序。图生视频，首帧为该卦静态图。\n"]
        for h in rows:
            v = V[str(h['no'])]
            d = h['dials']
            out.append(f"\n---\n\n## 第 {h['no']} 卦 · {h['symbol']} {h['name']}"
                       f"（{h['upper']}上{h['lower']}下 · {h['upper_realm']}在上，{h['lower_realm']}在下）\n")
            out.append(f"> **卦辞** {h['guaci']}  \n> **大象** {h['daxiang']}\n")
            out.append(f"**旋钮** 光时 {d['light']}（{d['light_reason']}）· "
                       f"天候 {d['weather']}（{d['weather_reason']}）· "
                       f"水势 {d['terrain']}（{d['terrain_reason']}）  \n"
                       f"**时间弧** {v['time_arc']['note']}（{v['time_arc']['reason']}）  \n"
                       f"**色板** {' + '.join(h['palette_zh'])}　**灵禽** {creature_zh(h)}\n")
            out.append(f"\n**{label} · {'一镜到底' if outdir.endswith('take') else '六镜头分镜'}**\n\n```\n{model_fn(h, v, aspect, 'take' if outdir.endswith('take') else 'shots')}\n```\n")
            total += 1
        open(f'{BASE}/{outdir}/upper-{PY[tri]}.md', 'w', encoding='utf-8').write('\n'.join(out))
    return total


def main():
    combos = [
        # (aspect, structure, outdir, model_fn, label)
        ('3:4', 'take', 'video-prompts/vertical-take', seedance_prompt, 'Seedance 2.5'),
        ('3:4', 'shots', 'video-prompts/vertical-shots', seedance_prompt, 'Seedance 2.5'),
        ('16:9', 'take', 'video-prompts/wide-take', seedance_prompt, 'Seedance 2.5'),
        ('16:9', 'shots', 'video-prompts/wide-shots', seedance_prompt, 'Seedance 2.5'),
        ('3:4', 'take', 'video-prompts-h3/vertical-take', h3_prompt, 'MiniMax H3'),
        ('3:4', 'shots', 'video-prompts-h3/vertical-shots', h3_prompt, 'MiniMax H3'),
        ('16:9', 'take', 'video-prompts-h3/wide-take', h3_prompt, 'MiniMax H3'),
        ('16:9', 'shots', 'video-prompts-h3/wide-shots', h3_prompt, 'MiniMax H3'),
    ]
    grand = 0
    for aspect, structure, outdir, fn, label in combos:
        n = emit(aspect, outdir, fn, label)
        print(f'{outdir}/  {aspect} {structure}  {n} 卦 = {n} 条')
        grand += n
    print(f'合计 {grand} 条视频提示词')


if __name__ == '__main__':
    main()
