# %%
import os
from datetime import datetime, timedelta

from pathlib import Path
import pandas as pd
import requests


def fetch_daily_quotes(code, from_date, to_date, id_token):
    """
    指定された銘柄の日次株価データを取得する関数
    
    Args:
        code (str): 証券コード
        from_date (str): 開始日（YYYY-MM-DD形式）
        to_date (str): 終了日（YYYY-MM-DD形式）
        id_token (str): IDトークン
    
    Returns:
        pd.DataFrame: 日次株価データ
    """
    quotes_url = f"https://api.jquants.com/v1/prices/daily_quotes"
    headers = {"Authorization": f"Bearer {id_token}"}
    
    # 日付範囲を1年ずつに分割して取得
    current_from = from_date
    all_data = []
    
    while current_from < to_date:
        current_to = min(
            (datetime.strptime(current_from, "%Y-%m-%d") + timedelta(days=365)).strftime("%Y-%m-%d"),
            to_date
        )
        
        params = {
            "code": code,
            "from": current_from,
            "to": current_to
        }
        
        response = requests.get(quotes_url, headers=headers, params=params)
        data = response.json()
        
        if "daily_quotes" in data:
            all_data.extend(data["daily_quotes"])
        
        current_from = current_to
    
    return pd.DataFrame(all_data)


def load_listed_companies():
    """
    上場企業データを読み込んで分析用のデータフレームを作成する関数
    
    Returns:
        pd.DataFrame: 上場企業データのデータフレーム
    """

    # データファイルのパス
    raw_data_dir = Path(__file__).parent.parent.parent / 'data' / 'raw'
    listed_companies_file_path = raw_data_dir / 'listed_companies.csv'
    
    # CSVファイルを読み込む
    df = pd.read_csv(
        listed_companies_file_path,
        dtype={'Code': str},
        parse_dates=['Date'],
    )
    
    return df


def fetch_stock_prices():
    df = load_listed_companies()
    df_prime_bank = df[
        (df["MarketCodeName"]=="プライム")
        & (df["Sector17CodeName"]=="銀行")
    ]

    # 環境変数からIDトークンを取得
    id_token = os.getenv('JQUANTS_ID_TOKEN')
    if not id_token:
        raise ValueError("環境変数 JQUANTS_ID_TOKEN が設定されていません。")

    # 株価データの取得期間を設定（過去1年）
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=(365*3))).strftime("%Y-%m-%d")

    # 各企業の株価データを取得
    all_stock_prices = []
    print(id_token, to_date, from_date)

    for _, row in df_prime_bank.iterrows():
        code = row["Code"]
        company_name = row["CompanyName"]
        print(f"Fetching data for {company_name} ({code})...")

        try:
            stock_prices = fetch_daily_quotes(code, from_date, to_date, id_token)
            stock_prices["CompanyName"] = company_name
            all_stock_prices.append(stock_prices)
        except Exception as e:
            print(f"Error fetching data for {code}: {e}")

    # データを結合
    if all_stock_prices:
        combined_data = pd.concat(all_stock_prices, ignore_index=True)

        # データを保存
        output_dir = Path(__file__).parent.parent.parent / 'data' / 'processed'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / 'stock_prices_prime_bank.csv'
        combined_data.to_csv(output_file, index=False)
        print(f"\nデータを保存しました: {output_file}")
    else:
        print("データの取得に失敗しました。")


if __name__ == "__main__":
    fetch_stock_prices()
# %%
