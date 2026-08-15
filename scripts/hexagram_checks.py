# -*- coding: utf-8 -*-
"""上下卦分解的独立验证（spec 4.4），供 validate.py 与 selftest.py 复用。

1. 八经卦各作上卦恰 8 次、作下卦恰 8 次
2. 卦画(lines)与上下卦分解一致 64/64（lines = 下卦三位 + 上卦三位，自下而上）
3. 64 卦画互异且穷尽 2^6
4. 32 对序卦全部满足反卦（上下颠倒）或错卦（阴阳全变）
5. 大象传物象与上下卦相符 64/64（如屯「雲，雷」、既濟「水在火上」）
"""
import collections

# 八卦三位（自下而上，1 阳 0 阴）
TRIGRAM_BITS = {'乾': '111', '兌': '110', '離': '101', '震': '100',
                '巽': '011', '坎': '010', '艮': '001', '坤': '000'}


def verify_decomposition(hexagrams):
    """返回失败描述列表；空列表即全部通过。"""
    fails = []
    # 1. 八经卦各作上下卦恰 8 次
    upper_c = collections.Counter(h['upper'] for h in hexagrams)
    lower_c = collections.Counter(h['lower'] for h in hexagrams)
    for tri in '乾坤震巽坎離艮兌':
        if upper_c[tri] != 8:
            fails.append(f'上卦{tri}出现 {upper_c[tri]} 次，应为 8')
        if lower_c[tri] != 8:
            fails.append(f'下卦{tri}出现 {lower_c[tri]} 次，应为 8')
    # 2. 卦画与上下卦分解一致
    for h in hexagrams:
        expect = TRIGRAM_BITS[h['lower']] + TRIGRAM_BITS[h['upper']]
        if expect != h['lines']:
            fails.append(f"{h['no']}{h['name']} 卦画 {h['lines']} 与 {h['upper']}上{h['lower']}下 不符（应为 {expect}）")
    # 3. 64 卦画互异且穷尽 2^6
    lines = set(h['lines'] for h in hexagrams)
    if len(lines) != 64:
        fails.append(f'卦画去重后仅 {len(lines)} 种，应为 64')
    if lines != {format(i, '06b') for i in range(64)}:
        fails.append('卦画未穷尽 2^6 全部 64 种组合')
    # 4. 32 对序卦满足反卦或错卦
    by_no = {h['no']: h for h in hexagrams}

    def _rev(s):
        return s[::-1]

    def _comp(s):
        return ''.join('1' if c == '0' else '0' for c in s)

    for odd in range(1, 64, 2):
        a, b = by_no[odd]['lines'], by_no[odd + 1]['lines']
        if b != _rev(a) and b != _comp(a):
            fails.append(f'序卦对 {odd}/{odd + 1} 既非反卦也非错卦')
    # 5. 大象传物象与上下卦相符
    wuxiang = {'乾': '天', '坤': '地', '震': '雷', '巽': '風木',
               '坎': '水雲雨泉', '離': '火明電', '艮': '山', '兌': '澤'}
    for h in hexagrams:
        dx = h['daxiang']
        up_ok = any(c in dx for c in wuxiang[h['upper']])
        lo_ok = any(c in dx for c in wuxiang[h['lower']])
        if not (up_ok and lo_ok):
            fails.append(f"{h['no']}{h['name']} 大象「{dx[:14]}…」与 {h['upper']}上{h['lower']}下不符")
    return fails
