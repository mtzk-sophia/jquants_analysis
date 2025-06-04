# %%
from datetime import datetime, timedelta

import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from analysis.processer import process_stock_data


def load_stock_prices():
    """
    株価データを読み込む関数
    
    Returns:
        pd.DataFrame: 株価データ
    """
    file_path = Path(__file__).parent.parent / 'data' / 'processed' / 'stock_prices_prime_bank.csv'
    df = pd.read_csv(
        file_path,
        dtype={'Code': str,},
        parse_dates=['Date'],
    )
    return df


def get_recent_cross_companies(df: pd.DataFrame, days: int = 5, cross_type: str = 'both') -> pd.DataFrame:
    """
    直近の指定日数でMACDのクロスが発生した企業を取得
    
    Args:
        df (pd.DataFrame): 株価データ
        days (int): 直近何日分を確認するか（デフォルト: 5）
        cross_type (str): クロスの種類（'golden', 'dead', 'both'）
    
    Returns:
        pd.DataFrame: クロスが発生した企業の情報
    """
    # 日付を文字列からdatetimeに変換
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 直近の日付を取得
    latest_date = df['Date'].max()
    start_date = latest_date - timedelta(days=days)
    
    # 直近の期間でクロスが発生した企業を抽出
    recent_data = df[df['Date'] >= start_date]
    
    # クロスの種類に応じて条件を設定
    if cross_type == 'golden':
        cross_condition = recent_data['MACD_golden_cross'] == True
    elif cross_type == 'dead':
        cross_condition = recent_data['MACD_dead_cross'] == True
    else:  # 'both'
        cross_condition = (recent_data['MACD_golden_cross'] == True) | (recent_data['MACD_dead_cross'] == True)
    
    cross_companies = recent_data[cross_condition][['Code', 'CompanyName']].drop_duplicates()
    
    return cross_companies


def plot_stock_info_streamlit(df, code, company_name, title: str = "株価チャート"):
    """
    Streamlit用にローソク足チャートとテクニカル指標をPlotlyでプロットする
    
    Args:
        df (pd.DataFrame): 株価データ
        title (str): グラフのタイトル
    """
    stock_data = df[df['Code'] == code].copy()
    stock_data = stock_data.loc[stock_data['Date']>='2025-01-01']


    # 土日祝日を除外
    # df = remove_holidays(df)
    
    # 日付を文字列に変換
    stock_data["Date"] = stock_data["Date"].dt.strftime('%Y-%m-%d')
    
    # MACDのゴールデンクロスを検出
    golden_cross_dates = stock_data.loc[stock_data['MACD_golden_cross']==True, 'Date']
    golden_cross_values = stock_data.loc[stock_data['MACD_golden_cross']==True, 'MACD']
    
    # MACDのデッドクロスを検出
    dead_cross_dates = stock_data.loc[stock_data['MACD_dead_cross']==True, 'Date']
    dead_cross_values = stock_data.loc[stock_data['MACD_dead_cross']==True, 'MACD']
    
    # サブプロットの作成
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25],
        subplot_titles=(title, 'MACD')
    )

    # ローソク足チャート
    fig.add_trace(
        go.Candlestick(
            x=stock_data["Date"],
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close'],
            increasing_line_color='red',
            decreasing_line_color='lime',
            name='ローソク足',
        ),
        row=1, col=1
    )

    # 移動平均線
    fig.add_trace(
        go.Scatter(
            x=stock_data["Date"],
            y=stock_data['SMA5'],
            name='SMA5',
            line=dict(color='blue'),
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=stock_data["Date"],
            y=stock_data['SMA25'],
            name='SMA25',
            line=dict(color='green'),
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=stock_data["Date"],
            y=stock_data['SMA75'],
            name='SMA75',
            line=dict(color='red'),
        ),
        row=1, col=1
    )

    # ボリンジャーバンド
    fig.add_trace(
        go.Scatter(
            x=stock_data['Date'],
            y=stock_data['BB_upper'],
            name='BB Upper',
            line=dict(color='aqua'),
            opacity=0.7,
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=stock_data['Date'],
            y=stock_data['BB_lower'],
            name='BB Lower',
            line=dict(color='aqua'),
            opacity=0.7,
        ),
        row=1, col=1
    )

    # MACD
    fig.add_trace(
        go.Scatter(
            x=stock_data['Date'],
            y=stock_data['MACD'],
            name='MACD',
            line=dict(color='blue'),
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=stock_data['Date'],
            y=stock_data['MACD_signal'],
            name='Signal',
            line=dict(color='red'),
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            x=stock_data['Date'],
            y=stock_data['MACD_histogram'],
            name='Histogram',
            marker_color='gray',
            textposition='none'  # 棒グラフ内の数値を非表示
        ),
        row=2, col=1
    )

    # ゴールデンクロスのマーカーを追加
    fig.add_trace(
        go.Scatter(
            x=golden_cross_dates,
            y=golden_cross_values,
            mode='markers',
            name='ゴールデンクロス',
            marker=dict(
                symbol='triangle-up',
                size=12,
                color='gold',
                line=dict(color='black', width=1)
            ),
        ),
        row=2, col=1
    )
    # デッドクロスのマーカーを追加
    fig.add_trace(
        go.Scatter(
            x=dead_cross_dates,
            y=dead_cross_values,
            mode='markers',
            name='デッドクロス',
            marker=dict(
                symbol='triangle-down',
                size=12,
                color='lightgreen',
                line=dict(color='black', width=1)
            ),
        ),
        row=2, col=1
    )

    # レイアウトの設定
    fig.update_layout(
        height=750,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        # 日付表示の設定
        # xaxis=dict(
        #     type='category',
        #     tickangle=45,
        #     tickmode='auto',
        #     nticks=10,
        #     showgrid=True,
        #     gridcolor='lightgray',
        #     rangeslider=dict(visible=False)
        # ),
        # マージンの調整
        margin=dict(l=0, r=0, t=50, b=0),
        # ホバー設定
        hovermode='x unified'
    )

    # Streamlitで表示（コンテナ幅いっぱいに表示）
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})


def main():
    # ページの設定
    st.set_page_config(
        page_title="株価チャート分析アプリ",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title('株価チャート分析アプリ')
    
    df = load_stock_prices()
    df_with_indicators = process_stock_data(df)
    
    # クロスの種類を選択
    cross_type = st.radio(
        "クロスの種類を選択してください",
        options=['both', 'golden', 'dead'],
        format_func=lambda x: {
            'both': '両方',
            'golden': 'ゴールデンクロスのみ',
            'dead': 'デッドクロスのみ'
        }[x],
        horizontal=True
    )
    
    # 直近5営業日でクロスが発生した企業を取得
    cross_companies = get_recent_cross_companies(df_with_indicators, cross_type=cross_type)
    
    if len(cross_companies) == 0:
        st.warning(f"直近5営業日で{'ゴールデン' if cross_type == 'golden' else 'デッド' if cross_type == 'dead' else 'MACDの'}クロスが発生した企業はありません。")
        return
    
    # 企業選択
    company_options = [f"{row['CompanyName']} ({row['Code']})" for _, row in cross_companies.iterrows()]
    selected_company = st.selectbox("企業を選択してください", company_options)
    
    # 選択された企業のコードを取得
    selected_code = selected_company.split('(')[-1].strip(')')
    selected_name = selected_company.split('(')[0].strip()

    plot_stock_info_streamlit(df_with_indicators, selected_code, selected_name)


if __name__ == "__main__":
    main()

# %%
