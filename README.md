# J-Quants 株価分析プロジェクト

このプロジェクトは、J-Quants APIを使用して日本株式市場のデータを取得し、可視化・分析を行うためのツールです。

## セットアップ

1. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
```

2. 環境変数の設定:
`.env`ファイルを作成し、以下の情報を設定してください：
```
JQUANTS_API_KEY=your_api_key
JQUANTS_REFRESH_TOKEN=your_refresh_token
```

## プロジェクト構成

- `src/`: メインのソースコード
  - `api/`: J-Quants APIとの通信
  - `data/`: データ処理
  - `visualization/`: 可視化機能
- `notebooks/`: Jupyter Notebookによる分析
- `data/`: 取得したデータの保存

## 使用方法

1. Jupyter Notebookを起動:
```bash
jupyter notebook
```

2. `notebooks/analysis.ipynb`を開いて分析を開始 