# %%
from get_refresh_token import get_refresh_token
from get_id_token import get_id_token


def get_all_tokens():
    """
    リフレッシュトークンとIDトークンを順番に取得する
    """
    # リフレッシュトークンの取得
    refresh_token = get_refresh_token()
    if not refresh_token:
        print("リフレッシュトークンの取得に失敗したため、処理を中止します。")
        return False
    
    # IDトークンの取得
    id_token = get_id_token()
    if not id_token:
        print("IDトークンの取得に失敗したため、処理を中止します。")
        return False
    
    print("トークンの取得が完了しました。")
    return True


if __name__ == "__main__":
    get_all_tokens() 
# %%
