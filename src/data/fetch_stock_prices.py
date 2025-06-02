import os
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
from process_listed_companies import load_listed_companies
from api.fetch_stock_prices import fetch_daily_quotes

def main():
    # 上場企業データを読み込む
    df = load_listed_companies()
    
    # プライム市場の銀行業の企業を抽出
    df_prime_bank = df[
        (df["MarketCodeName"] == "プライム") &
        (df["Sector17CodeName"] == "銀行")
    ]
    
    # 環境変数からIDトークンを取得
    id_token = os.getenv('JQUANTS_ID_TOKEN')
    if not id_token:
        raise ValueError("環境変数 JQUANTS_ID_TOKEN が設定されていません。")
    
    # 株価データの取得期間を設定（過去1年）
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    # 各企業の株価データを取得
    all_stock_prices = []
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
        output_file = output_dir / 'prime_bank_stock_prices.csv'
        combined_data.to_csv(output_file, index=False)
        print(f"\nデータを保存しました: {output_file}")
    else:
        print("データの取得に失敗しました。")

if __name__ == "__main__":
    main() 