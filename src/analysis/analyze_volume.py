import pandas as pd
from pathlib import Path

data_dir = Path(__file__).parent.parent.parent / 'data'


def load_stock_prices_analyzed():
    """
    株価データを読み込む関数
    
    Returns:
        pd.DataFrame: 株価データ
    """
    file_name = 'stock_prices_2025q1.csv'
    file_path = data_dir / 'raw' / file_name
    df = pd.read_csv(
        file_path,
        dtype={'Code': str,},
        parse_dates=['Date'],
    )
    return df


def analyze_volume():
    df = load_stock_prices_analyzed()

    # 企業ごとの出来高を計算
    turnover_by_company = df.groupby([
        'Code',
        'CompanyName',
    ])[['Volume', 'TurnoverValue']].sum()

    # 取引金額でソート（降順）
    turnover_by_company_sorted = turnover_by_company.sort_values(
        by='TurnoverValue',
        ascending=False,
    )
    turnover_by_company_sorted

    # 結果を表示
    print("\n企業ごとの取引金額（上位20社）:")
    print(turnover_by_company_sorted.head(20))

    # 結果をCSVファイルとして保存
    turnover_by_company_sorted.head(500).to_csv(
        data_dir / 'processed' / 'turnover_top500_companies.csv'
    )


if __name__ == '__main__':
    analyze_volume()

