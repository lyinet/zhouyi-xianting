#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轻量单元测试（无第三方依赖，纯 assert）。

覆盖：上下卦分解验证、爻辞解析、视频时间戳。运行：
    python3 scripts/selftest.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetch_yaoci
import gen_video_prompts as gv
from hexagram_checks import verify_decomposition, TRIGRAM_BITS

H = json.load(open(f'{BASE}/data/hexagrams.json', encoding='utf-8'))['hexagrams']

passed, failed = 0, 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f'  ✓ {name}')
    else:
        failed += 1
        print(f'  ✗ {name}')


print('== 1. 上下卦分解验证 ==')
check('真实数据 64 卦全部通过', verify_decomposition(H) == [])

# 变异测试：把泰卦(11)的 lines 改错，必须被抓出
import copy
mut = copy.deepcopy(H)
for h in mut:
    if h['no'] == 11:
        h['lines'] = '000111'  # 泰 111000 → 改成否的卦画，与上下卦(坤上乾下)不符
check('变异(泰卦卦画错)被抓出', len(verify_decomposition(mut)) >= 1)

# 变异测试：把乾(1)的 upper 改成坤，破坏"各作上卦8次"
mut = copy.deepcopy(H)
for h in mut:
    if h['no'] == 1:
        h['upper'] = '坤'
check('变异(上卦计数破坏)被抓出', len(verify_decomposition(mut)) >= 1)


print('== 2. 爻辞解析 fetch_yaoci.parse_yaoci ==')
def cells(texts):
    return [t.replace(' ', '') for t in texts]

# 冒号标注 + 小象不带标签
c = cells(['泰：小往大來', '天地交泰', '初九：拔茅茹，以其彙，征吉。', '拔茅征吉，志在外也。',
           '九二：包荒，用馮河。', '包荒，得尚于中行。', '九三：无平不陂。', '无往不復，天地際也。',
           '六四：翩翩。', '翩翩不富，皆失實也。', '六五：帝乙歸妹。', '以祉元吉。', '上六：城復于隍。', '城復于隍，其命亂也。'])
y = fetch_yaoci.parse_yaoci(c)
check('冒号标注解析出 6 爻', len(y) == 6)
check('首爻为初九且文本正确', y[0]['line'] == '初九' and y[0]['text'] == '拔茅茹，以其彙，征吉。')
check('小象紧随爻辞', y[0]['xiaoxiang'] == '拔茅征吉，志在外也。')

# 逗号标注(咸卦)+ 小象以标签+逗号开头(用九) + 文言被排除
c = cells(['乾：元亨，利貞。', '天行健。', '初九：潛龍，勿用。', '潛龍勿用，陽在下也。',
           '九二：見龍在田。', '見龍在田，德施普也。', '九三：終日乾乾。', '終日乾乾，反復道也。',
           '九四：或躍在淵。', '或躍在淵，進无咎也。', '九五：飛龍在天。', '飛龍在天，大人造也。',
           '上九：亢龍有悔。', '亢龍有悔，盈不可久也。', '用九：見群龍无首，吉。', '用九，天德不可為首也。',
           '《文言》曰：元者，善之長也。', '初九曰：潛龍勿用，何謂也？'])
y = fetch_yaoci.parse_yaoci(c)
check('逗号/冒号混排 + 用九解析出 7 爻', len(y) == 7)
check('用九的小象(逗号开头)正确归位', y[6]['line'] == '用九' and y[6]['xiaoxiang'] == '用九，天德不可為首也。')
check('《文言》被排除', all('文言' not in x['text'] and '何謂' not in x['xiaoxiang'] for x in y))

# 咸卦逗号标注(爻辞本体以逗号分隔)
c = cells(['咸：亨，利貞。', '咸，感也。', '初六，咸其拇。', '咸其拇，志在外也。',
           '六二，咸其腓，凶，居吉。', '雖凶居吉，順不害也。', '九三，咸其股。', '咸其股，亦不處也。',
           '九四，貞吉，悔亡。', '貞吉悔亡，未感害也。', '九五，咸其脢。', '咸其脢，志末也。',
           '上六，咸其輔頰舌。', '咸其輔頰舌，滕口說也。'])
y = fetch_yaoci.parse_yaoci(c)
check('咸卦逗号标注 6 爻', len(y) == 6)
check('咸卦爻辞无前导逗号', y[0]['text'] == '咸其拇。')


print('== 3. 视频时间戳 gen_video_prompts ==')
check('6 幕 beat_ms(1)=2500ms', gv.beat_ms(1, 6) == 2500)
check('7 幕 beat_ms(2)=4286ms(15/7×2 精确取整)', gv.beat_ms(2, 7) == 4286)
check('fmt_ts(2500) = At 00:02.500', gv.fmt_ts(2500) == 'At 00:02.500')
check('fmt_ts(4286) = At 00:04.286', gv.fmt_ts(4286) == 'At 00:04.286')
# 无浮点误差：6 幕与 7 幕的时间戳毫秒均为整数、严格递增
for n in (6, 7):
    ts = [gv.beat_ms(i, n) for i in range(n)]
    check(f'{n} 幕时间戳严格递增且为正', all(a < b for a, b in zip(ts, ts[1:])) and ts[0] == 0)


print(f'\n结果：{passed} 通过，{failed} 失败')
sys.exit(1 if failed else 0)
