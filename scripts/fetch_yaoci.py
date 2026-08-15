#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 ctext.org 抓取 64 卦爻辞与小象,写入 data/hexagrams.json 的 yaoci 字段。

- 每卦 URL 取自该卦已有的 source 字段,确保抓的是同一页
- 解析:ctext 页面中"爻标签开头"(初九/九二/…/上六/用九/用六)的 ctext 单元格
  是爻辞,紧随其后的单元格是小象;《文言》等后续内容一律丢弃
- 交叉验证:页面首条必须与该卦已有 guaci 一致(防止抓到错页)
- 幂等:已有 yaoci 的卦跳过;--force 强制重抓
"""
import json
import os
import re
import sys
import time
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(BASE, 'data', 'hexagrams.json')

# 爻辞单元格:爻标签后紧跟冒号(如 "初九：潛龍，勿用。")。
# 小象常以爻标签开头(如 "六二之難，乘剛也。")但无冒号,故不以标签+冒号匹配;
# 《文言》引文形如 "初九曰、「潛龍勿用」..." 亦无冒号,天然排除。
LINE_RE = re.compile(r'^(初九|初六|九二|六二|九三|六三|九四|六四|九五|六五|上九|上六|用九|用六)[：:]')


def fetch(url, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0 (zhouyi-xianting research)'})
            return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


def parse_cells(html):
    cells = re.findall(
        r'<td class="ctext">\s*<div id="comm\d+"></div>(.*?)</td>', html, re.S)
    out = []
    for c in cells:
        txt = re.sub(r'<[^>]+>', '', c)
        txt = re.sub(r'\s+', '', txt).strip()
        if txt:
            out.append(txt)
    return out


def parse_yaoci(cells):
    """从 ctext 单元格序列中提取 {爻标签: {text, xiaoxiang}}。

    规则:爻标签开头的单元格是爻辞,紧随其后的单元格是其小象。
    爻辞本身可能以标签开头但内容包含重复标签(如九三),按第一处标签判定。
    """
    yaoci = []
    for i, cell in enumerate(cells):
        m = LINE_RE.match(cell)
        if not m:
            continue
        label = m.group(1)
        text = cell[len(label):].lstrip('：:').strip()
        xiaoxiang = ''
        if i + 1 < len(cells):
            nxt = cells[i + 1]
            # 小象:不以"标签+冒号"开头,非文言长段(文言以《开头或含曰、何謂等),长度受限
            if not LINE_RE.match(nxt) and not nxt.startswith('《') and len(nxt) < 60:
                xiaoxiang = nxt
        yaoci.append({'line': label, 'text': text, 'xiaoxiang': xiaoxiang})
    return yaoci


def norm(s):
    return re.sub(r'\s+', '', s)


def main():
    force = '--force' in sys.argv
    data = json.load(open(PATH, encoding='utf-8'))
    hexagrams = data['hexagrams']
    done, skipped, failed = 0, 0, []

    for h in hexagrams:
        if not force and h.get('yaoci'):
            skipped += 1
            continue
        url = h.get('source', '')
        if '/book-of-changes/' not in url:
            failed.append((h['name'], 'no source url'))
            continue
        try:
            html = fetch(url)
            cells = parse_cells(html)
            if not cells:
                failed.append((h['name'], 'empty page'))
                continue
            # 交叉验证:页面首条卦辞应与已有 guaci 一致
            page_guaci = cells[0]
            if norm(page_guaci) != norm(h['guaci']):
                failed.append((h['name'], f'guaci mismatch: {page_guaci} vs {h["guaci"]}'))
                continue
            yaoci = parse_yaoci(cells)
            n_lines = len(yaoci)
            # 六爻齐备;乾/坤可有第 7 条(用九/用六)
            if n_lines not in (6, 7):
                failed.append((h['name'], f'got {n_lines} lines'))
                continue
            # 验证标签序列合法:初九/初六 开头,严格递增
            labels = [y['line'] for y in yaoci]
            if labels[0] not in ('初九', '初六'):
                failed.append((h['name'], f'bad first label {labels[0]}'))
                continue
            for a, b in zip(labels, labels[1:]):
                if not label_gt(b, a):
                    failed.append((h['name'], f'bad label order {a}->{b}'))
                    break
            else:
                h['yaoci'] = yaoci
                done += 1
                print(f"OK  {h['no']:>2} {h['name']} ({url.split('/')[-2]}): {n_lines} 爻")
        except Exception as e:
            failed.append((h['name'], str(e)))
        time.sleep(0.4)

    json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n完成 {done} 卦,跳过 {skipped} 卦,失败 {len(failed)} 卦')
    for name, why in failed:
        print(f'  FAIL {name}: {why}')
    sys.exit(1 if failed else 0)


ORDER = ['初九', '初六', '九二', '六二', '九三', '六三', '九四', '六四',
         '九五', '六五', '上九', '上六', '用九', '用六']


def label_gt(a, b):
    return ORDER.index(a) > ORDER.index(b)


if __name__ == '__main__':
    main()
