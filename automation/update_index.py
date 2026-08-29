#!/usr/bin/env python3
"""site/index.htmlの記事一覧に、まだ載っていないsite/articles/*.htmlを追記する。

冪等: 既に<!-- ARTICLE_LIST_START -->〜<!-- ARTICLE_LIST_END -->の間に
リンクされているファイルはスキップするため、追加すべき新規記事がなければ
index.htmlは一切書き換えない(diffなし)。マーカーが見つからない場合は
ファイルを壊さず、明確なエラーで停止する。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

START_MARKER = "<!-- ARTICLE_LIST_START -->"
END_MARKER = "<!-- ARTICLE_LIST_END -->"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
DESCRIPTION_RE = re.compile(r'<meta name="description" content="(.*?)">', re.DOTALL)


def extract_meta(article_html: str, filename: str) -> tuple[str, str]:
    title_match = TITLE_RE.search(article_html)
    description_match = DESCRIPTION_RE.search(article_html)
    if not title_match or not description_match:
        raise ValueError(f'{filename}: <title>または<meta name="description">が見つかりません')
    return title_match.group(1), description_match.group(1)


def build_card(filename: str, title: str, description: str) -> str:
    return (
        f'<a class="article-card" href="articles/{filename}">\n'
        f"<h2>{title}</h2>\n"
        f"<p>{description}</p>\n"
        f"</a>\n"
    )


def update_index(index_path: Path, articles_dir: Path) -> list[str]:
    index_html = index_path.read_text(encoding="utf-8")
    if START_MARKER not in index_html or END_MARKER not in index_html:
        raise ValueError(f"{index_path}にマーカー({START_MARKER} / {END_MARKER})が見つかりません")

    before, rest = index_html.split(START_MARKER, 1)
    existing_block, after = rest.split(END_MARKER, 1)
    linked = set(re.findall(r'href="articles/([^"]+)"', existing_block))

    article_files = sorted(p.name for p in articles_dir.glob("*.html"))
    new_files = [name for name in article_files if name not in linked]
    if not new_files:
        return []

    cards = "".join(
        build_card(name, *extract_meta((articles_dir / name).read_text(encoding="utf-8"), name))
        for name in new_files
    )
    updated_block = existing_block.rstrip("\n") + "\n" + cards
    index_path.write_text(before + START_MARKER + "\n" + updated_block + END_MARKER + after, encoding="utf-8")
    return new_files


def main() -> int:
    parser = argparse.ArgumentParser(description="site/index.htmlの記事一覧を更新")
    parser.add_argument("--index", type=Path, default=Path("site/index.html"))
    parser.add_argument("--articles-dir", type=Path, default=Path("site/articles"))
    args = parser.parse_args()
    try:
        new_files = update_index(args.index, args.articles_dir)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for name in new_files:
        print(f"added: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
