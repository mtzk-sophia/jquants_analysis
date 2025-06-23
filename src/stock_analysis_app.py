import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pathlib import Path
import datetime

# 環境変数の読み込み
load_dotenv()

# Gemini APIの設定
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')
target_sector_size = 'Sector17CodeName'

# ページ設定
st.set_page_config(
    page_title="AI株価分析アプリ",
    page_icon="📈",
    layout="wide"
)

# タイトル
st.title("AI株価分析アプリ 📈")

# データの読み込み
@st.cache_data
def load_data():
    file_path = Path(__file__).parent.parent / 'data' / 'processed' / 'stock_prices_analyzed.csv'
    df = pd.read_csv(
        file_path,
        dtype={
            'Code': object,
        },
        parse_dates=['Date'],
    )
    return df

try:
    df = load_data()
    
    # 業種リストを作成（銘柄数付き）
    sector_counts = df[[target_sector_size, 'Code']].drop_duplicates()[target_sector_size].value_counts()
    sector_options = [f"{sector}（{count}）" for sector, count in sector_counts.items()]
    selected_sector_with_count = st.selectbox('業種を選択してください', sector_options)

    # 選択した業種名を抽出（銘柄数部分を除去）
    selected_sector = selected_sector_with_count.split('（')[0]

    # 選択した業種でフィルタ
    sector_df = df[df[target_sector_size] == selected_sector]

    # 銘柄名とコードのリストを作成（業種で絞ったもの）
    company_options = [f"{row['CompanyName']}（{row['Code']}）" for _, row in sector_df[['CompanyName', 'Code']].drop_duplicates().iterrows()]
    selected_company = st.selectbox('分析する銘柄を選択してください', company_options)

    # 選択された銘柄コードを抽出
    selected_code = selected_company.split('（')[-1].replace('）', '')
    stock_data = df[df['Code'] == selected_code]
    
    # デバッグ情報を表示
    st.write(f"選択した銘柄の総データ数: {len(stock_data)}")
    
    if len(stock_data) == 0:
        st.error(f"銘柄コード {selected_code} のデータが見つかりません。")
        st.stop()

    # 直近3ヶ月分を抽出
    latest_date = stock_data['Date'].max()
    three_months_ago = latest_date - pd.DateOffset(months=3)
    recent_data = stock_data[stock_data['Date'] >= three_months_ago]
    
    # デバッグ情報を表示
    st.write(f"直近3ヶ月分のデータ数: {len(recent_data)}")
    
    if len(recent_data) == 0:
        st.error(f"銘柄コード {selected_code} の直近3ヶ月分のデータが見つかりません。")
        st.stop()

    # 必要なカラムだけ抽出
    columns = ['Date', 'Open', 'Close', 'Volume', 'SMA25', 'SMA75']
    recent_data = recent_data[columns]

    # 日付を「YYYY-MM-DD」形式に変換
    recent_data['Date'] = recent_data['Date'].dt.strftime('%Y-%m-%d')

    # テーブルを文字列化（markdown形式）
    table_str = recent_data.to_markdown(index=False)

    # 基本情報の表示
    st.subheader("基本情報")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("現在値", f"¥{stock_data['Close'].iloc[-1]:,.0f}")
    with col2:
        price_change = ((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]) / stock_data['Close'].iloc[-2]) * 100
        st.metric("前日比", f"{price_change:.2f}%")
    with col3:
        st.metric("出来高", f"{stock_data['Volume'].iloc[-1]:,.0f}")
    
    # Geminiによる分析
    st.subheader("AI分析")
    
    # 分析用のプロンプトを作成
    prompt = f"""
    以下は銘柄コード: {selected_code} の直近3ヶ月分の株価データです。

    {table_str}

    このデータをもとに、投資判断のアドバイスをお願いします。
    1. 直近の株価トレンド
    2. 出来高の推移
    3. 移動平均線の観点
    4. 投資判断のアドバイス
    5. 注意点

    分析は簡潔に、箇条書きでお願いします。
    """

    st.write(len(prompt))
    
    if st.button("分析を実行"):
        with st.spinner("AIが分析中..."):
            response = model.generate_content(prompt)
            st.write(response.text)
    
    # グラフ表示
    st.subheader("株価推移")
    st.line_chart(stock_data.set_index('Date')['Close'])
    
    # 出来高の推移
    st.subheader("出来高推移")
    st.bar_chart(stock_data.set_index('Date')['Volume'])

    # 分析用のプロンプトを表示
    st.subheader("分析用のプロンプト")
    st.write(prompt)

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
    st.info("データの読み込みに失敗しました。ファイルパスとデータ形式を確認してください。") 