# TRAVEL_AFFILIATE(「旅と、じぶん。」一人旅系アフィリエイト)

一人旅系の日本語アフィリエイトサイト。[[GOLF_AFFILIATE]](../GOLF_AFFILIATE/) の国内版という位置づけ。

## 構成

- `site/` — 公開サイト本体(`index.html` / `style.css` / `articles/` / `robots.txt`)。Vercelのルートディレクトリはここ。
- `automation/` — AFB案件から記事を自動生成し、生成から公開まで完全自動で行うパイプライン。GOLF_AFFILIATEと違い下書き止まりではなく、GitHub Actions(`.github/workflows/afb-publish.yml`)が15分おきに実行し、生成後そのまま`site/articles/`へ書き込み・`site/index.html`更新・git commit・pushまで行う。**このディレクトリで作業するときは`automation/CLAUDE.md`の禁止事項を必ず守ること。**
- `企画/`・`記事/` — 公開前の企画・下書き置き場。

## 姉妹プロジェクト

訪日ゴルフ旅行者向け英語版が[[GOLF_AFFILIATE]](../GOLF_AFFILIATE/)にある。サイト構造(`site/`)は同じだが、自動化の性質が異なる: GOLF_AFFILIATEは下書き止まり(人間が確認してから手動でsite/へ反映)、TRAVEL_AFFILIATEは完全自動公開(人間の承認は`campaigns.csv`の`approved=true`設定の時点で完了している)。
