#!/usr/bin/env python3
"""
split_book.py — 依 cuts.txt 機械式切割書籍

用法：
  python scripts/split_book.py <書名> <cuts.txt> [--force] [--dry-run]

cuts.txt 格式（每行一個切割點，行號從 0 開始）：
  行號<TAB>標題
  45	第一章 數位轉型
  201	第二章 AI核心技術

輸出：
  wiki/raw/<書名>_0.md
  wiki/raw/<書名>_1.md
  ...

若 cuts.txt 含有 _SUB 標記，表示是二次切割的子段（由 LLM 標記）：
  45	第一章 數位轉型
  201	第二章 AI核心技術   _SUB:3
  245	第二章 AI核心技術（下）  _SUB:3
  →  <書名>_3.md, <書名>_3_1.md
（_SUB:N 表示此行屬於第 N 個主章節的二次切割子段）
"""

import sys
import re
import argparse
from pathlib import Path

OUT_DIR = Path('wiki/raw')


def parse_cuts(cuts_file: Path) -> list[dict]:
    """
    回傳 [{"line": int, "title": str, "sub": int|None}]
    sub=None  → 正常主章節
    sub=N     → 第 N 個主章節的二次切割子段
    """
    cuts = []
    for raw in cuts_file.read_text(encoding='utf-8').splitlines():
        raw = raw.strip()
        if not raw or raw.startswith('#'):
            continue
        # 解析 _SUB:N 標記
        sub = None
        sub_m = re.search(r'\s+_SUB:(\d+)\s*$', raw)
        if sub_m:
            sub = int(sub_m.group(1))
            raw = raw[:sub_m.start()]
        # 解析 行號<TAB>標題
        m = re.match(r'^(\d+)\t(.+)$', raw)
        if not m:
            print(f'[警告] 跳過無法解析的行：{raw!r}', file=sys.stderr)
            continue
        cuts.append({'line': int(m.group(1)), 'title': m.group(2).strip(), 'sub': sub})
    return cuts


def split(all_lines: list, cuts: list) -> list[dict]:
    """
    依切割點切分，回傳：
    [{"title": str, "lines": list, "start": int, "end": int, "sub": int|None}]
    """
    total = len(all_lines)
    valid = sorted(
        [c for c in cuts if 0 <= c['line'] < total],
        key=lambda x: x['line']
    )
    if not valid:
        return [{'title': '全文', 'lines': all_lines, 'start': 0, 'end': total, 'sub': None}]

    chunks = []
    # 第一個切割點前的序言
    if valid[0]['line'] > 0:
        chunks.append({'title': '序言', 'lines': all_lines[:valid[0]['line']],
                       'start': 0, 'end': valid[0]['line'], 'sub': None})

    for i, cut in enumerate(valid):
        start = cut['line']
        end   = valid[i + 1]['line'] if i + 1 < len(valid) else total
        chunks.append({'title': cut['title'], 'lines': all_lines[start:end],
                       'start': start, 'end': end, 'sub': cut['sub']})
    return chunks


def assign_filenames(book_name: str, chunks: list) -> list[dict]:
    """
    決定每個 chunk 的輸出檔名。
    sub=None → <書名>_N.md（N 遞增）
    sub=K    → <書名>_K_M.md（M 從 1 開始，K 固定）
    """
    result = []
    main_index = 0
    sub_counters = {}  # {K: 下一個 M}

    for chunk in chunks:
        if chunk['sub'] is None:
            filename = f'{book_name}_{main_index}.md'
            main_index += 1
        else:
            k = chunk['sub']
            m = sub_counters.get(k, 1)
            filename = f'{book_name}_{k}_{m}.md'
            sub_counters[k] = m + 1

        result.append({**chunk, 'filename': filename})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('book_name')
    parser.add_argument('cuts_file', help='cuts.txt 路徑')
    parser.add_argument('--force',   action='store_true', help='強制覆寫')
    parser.add_argument('--dry-run', action='store_true', help='只顯示計畫，不寫檔')
    parser.add_argument('--src-dir', default='book')
    parser.add_argument('--out-dir', default='wiki/raw')
    args = parser.parse_args()

    book_name = args.book_name
    out_dir   = Path(args.out_dir)

    # 來源檔
    candidates = [
        Path(args.src_dir) / book_name / f'{book_name}.md',
        Path(args.src_dir) / book_name / f'{book_name}.txt',
    ]
    src = next((p for p in candidates if p.exists()), None)
    if src is None:
        print('[錯誤] 找不到來源檔案', file=sys.stderr)
        sys.exit(1)

    # 防呆
    if not args.force and not args.dry_run:
        existing = list(out_dir.glob(f'{book_name}_*.md'))
        if existing:
            print(f'[攔截] {out_dir}/ 已存在 {len(existing)} 個同名切割檔。加 --force 覆寫。')
            sys.exit(0)

    # 讀取
    cuts_path = Path(args.cuts_file)
    if not cuts_path.exists():
        print(f'[錯誤] 找不到 cuts.txt：{cuts_path}', file=sys.stderr)
        sys.exit(1)

    cuts      = parse_cuts(cuts_path)
    all_lines = src.read_text(encoding='utf-8').splitlines()

    print(f'[來源] {src}（{len(all_lines)} 行）')
    print(f'[切割] {len(cuts)} 個切割點')

    chunks   = split(all_lines, cuts)
    named    = assign_filenames(book_name, chunks)

    # 顯示計畫
    print(f'\n{"="*60}')
    print(f'  切割計畫（共 {len(named)} 個區塊）')
    print(f'{"="*60}')
    for c in named:
        print(f"  {c['filename']:<30} {len(c['lines']):>5} 行  {c['title'][:40]}")
    print()

    if args.dry_run:
        print('[dry-run] 不寫出檔案。')
        return

    # 寫出
    for c in named:
        path = out_dir / c['filename']
        path.parent.mkdir(parents=True, exist_ok=True)
        content = '\n'.join(c['lines']) + '\n'
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ {path}")

    print(f'\n[完成] {len(named)} 個檔案 → {out_dir}/')


if __name__ == '__main__':
    main()
