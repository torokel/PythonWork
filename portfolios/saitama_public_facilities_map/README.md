<!-- ─── TOP VISUAL ─────────────────────────────────────────────── -->
<p align="center">
  <img src="thumbnail.png" alt="埼玉県公共施設ダッシュボード サムネイル" width="800">
</p>

# 埼玉県公共施設の分布と傾向ダッシュボード

## 🔥 3-Line Pitch

|  |  |
|---|---|
| **目的** | 埼玉県内の公共施設が “どこに・どんな用途で” 集中しているかを可視化し、都市計画・防災・サービス配置の判断材料を提供 |
| **手法** | Python（Pandas / Geopandas）でデータクレンジング → Tableau Cloud でマップ／ヒートマップ＆棒グラフを連動 |
| **見どころ** | 🗺️/🔥 パラメータ切替、動的フィルタ、凡例統一、レスポンシブ埋め込み（`index.html`） |

---

## ✨ Features

| 機能 | 説明 |
|------|------|
| **インタラクティブ切替** | パラメータで「マップ」⇆「ヒートマップ」を瞬時に切替 |
| **動的フィルタ** | 施設区分・カテゴリで多段フィルタ（デフォルトは全選択） |
| **色凡例統一** | マップと棒グラフでカテゴリカラーを共通管理 |
| **軽量埋め込み** | Tableau Cloud Embed をローカル `index.html` に読み込み（GitHub Pages 展開可） |
| **再現可能な前処理** | `cleaning_saitama.ipynb` で <br> - CSV ⇒ UTF-8 変換 <br> - 列名英語化・緯度経度チェック <br> - 出力 `saitama_facilities_clean.csv` |

---

## 🗂️ フォルダ構成
```text
saitama_public_facilities_map/
├─ data/                       # サンプルデータ (raw / clean)
│   ├─ saitama_facilities_raw.csv
│   └─ saitama_facilities_clean.csv
├─ cleaning_saitama.ipynb      # 前処理ノートブック
├─ index.html                  # Tableau ダッシュボード埋め込みページ
├─ thumbnail.png               # README トップ画像
└─ README.md                   # このファイル

## 🚀 クイックスタート

### 1. リポジトリをクローン
```bash
git clone https://github.com/YOUR_USERNAME/saitama_public_facilities_map.git
cd saitama_public_facilities_map
```

### 2. データ確認・加工（任意）
`cleaning_saitama.ipynb` を実行し、
`data/saitama_facilities_clean.csv` を生成

### 3. ダッシュボード確認
`index.html` をブラウザで開き、Tableauダッシュボードを確認
（Tableau Publicで公開したURLが埋め込まれています）

---

📈 技術スタック

Layer	Tech
可視化	Tableau Cloud / Tableau Public
前処理	Python 3.10, Pandas, Geopandas
ホスティング	GitHub Pages (静的 HTML + Embed)

---


## 🗺️ ダッシュボード構成
| セクション | 内容 |
|------------|------|
| 🧭 マップ / ヒートマップ切替 | パラメータで切替可能（🗺️ / 🔥）|
| 📊 施設カテゴリ別件数 | 棒グラフ表示（横向き）|
| 🎯 フィルター | 施設区分・カテゴリで絞り込み |

---

✍️ ライセンス & クレジット
データ：埼玉県オープンデータポータル（公共施設一覧）
地図タイル：©︎ Mapbox, ©︎ OpenStreetMap
ライセンス：MIT