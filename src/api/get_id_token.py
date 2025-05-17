import json
import os
import requests

from token_utils import load_env, update_env_file


def get_id_token():
    # 環境変数を読み込む
    load_env()
    
    # リフレッシュトークンを取得
    refresh_token = os.getenv("JQUANTS_REFRESH_TOKEN")
    if not refresh_token:
        print("リフレッシュトークンが設定されていません。")
        return None
    
    # IDトークンを取得
    r_post = requests.post(
        f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}"
    )
    id_token = r_post.json().get("idToken")
    
    if id_token:
        update_env_file("JQUANTS_ID_TOKEN", id_token)
        return id_token
    else:
        print("IDトークンの取得に失敗しました。")
        return None


if __name__ == "__main__":
    get_id_token()
