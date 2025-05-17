import os

from pathlib import Path
from dotenv import load_dotenv


def load_env():
    """環境変数を読み込む"""
    load_dotenv()


def get_env_path():
    """環境変数ファイルのパスを取得"""
    return Path(__file__).parent.parent.parent / '.env'


def update_env_file(key: str, value: str):
    """環境変数ファイルを更新する
    
    Args:
        key (str): 更新する環境変数のキー
        value (str): 設定する値
    """
    env_path = get_env_path()
    env_content = env_path.read_text() if env_path.exists() else ""
    
    if f"{key}=" in env_content:
        # 既存の値を更新
        env_content = env_content.replace(
            f"{key}={os.getenv(key, '')}",
            f"{key}={value}"
        )
    else:
        # 新しい値を追加
        env_content += f"\n{key}={value}"
    
    env_path.write_text(env_content)
    print(f"{key}を.envファイルに保存しました。") 