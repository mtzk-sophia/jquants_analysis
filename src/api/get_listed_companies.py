# %%
import json
import os
import requests
import sys

import pandas as pd
from pathlib import Path

from token_utils import load_env


def get_listed_companies():
    """上場銘柄一覧を取得する
    
    Returns:
        list: 上場銘柄一覧のリスト
    """
    # 環境変数を読み込む
    load_env()
    
    # IDトークンを取得
    id_token = os.getenv("JQUANTS_ID_TOKEN")
    if not id_token:
        print("IDトークンが設定されていません。")
        return None
    
    # 上場銘柄一覧を取得
    headers = {"Authorization": f"Bearer {id_token}"}
    r_get = requests.get(
        "https://api.jquants.com/v1/listed/info",
        headers=headers
    )
    
    if r_get.status_code == 200:
        companies = r_get.json().get("info", [])
        print(f"{len(companies)}件の上場銘柄を取得しました。")
        return companies
    else:
        print(f"上場銘柄一覧の取得に失敗しました。ステータスコード: {r_get.status_code}")
        return None


def save_to_csv(companies, filename="listed_companies.csv"):
    """上場銘柄一覧をCSVファイルに保存する
    
    Args:
        companies (list): 上場銘柄一覧のリスト
        filename (str): 保存するファイル名
    """
    if not companies:
        print("保存するデータがありません。")
        return
    
    # 保存先ディレクトリのパスを取得
    save_dir = Path(__file__).parent.parent.parent / 'data' / 'raw'
    
    # ディレクトリが存在しない場合は作成
    # ensure_dir_exists(save_dir)
    
    # 保存先のフルパスを作成
    save_path = save_dir / filename
    
    # DataFrameに変換
    df = pd.DataFrame(companies)
    
    # CSVファイルに保存
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"データを{save_path}に保存しました。")


if __name__ == "__main__":
    companies = get_listed_companies()
    df = pd.DataFrame(companies)
    display(df.head(500))
    if companies:
        # 最初の5件を表示
        for company in companies[1000:1100]:
            print(f"銘柄コード: {company.get('Code')}, 銘柄名: {company.get('CompanyName')}")
    
        # CSVファイルに保存
        # save_to_csv(companies) 
# %%
