import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリを取得
project_root = Path(__file__).parent.parent

# 必要なモジュールのパスを追加
sys.path.append(str(project_root))

# 各モジュールをインポート
from src.api.get_tokens import get_all_tokens
from src.api.fetch_stock_prices import fetch_stock_prices
from src.analysis.processer import process_stock_data
import pandas as pd


def main():
    print("1. トークンの取得を開始します...")
    if not get_all_tokens():
        print("トークンの取得に失敗しました。処理を中止します。")
        return

    print("\n2. 株価データの取得を開始します...")
    fetch_stock_prices()

    print("\n3. 株価データの分析を開始します...")
    # 処理済みデータの読み込み
    processed_data_path = project_root / 'data' / 'raw' / 'stock_prices.csv'
    if not processed_data_path.exists():
        print("株価データが見つかりません。処理を中止します。")
        return

    df = pd.read_csv(processed_data_path)
    processed_df = process_stock_data(df)

    # 分析結果の保存
    output_path = project_root / 'data' / 'processed' / 'stock_prices_analyzed.csv'
    processed_df.to_csv(output_path, index=False)
    print(f"分析結果を保存しました: {output_path}")


if __name__ == "__main__":
    main() 