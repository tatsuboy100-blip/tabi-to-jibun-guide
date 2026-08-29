import tempfile
import unittest
from pathlib import Path

from update_index import END_MARKER, START_MARKER, update_index


INDEX_TEMPLATE = """<!doctype html>
<html lang="ja"><body>
<main>
{start}
<a class="article-card" href="articles/existing.html">
<h2>既存記事</h2>
<p>既存の説明文</p>
</a>
{end}
</main>
</body></html>
""".format(start=START_MARKER, end=END_MARKER)

ARTICLE_HTML = (
    "<!doctype html><html><head><title>新しい記事のタイトル</title>"
    '<meta name="description" content="新しい記事の説明文"></head>'
    "<body>本文</body></html>"
)


class UpdateIndexTests(unittest.TestCase):
    def _write_index(self, directory: Path) -> Path:
        index_path = directory / "index.html"
        index_path.write_text(INDEX_TEMPLATE, encoding="utf-8")
        return index_path

    def test_appends_new_article_card_from_title_and_description(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            index_path = self._write_index(directory)
            articles_dir = directory / "articles"
            articles_dir.mkdir()
            (articles_dir / "new.html").write_text(ARTICLE_HTML, encoding="utf-8")

            new_files = update_index(index_path, articles_dir)

            self.assertEqual(new_files, ["new.html"])
            updated = index_path.read_text(encoding="utf-8")
            self.assertIn('href="articles/new.html"', updated)
            self.assertIn("新しい記事のタイトル", updated)
            self.assertIn("新しい記事の説明文", updated)
            self.assertIn('href="articles/existing.html"', updated)

    def test_idempotent_no_duplicate_on_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            index_path = self._write_index(directory)
            articles_dir = directory / "articles"
            articles_dir.mkdir()
            (articles_dir / "new.html").write_text(ARTICLE_HTML, encoding="utf-8")

            update_index(index_path, articles_dir)
            second_run_new_files = update_index(index_path, articles_dir)

            self.assertEqual(second_run_new_files, [])
            updated = index_path.read_text(encoding="utf-8")
            self.assertEqual(updated.count('href="articles/new.html"'), 1)

    def test_no_new_files_leaves_index_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            index_path = self._write_index(directory)
            articles_dir = directory / "articles"
            articles_dir.mkdir()
            before = index_path.read_text(encoding="utf-8")

            new_files = update_index(index_path, articles_dir)

            self.assertEqual(new_files, [])
            self.assertEqual(index_path.read_text(encoding="utf-8"), before)

    def test_missing_marker_raises_without_modifying_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            index_path = directory / "index.html"
            index_path.write_text("<html><body>no markers here</body></html>", encoding="utf-8")
            articles_dir = directory / "articles"
            articles_dir.mkdir()
            (articles_dir / "new.html").write_text(ARTICLE_HTML, encoding="utf-8")
            before = index_path.read_text(encoding="utf-8")

            with self.assertRaises(ValueError):
                update_index(index_path, articles_dir)

            self.assertEqual(index_path.read_text(encoding="utf-8"), before)

    def test_article_missing_title_or_description_raises(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            index_path = self._write_index(directory)
            articles_dir = directory / "articles"
            articles_dir.mkdir()
            (articles_dir / "broken.html").write_text("<html><body>no head tags</body></html>", encoding="utf-8")

            with self.assertRaises(ValueError):
                update_index(index_path, articles_dir)


if __name__ == "__main__":
    unittest.main()
