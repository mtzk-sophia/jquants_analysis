from datetime import datetime, timedelta
import json
import os
import requests

from .token_utils import load_env, update_env_file


def get_refresh_token():
    # 環境変数を読み込む
    load_env()
    
    # 認証情報を取得
    data = {
        "mailaddress": os.getenv("JQUANTS_EMAIL"),
        "password": os.getenv("JQUANTS_PASSWORD")
    }
    
    # リフレッシュトークンを取得
    r_post = requests.post(
        "https://api.jquants.com/v1/token/auth_user",
        data=json.dumps(data)
    )
    refresh_token = r_post.json().get("refreshToken")
    
    if refresh_token:
        update_env_file("JQUANTS_REFRESH_TOKEN", refresh_token)
        return refresh_token
    else:
        print("リフレッシュトークンの取得に失敗しました。")
        return None


if __name__ == "__main__":
    get_refresh_token()
