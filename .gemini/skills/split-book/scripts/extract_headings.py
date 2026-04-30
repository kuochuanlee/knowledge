#!/usr/bin/env python3
"""
extract_headings.py — 從 Markdown 萃取標題與行號

用法：
  python scripts/extract_headings.py <書名> [--src-dir book] [--level-max N]

參數：
  --level-max N   只輸出層級 <= N 的標題（預設 6，即全部輸出）
                  建議第一輪分析時設 --level-max 2，過濾圖表、說明等雜訊

輸出（stdout）：
  # 書名：XXX
  # 總行數：3241
  # 標題數量：47
  # 格式：行號<TAB>層級<TAB>標題

  5	1	第一章 數位轉型
  23	2	1.1 背景說明
  ...

設計原則：
  - 純掃描，不呼叫任何 API
  - 輸出精簡，供 LLM 低成本閱讀後判斷切割點
"""

import sys
import re
import argparse
from pathlib import Path


def extract_headings(src_file: Path, level_max: int) -> tuple[list[dict], int]:
    """
    掃描 Markdown 檔案，回傳 (headings, total_lines)。
    只回傳層級 <= level_max 的標題。
    """
    lines = src_file.read_text(encoding='utf-8').splitlines()
    headings = []

    # Markdown 標題語法：# ~ ######
    md_heading = re.compile(r'^(#{1,6})\s+(.+)')

    # 中文章節標記（未加 # 的純文字行）
    zh_chapter = re.compile(r'^第[零〇一二三四五六七八九十百千\d]+[章篇部卷]')
    zh_section = re.compile(r'^第[零〇一二三四五六七八九十百千\d]+節')

    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue

        # 優先匹配 Markdown 標題語法
        m = md_heading.match(s)
        if m:
            level = len(m.group(1))
            if level <= level_max:
                headings.append({'line': i, 'level': level, 'title': m.group(2).strip()})
            continue

        # 匹配中文章篇部卷（視為 level 1）
        if zh_chapter.match(s):
            if 1 <= level_max:
                headings.append({'line': i, 'level': 1, 'title': s[:60]})
            continue

        # 匹配中文節（視為 level 2）
        if zh_section.match(s):
            if 2 <= level_max:
                headings.append({'line': i, 'level': 2, 'title': s[:60]})

    return headings, len(lines)


def main():
    parser = argparse.ArgumentParser(description='從 Markdown 書籍萃取標題清單')
    parser.add_argument('book_name', help='書名（對應 book/<書名>/<書名>.md）')
    parser.add_argument('--src-dir', default='book', help='來源根目錄（預設：book）')
    parser.add_argument(
        '--level-max',
        type=int,
        default=6,
        metavar='N',
        help='只輸出層級 <= N 的標題（預設：6，即全部）。第一輪分析建議設 2'
    )
    args = parser.parse_args()

    # 尋找來源檔案
    candidates = [
        Path(args.src_dir) / args.book_name / f'{args.book_name}.md',
        Path(args.src_dir) / args.book_name / f'{args.book_name}.txt',
    ]
    src = next((p for p in candidates if p.exists()), None)

    if src is None:
        print('[錯誤] 找不到來源檔案：', file=sys.stderr)
        for p in candidates:
            print(f'       {p}', file=sys.stderr)
        sys.exit(1)

    headings, total = extract_headings(src, args.level_max)

    # 輸出標頭資訊
    print(f'# 書名：{args.book_name}')
    print(f'# 總行數：{total}')
    print(f'# 標題數量：{len(headings)}（level <= {args.level_max}）')
    print(f'# 格式：行號<TAB>層級<TAB>標題')
    print()

    if not headings:
        print('# [警告] 未偵測到任何標題，請確認檔案是否有 Markdown 標題（#）或中文章節標記。')
        sys.exit(0)

    for h in headings:
        print(f"{h['line']}\t{h['level']}\t{h['title']}")


if __name__ == '__main__':
    main()
